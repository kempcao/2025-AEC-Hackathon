import json
import re
import os
import csv

from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from itertools import combinations


def polygon_from_coords(coords):
    """
    Converts a list of {x, y, z} dicts to a Shapely Polygon (2D).
    Ignores the 'z' coordinate.
    """
    points_2d = [(pt["x"], pt["y"]) for pt in coords]
    return Polygon(points_2d)

def compute_spaces_convex_hull_ratio(data):
    """
    Given a JSON dictionary 'data' that contains 'spaces' with their coordinates and room types,
    compute the ratio of the sum of areas of [bathroom, corridor, bedroom, kitchen]
    to the total area of their convex hull.
    """

    # Room types we care about
    #relevant_room_types = {"bathroom", "corridor", "kitchen"}
    relevant_room_types = {"bathroom","corridor", "kitchen"}
    #Checking the bathroom

    polygons = []
    total_area = 0.0

    individual_areas = []

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

            individual_areas.append({room_type:poly.area})

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
        return total_area / hull_area, hull_area, individual_areas


def compute_space_combinations_ratios(data):
    """
    Given a JSON dictionary 'data' that contains 'spaces' with their coordinates and room types,
    compute the ratio of the sum of areas to the total area of the convex hull
    for each combination of bathroom, corridor, kitchen:

      1) bathroom alone
      2) corridor alone
      3) kitchen alone
      4) bathroom + corridor
      5) bathroom + kitchen
      6) corridor + kitchen
      7) bathroom + corridor + kitchen

    Returns a dict mapping each combo to (ratio, hull_area, total_area).
    """

    # Define the possible room types of interest
    relevant_room_types = {"bathroom", "corridor", "kitchen"}

    # Separate polygons by room type
    polygons_by_type = {
        "bathroom": [],
        "corridor": [],
        "kitchen": []
    }

    rooms_number = 0
    # Loop through the 'spaces' entry in the JSON
    for space_id, space_info in data.get("spaces", {}).items():
        room_type = space_info.get("room_type", "").lower()
        rooms_number += 1
        
        print("Room type = ", room_type)
        # If it's one of the desired room types, parse
        if room_type in relevant_room_types:
            coords = space_info.get("coordinates", [])
            polygon_coords = [(c["x"], c["y"]) for c in coords]
            poly = Polygon(polygon_coords)
            polygons_by_type[room_type].append(poly)

    
    # Only include room types that are present in the JSON.
    active_room_types = [rt for rt in ["bathroom", "corridor", "kitchen"] if polygons_by_type[rt]]
    print(active_room_types)
    if not active_room_types:
        # If none of the room types are present, return an empty dict.
        return {}

    # Generate all subsets (combos) of the 3 room types
    # 1-element combos, 2-element combos, 3-element combos
    combos = []
    for r in range(1, len(active_room_types) + 1):
        combos.extend(combinations(active_room_types, r))
    # Dictionary to store results
    # e.g., results["bathroom,corridor"] = (ratio, hull_area, total_area)
    results = {}

    for combo in combos:
        combo_name = ",".join(sorted(combo))  # e.g. "bathroom,corridor"
        
        # Collect all polygons for these room types
        combo_polygons = []
        for room_t in combo:
            combo_polygons.extend(polygons_by_type[room_t])

        if not combo_polygons:
            # If no polygons found for this combo, ratio is 0
            results[combo_name] = (0.0, 0.0, 0.0)
            continue

        # Combine polygons into a single MultiPolygon
        multi_poly = MultiPolygon(combo_polygons)
        # Sum of areas
        total_area = sum(poly.area for poly in combo_polygons)
        # Compute convex hull
        hull = multi_poly.convex_hull
        hull_area = hull.area

        weight = 1 / ((rooms_number + 1)/2 - len(combo))
        

        if hull_area == 0:
            ratio = 0.0
        else:
            ratio = (total_area / hull_area) * weight

        # Store ratio, hull_area, and total_area
        results[combo_name] = (ratio,  hull_area, total_area)

    return results

