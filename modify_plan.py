import numpy as np
from shapely.geometry import Polygon, box
from shapely import affinity
from typing import Dict, List, Any
import matplotlib.pyplot as plt
from descartes import PolygonPatch
import json
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union


def compute_spaces_convex_hull_ratio(data, buffer_distance=0.001):
    """
    Compute the ratio of total relevant room areas to their convex hull area.
    Enhanced with geometry validation and error handling.
    """
    relevant_room_types = {"bathroom", "corridor", "kitchen", "bedroom"}
    
    valid_polygons = []
    total_area = 0.0

    for space_id, space_info in data.get("spaces", {}).items():
        try:
            room_type = space_info.get("room_type", "").lower()
            if room_type not in relevant_room_types:
                continue

            coords = space_info.get("coordinates", [])
            if len(coords) < 3:
                print(f"Skipping {room_type} {space_id} - not enough points")
                continue

            # Create and validate polygon
            poly_coords = [(c["x"], c["y"]) for c in coords]
            poly = Polygon(poly_coords).buffer(buffer_distance)
            
            if not poly.is_valid or poly.is_empty:
                print(f"Skipping invalid {room_type} {space_id}")
                continue
                
            valid_polygons.append(poly)
            total_area += poly.area

        except Exception as e:
            print(f"Error processing {space_id}: {str(e)}")
            continue

    if not valid_polygons:
        return 0.0

    try:
        # Create unified geometry
        combined = unary_union(valid_polygons)
        hull = combined.convex_hull
        
        if hull.is_empty:
            return 0.0
            
        hull_area = hull.area
        return total_area / hull_area if hull_area > 0 else 0.0

    except Exception as e:
        print(f"Convex hull calculation failed: {str(e)}")
        return 0.0

class PrefabPart:
    def __init__(self, part_type: str, geometry: Polygon, max_area: float):
        self.type = part_type
        self.geometry = geometry
        self.max_area = max_area


class CorridorPrefab(PrefabPart):
    def __init__(self, geometry: Polygon, max_area: float, 
                 max_length: float, max_width: float):
        super().__init__("corridor", geometry, max_area)
        self.max_length = max_length
        self.max_width = max_width

class Room:
    def __init__(self, room_id: str, data: Dict[str, Any]):
        self.id = room_id
        self.type = data['room_type']
        self.apartment = data['apartment']
        self.geometry = self._create_geometry(data['coordinates'])
        
    def _create_geometry(self, coordinates: List[Dict]) -> Polygon:
        # Convert JSON coordinates to Shapely Polygon
        points = [(float(pt['x']), float(pt['y'])) for pt in coordinates]
        return Polygon(points).buffer(0)  # Clean geometry

class Apartment:
    def __init__(self, name: str, rooms: List[Room]):
        self.name = name
        self.rooms = rooms
        
    @property
    def floorplan(self) -> Dict[str, List[Polygon]]:
        """Dynamic floorplan updated with latest geometries"""
        plan = {}
        for room in self.rooms:
            plan.setdefault(room.type, []).append(room.geometry)
        return plan
        
    def refresh_floorplan(self):
        """Force update of spatial relationships"""
        # Add any necessary post-processing here
        pass

# Sample data structures
class PrefabPart:
    def __init__(self, part_type: str, geometry: Polygon, max_area: float):
        self.type = part_type
        self.geometry = geometry
        self.max_area = max_area
