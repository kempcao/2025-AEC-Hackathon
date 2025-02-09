import json
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
import re
import os

def compute_spaces_convex_hull_ratio(data):
    """
    Given a JSON dictionary 'data' that contains 'spaces' with their coordinates and room types,
    compute the ratio of the sum of areas of [bathroom, corridor, bedroom, kitchen]
    to the total area of their convex hull.
    """

    # Room types we care about
    #relevant_room_types = {"bathroom", "corridor", "kitchen"}
    relevant_room_types = {"bathroom","corridor", "kitchen"}

    polygons = []
    total_area = 0.0


    # Loop through the 'spaces' entry in the JSON
    for space_id, space_info in data.get("spaces", {}).items():
        room_type = space_info.get("room_type", "").lower()
        
        # Only process if it's one of the desired room types
        if room_type in relevant_room_types:
            coords = space_info.get("coordinates", [])
            
            # Convert list of {x, y, z} to a list of (x, y) tuples
            polygon_coords = [(c["x"], c["y"]) for c in coords]
            
            # Create the polygon (Shapely auto-closes it)
            poly = Polygon(polygon_coords)

            # Add to list of polygons
            polygons.append(poly)
            
            # Accumulate its area
            total_area += poly.area

    # If we have no polygons, avoid errors
    if not polygons:
        return 0.0

    # Combine polygons into a single MultiPolygon and get its convex hull
    multi_poly = MultiPolygon(polygons)
    hull = multi_poly.convex_hull

    hull_area = hull.area
    
    # Compute the ratio, guarding against division by zero
    if hull_area == 0:
        return 0.0
    else:
        return total_area / hull_area, hull_area

def load_jsons_and_compute_ratios(base_json_folder):
    """
    1) Finds subfolders that start with "GenericDesign_".
    2) Within each, finds files that match the pattern "number.json".
    3) Loads each file, computes the ratio via compute_spaces_convex_hull_ratio, and returns results.
    """

    # Regex to match files named as "<number>.json" (e.g., "1.json", "12009.json")
    json_filename_pattern = re.compile(r'^\d+\.json$')

    results = {}  # Will hold { folder_name: { file_name: ratio } }

    # 1) Iterate over subfolders in the base folder
    for folder_name in os.listdir(base_json_folder):
        if folder_name.startswith("GenericDesign_"):
            folder_path = os.path.join(base_json_folder, folder_name)
            
            if not os.path.isdir(folder_path):
                continue  # Skip if it's not a directory

            # 2) Within that folder, find all matching JSON files
            for file_name in os.listdir(folder_path):
                if json_filename_pattern.match(file_name):
                    file_path = os.path.join(folder_path, file_name)
                    
                    # Load the JSON
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    except (json.JSONDecodeError, OSError) as e:
                        print(f"Error loading {file_path}: {e}")
                        continue

                    # 3) Compute the ratio
                    ratio, hull_area = compute_spaces_convex_hull_ratio(data)

                    maximum_area = 3.2 * 14.

                    if hull_area > maximum_area:
                        weight = maximum_area / hull_area
                    else:
                        weight = 1.

                    # Store the ratio in our results
                    results.setdefault(folder_name, {})[file_name] = ratio * weight
                    results.setdefault(folder_name, {})["area"] = hull_area

    return results


if __name__ == "__main__":


    json_folder_path = "/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/hackathon/2025-AEC-Hackathon/json"

    # Get a list of all items in the directory and filter by folders
    results = load_jsons_and_compute_ratios(json_folder_path)

    print(results)


    with open('/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/hackathon/2025-AEC-Hackathon/json/GenericDesign_12009/12009.json', 'r') as file:
        data = json.load(file) 

    iou = compute_spaces_convex_hull_ratio(data)


    print(iou)
    