def compute_space_combinations_ratios_by_apartment(data, weight_flag = False):
    """
    Given a JSON dictionary 'data' with a "spaces" entry containing each space's
    coordinates, room_type, and apartment name, compute for each apartment the ratio
    of (sum of areas of selected spaces) to (convex hull area of those spaces) for every
    combination of room types among bathroom, corridor, and kitchen.
    
    For a combination that contains only one polygon, the ratio is forced to 1.
    
    Only the room types that are present in an apartment are considered. For example, if an
    apartment does not contain any kitchen, no combination including "kitchen" will be computed.
    
    Returns:
        A dict of the form:
        
        {
          "Apartment 1": {
              "bathroom": (ratio, hull_area, total_area),
              "corridor": (ratio, hull_area, total_area),
              "bathroom,corridor": (ratio, hull_area, total_area),
              ... (other combinations available)
          },
          "Apartment 2": {
              ... similar structure ...
          },
          ...
        }
    """
    # Room types of interest.
    relevant_room_types = {"bathroom", "corridor", "kitchen"}
    
    # Group spaces by apartment.
    apartments = {}
    rooms_number = 0
    for space_id, space_info in data.get("spaces", {}).items():
        room_type = space_info.get("room_type", "").lower()
        rooms_number += 1
        # Only consider relevant room types.
        if room_type not in relevant_room_types:
            continue
        
        apartment = space_info.get("apartment", "Unknown")
        poly = polygon_from_coords(space_info.get("coordinates", []))
        
        # Initialize structure for this apartment if needed.
        if apartment not in apartments:
            apartments[apartment] = {
                "bathroom": [],
                "corridor": [],
                "kitchen": []
            }
        apartments[apartment][room_type].append(poly)
    
    # Now compute ratios for each apartment.
    results = {}
    for apartment, poly_dict in apartments.items():
        # Identify which room types are actually present.
        active_types = [rt for rt in ["bathroom", "corridor", "kitchen"] if poly_dict[rt]]
        if not active_types:
            # No relevant spaces for this apartment.
            continue

        # Prepare a dictionary for this apartment's combinations.
        apt_results = {}
        # Generate all non-empty combinations from the active room types.
        for r in range(1, len(active_types) + 1):
            for combo in combinations(active_types, r):
                # The combo key is a comma-separated list of room types (sorted for consistency).
                combo_key = ",".join(sorted(combo))
                
                # Gather all polygons for the combination.
                combo_polygons = []
                for rt in combo:
                    combo_polygons.extend(poly_dict[rt])
                
                if not combo_polygons:
                    apt_results[combo_key] = (0.0, 0.0, 0.0)
                    continue
                
                # Sum the areas of the individual polygons.
                total_area = sum(poly.area for poly in combo_polygons)
                
                if weight_flag:
                    weight = 1 / ((rooms_number + 1)/2 - len(combo))
                else:
                    weight = 1

                # If only one polygon is in the combo, force the hull area to equal its area.
                if len(combo_polygons) == 1:
                    hull_area = total_area
                else:
                    multi_poly = MultiPolygon(combo_polygons)
                    hull_area = multi_poly.convex_hull.area
                
                ratio = (total_area / hull_area) * weight if hull_area != 0 else 0.0
                
                apt_results[combo_key] = (ratio, rooms_number, hull_area, total_area)
        
        results[apartment] = apt_results
    
    return results

def process_json_file(file_path):
    """
    Opens the JSON file at file_path, computes the apartment-level ratios,
    and returns a list of records (one per combination) as dictionaries.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    apartment_results = compute_space_combinations_ratios_by_apartment(data,weight_flag = False)

    records = []
    for apt, combos in apartment_results.items():
        for combo, (ratio,rooms_number, hull_area, total_area) in combos.items():
            record = {
                # Use only the file name (basename) for the CSV output.
                "file": os.path.basename(file_path),
                "apartment": apt,
                "combination": combo,
                "ratio": ratio,
                "rooms_number": rooms_number,
                "hull_area": hull_area,
                "total_area": total_area
            }
            records.append(record)
    return records

def process_all_jsons(base_folder):
    """
    Recursively walks through the base_folder, processes all .json files,
    and returns a list of records.
    """
    all_records = []
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    recs = process_json_file(file_path)
                    all_records.extend(recs)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    return all_records

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
                    ratio, hull_area, individual_areas = compute_spaces_convex_hull_ratio(data)

                    #print("Individual areas = ", individual_areas)
                    maximum_area = 3.2 * 14.

                    if hull_area > maximum_area:
                        weight = maximum_area / hull_area
                    else:
                        weight = 1.

                    # Store the ratio in our results
                    results.setdefault(folder_name, {})[file_name] = ratio
                    results.setdefault(folder_name, {})["area"] = hull_area

    return results

def save_records_to_csv(records, csv_path):
    """
    Saves a list of dictionary records to a CSV file at csv_path.
    """
    fieldnames = ["file", "apartment", "combination", "ratio","rooms_number", "hull_area", "total_area"]
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record)

if __name__ == "__main__":

    # Base folder containing your JSON files.
    json_folder_path = "/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/2025-AEC-Hackathon/json"
    # Output CSV file.
    csv_output_path = "/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/2025-AEC-Hackathon/results/naive_ratios.csv"

    # Process all JSON files.
    records = process_all_jsons(json_folder_path)

    # Save results to CSV.
    save_records_to_csv(records, csv_output_path)
    print(f"Saved results for {len(records)} records to {csv_output_path}")

    with open('/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/2025-AEC-Hackathon/json/ReferenceDesign_02/Reference02.json', 'r') as file:
        data = json.load(file) 

    iou = compute_space_combinations_ratios(data)


    apartment_ratios = compute_space_combinations_ratios_by_apartment(data)
    for apartment, combo_results in apartment_ratios.items():
        print(f"Apartment: {apartment}")
        for combo, (ratio,rooms_number, hull_area, total_area) in combo_results.items():
            print(f"  Combination: {combo}")
            print(f"    Ratio:      {ratio:.3f}")
            print(f"    Hull Area:  {hull_area:.2f}")
            print(f"    Total Area: {total_area:.2f}")
        print()
    