class PrefabOptimizer:
    def __init__(self, prefabs: List[PrefabPart]):
        self.prefabs = {p.type: p for p in prefabs}
        self.relevant_types = set(self.prefabs.keys())
        self.placement_strategies = {
            'corridor': self._fit_corridor,
            'default': self._fit_standard_room
        }

     def _calculate_hull_ratio(self, apartment: Apartment) -> float:
        """Calculate convex hull ratio for relevant rooms in apartment"""
        relevant_rooms = [r for r in apartment.rooms 
                        if r.type in self.relevant_types]
        
        valid_polys = []
        total_area = 0.0
        
        for room in relevant_rooms:
            if room.geometry.is_valid and not room.geometry.is_empty:
                valid_polys.append(room.geometry)
                total_area += room.geometry.area
                
        if not valid_polys or total_area == 0:
            return 0.0
            
        try:
            combined = unary_union(valid_polys)
            hull = combined.convex_hull
            return total_area / hull.area if hull.area > 0 else 0.0
        except:
            return 0.0
    def optimize(self, apartments: List[Apartment], 
                hull_ratio_threshold: float = 0.65,
                iou_threshold: float = 0.6):
        """Optimize apartments meeting convex hull efficiency threshold"""
        for apartment in apartments:
            print(f"\n{'='*40}")
            print(f"Processing {apartment.name}")
            
            ratio = self._calculate_hull_ratio(apartment)
            print(f"Space Efficiency Ratio: {ratio:.2f}")
            
            if ratio < hull_ratio_threshold:
                print(f"Skipping - below threshold {hull_ratio_threshold}")
                continue
                
            self._optimize_apartment(apartment, iou_threshold)

    def _optimize_apartment(self, apartment: Apartment, iou_threshold: float):
        """Coordinate optimization for all relevant room types"""
        for room_type, prefab in self.prefabs.items():
            self._process_room_type(apartment, room_type, prefab, iou_threshold)

    def _process_room_type(self, apartment: Apartment, room_type: str, 
                         prefab: PrefabPart, threshold: float):
        """Handle optimization for specific room type"""
        target_rooms = [r for r in apartment.rooms if r.type == room_type]
        if not target_rooms:
            return

        print(f"\nProcessing {len(target_rooms)} {room_type}(s)")
        scores = self._calculate_iou_scores(target_rooms, prefab)
        
        for score, room in sorted(scores, reverse=True, key=lambda x: x[0]):
            if score < threshold:
                continue
                
            print(f"  Room {room.id} IoU: {score:.2f}")
            if self._try_fit_prefab(room, prefab):
                print("    Prefab fitted successfully")
                apartment.refresh_floorplan()

    def _try_fit_prefab(self, room: Room, prefab: PrefabPart) -> bool:
        """Attempt multiple fitting strategies"""
        strategy = self.placement_strategies.get(prefab.type, 
                     self.placement_strategies['default'])
        return strategy(room, prefab)

    def _fit_standard_room(self, room: Room, prefab: PrefabPart) -> bool:
        """Standard fitting process for most room types"""
        original = room.geometry
        strategies = [
            lambda: prefab.geometry,
            lambda: self._scaled_prefab(original, prefab),
            lambda: self._aligned_prefab(original, prefab.geometry)
        ]
        
        for strategy in strategies:
            candidate = strategy()
            if original.contains(candidate):
                room.geometry = candidate
                return True
        return False

    def _fit_corridor(self, room: Room, prefab: PrefabPart) -> bool:
        """Special handling for corridor prefabs"""
        aligned = self._align_to_axis(room.geometry, prefab.geometry)
        scaled = self._scale_corridor(room.geometry, aligned)
        
        if room.geometry.contains(scaled):
            room.geometry = scaled
            return True
        return False

    def _scaled_prefab(self, room_poly: Polygon, prefab: PrefabPart) -> Polygon:
        """Create safely scaled prefab"""
        scale = min(
            np.sqrt(room_poly.area / prefab.geometry.area),
            np.sqrt(prefab.max_area / prefab.geometry.area)
        )
        return affinity.scale(prefab.geometry, scale, scale, origin='centroid')

    def _aligned_prefab(self, room_poly: Polygon, prefab_poly: Polygon) -> Polygon:
        """Align prefab to room orientation"""
        room_angle = self._orientation_angle(room_poly)
        prefab_angle = self._orientation_angle(prefab_poly)
        rotated = affinity.rotate(prefab_poly, room_angle - prefab_angle, 
                                origin='centroid')
        return affinity.translate(rotated, 
                                *self._centroid_offset(rotated, room_poly))

    def _orientation_angle(self, geom: Polygon) -> float:
        """Calculate main orientation angle"""
        mrr = geom.minimum_rotated_rectangle
        coords = list(mrr.exterior.coords)
        dx = coords[1][0] - coords[0][0]
        dy = coords[1][1] - coords[0][1]
        return np.degrees(np.arctan2(dy, dx))

    def _centroid_offset(self, source: Polygon, target: Polygon) -> tuple:
        """Calculate centroid alignment offset"""
        return (target.centroid.x - source.centroid.x,
                target.centroid.y - source.centroid.y)

    def _calculate_hull_ratio(self, apartment: Apartment) -> float:
        """Calculate space efficiency metric"""
        relevant_geoms = [r.geometry for r in apartment.rooms 
                        if r.type in self.relevant_types
                        and r.geometry.is_valid]
        
        if not relevant_geoms:
            return 0.0
            
        try:
            union = unary_union(relevant_geoms)
            hull = union.convex_hull
            return union.area / hull.area if hull.area > 0 else 0.0
        except:
            return 0.0

    def load_from_json(self, json_path: str) -> List[Apartment]:
        """Load and validate apartment data from JSON"""
        with open(json_path) as f:
            data = json.load(f)
            
        apartments = {}
        for room_id, room_data in data.get('spaces', {}).items():
            if self._valid_room(room_data):
                self._add_to_apartments(apartments, room_id, room_data)
                
        return [Apartment(name, rooms) for name, rooms in apartments.items()]

    def _valid_room(self, data: dict) -> bool:
        """Validate room data requirements"""
        return (data.get('apartment') not in [None, 'UNASSIGNED'] 
                and len(data.get('coordinates', [])) >= 3)

    def _add_to_apartments(self, apartments: dict, room_id: str, data: dict):
        """Organize rooms into apartment groups"""
        apt_name = data['apartment']
        if apt_name not in apartments:
            apartments[apt_name] = []
        try:
            apartments[apt_name].append(Room(room_id, data))
        except Exception as e:
            print(f"Invalid room {room_id}: {str(e)}")


def fit_prefabricated(apartments: List[Apartment], prefabs: List[PrefabPart], iou_threshold=0.7):
    # Track used prefab area per type
    used_areas: Dict[str, float] = {p.type: 0.0 for p in prefabs}
    
    # Sort apartments by best IoU scores
    sorted_apts = sorted(apartments, 
                       key=lambda a: max(a.iou_scores.values()), 
                       reverse=True)
    
    for apt in sorted_apts:
        print(f"\nProcessing apartment {apt.id}")
        
        # Sort prefabs by IoU for this apartment
        sorted_prefabs = sorted(prefabs, 
                              key=lambda p: apt.iou_scores.get(p.type, 0), 
                              reverse=True)
        
        for prefab in sorted_prefabs:
            prefab_type = prefab.type
            current_iou = apt.iou_scores.get(prefab_type, 0)
            
            if current_iou < iou_threshold:
                continue
                
            if used_areas[prefab_type] + prefab.geometry.area > prefab.max_area:
                print(f"Max area reached for {prefab_type}")
                continue
                
            # Get target room in floorplan
            target_room = apt.floorplan.get(prefab_type)
            if not target_room:
                continue
                
            # Check if prefab fits without modification
            if target_room.contains(prefab.geometry):
                apply_prefab(apt, prefab, target_room)
                used_areas[prefab_type] += prefab.geometry.area
                continue
                
            # Try to modify floorplan
            print(f"Attempting to fit {prefab_type} in apartment {apt.id}")
            modified = modify_floorplan(apt, prefab, target_room)
            
            if modified:
                used_areas[prefab_type] += prefab.geometry.area
                print("Successfully applied prefab!")
            else:
                print("Failed to fit prefab")

    return apartments

def modify_floorplan(apt: Apartment, prefab: PrefabPart, target_room: Polygon) -> bool:
    # Clean input geometry
    target_room = target_room.buffer(0)
    
    # 1. Try simple scaling
    scale_factor = np.sqrt(prefab.geometry.area / target_room.area)
    scaled_prefab = scale_geometry(prefab.geometry, scale_factor)
    
    if target_room.contains(scaled_prefab):
        apt.floorplan[prefab.type] = scaled_prefab
        return True
        
    # 2. Try axis-aligned adjustment
    prefab_bounds = prefab.geometry.bounds
    room_bounds = target_room.bounds
    
    # Calculate needed expansion/contraction
    dx = (prefab_bounds[2] - prefab_bounds[0]) - (room_bounds[2] - room_bounds[0])
    dy = (prefab_bounds[3] - prefab_bounds[1]) - (room_bounds[3] - room_bounds[1])
    
    # Create modified room (simplified example)
    new_room = box(room_bounds[0], room_bounds[1],
                   room_bounds[0] + dx + (room_bounds[2] - room_bounds[0]),
                   room_bounds[1] + dy + (room_bounds[3] - room_bounds[1]))
    
    new_room = new_room.buffer(0)  # Clean the result
    if not new_room.is_valid or new_room.is_empty:
        return False
   
    # Update floorplan with cleaned geometry
    apt.floorplan[prefab.type] = new_room
    return True

def check_room_fit(apt: Apartment, new_room: Polygon, room_type: str) -> bool:
    # Check for overlaps with other rooms
    for r_type, geometry in apt.floorplan.items():
        if r_type == room_type:
            continue
        if new_room.intersects(geometry):
            return False
    return True

def scale_geometry(geom: Polygon, factor: float) -> Polygon:
    # Simple scaling from centroid
    centroid = geom.centroid
    return affinity.scale(geom, xfact=factor, yfact=factor, origin=centroid)

def apply_prefab(apt: Apartment, prefab: PrefabPart, target_room: Polygon):
    apt.floorplan[prefab.type] = prefab.geometry


def draw_floorplan(apartment: Apartment, title="Floor Plan"):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title(title)
    ax.set_aspect('equal')
    
    colors = {
        'bathroom': '#a6cee3',
        'kitchen': '#fdbf6f',
        'corridor': '#cccccc',
        'living_room': '#b2df8a',
        'bedroom': '#cab2d6',
        'core': '#ff0000'
    }
    
    for room_type, geometries in apartment.floorplan.items():
        for i, geometry in enumerate(geometries):
            # Clean and validate geometry
            if not isinstance(geometry, Polygon):
                print(f"Skipping invalid {room_type} geometry #{i}")
                continue
                
            cleaned_geom = geometry.buffer(0)
            if cleaned_geom.is_empty:
                continue
                
            try:
                x, y = cleaned_geom.exterior.xy
                color = colors.get(room_type, '#888888')
                ax.fill(x, y, fc=color, ec='black', alpha=0.7, label=room_type)
                
                centroid = cleaned_geom.centroid
                ax.text(centroid.x, centroid.y, f"{room_type}\n{geometry.area:.1f}m²", 
                        ha='center', va='center', fontsize=6,
                        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
            except Exception as e:
                print(f"Error drawing {room_type} #{i}: {str(e)}")
                continue
    
    # Rest of the function remains the same...
    # [Keep the legend, bounds calculation, and grid setup from previous version]
    
    plt.show()
# Example usage
if __name__ == "__main__":

    """
    # Sample prefabs
    bathroom_prefab = PrefabPart("bathroom", box(0, 0, 1, 4), max_area=100)
    kitchen_prefab = PrefabPart("kitchen", box(0, 0, 5, 4), max_area=150)
    
    # Sample apartments
    apartment1 = Apartment(
        id=1,
        floorplan={
            "bathroom": box(0, 0, 3.2, 4.1),
            "kitchen": box(0, 0, 7.8, 9.9)
        },
        iou_scores={"bathroom": 0.85, "kitchen": 0.78}
    )
    
    modified_apartments = fit_prefabricated([apartment1], [bathroom_prefab, kitchen_prefab])

    print(modified_apartments)

    print("\nModified floor plan:")
    draw_floorplan(apartment1, "Modified Floor Plan")
    """

    # Load prefabs
    bathroom_prefab = PrefabPart(
        "bathroom", 
        Polygon([(0,0), (0,2), (3,2), (3,0)]),
        max_area=8
    )
    
    kitchen_prefab = PrefabPart(
        "kitchen",
        Polygon([(0,0), (0,3), (4,3), (4,0)]),
        max_area=12
    )

    corridor_prefab = CorridorPrefab(
        geometry=Polygon([(0,0), (0,1.2), (4,1.2), (4,0)]),
        max_area=15,
        max_length=5,
        max_width=1.5
    )

    
    optimizer = PrefabOptimizer([bathroom_prefab, kitchen_prefab, corridor_prefab])
    
    # Load apartments from JSON
    apartments = optimizer.load_from_json("/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/hackathon/2025-AEC-Hackathon/json/GenericDesign_14012/14012.json")
    
    # Run optimization
    optimizer.optimize(apartments,
    hull_ratio_threshold=0.55,  # Only process highly efficient layouts
    iou_threshold=0.75
    )         # Require strong prefab matches)
    
    # Visualize results
    for apartment in apartments:
        draw_floorplan(apartment)