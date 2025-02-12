import json
import re
import os
import csv
from shapely.geometry import Polygon, MultiPolygon
from itertools import combinations


def polygon_from_coords(coords):
    """Convert a list of {'x', 'y', 'z'} dicts to a 2D Shapely Polygon (ignores 'z')."""
    points_2d = [(pt["x"], pt["y"]) for pt in coords]
    return Polygon(points_2d)


def compute_spaces_convex_hull_ratio(data):
    """
    Compute the ratio of the sum of areas of selected spaces to the area of their convex hull.
    
    Only spaces with room types "bathroom", "corridor", or "kitchen" are considered.
    
    Returns:
        (ratio, hull_area, individual_areas): tuple containing:
            - ratio: total area / convex hull area (or 0.0 if no valid hull)
            - hull_area: area of the convex hull
            - individual_areas: list of dicts with individual room area by room type
    """
    relevant_room_types = {"bathroom", "corridor", "kitchen"}
    polygons = []
    total_area = 0.0
    individual_areas = []

    for space_info in data.get("spaces", {}).values():
        room_type = space_info.get("room_type", "").lower()
        if room_type in relevant_room_types:
            coords = space_info.get("coordinates", [])
            poly = Polygon([(c["x"], c["y"]) for c in coords])
            polygons.append(poly)
            total_area += poly.area
            individual_areas.append({room_type: poly.area})

    if not polygons:
        return 0.0

    multi_poly = MultiPolygon(polygons)
    hull = multi_poly.convex_hull
    hull_area = hull.area

    if hull_area == 0:
        return 0.0
    return total_area / hull_area, hull_area, individual_areas


def compute_space_combinations_ratios(data):
    """
    Compute the area ratio for every combination of room types (bathroom, corridor, kitchen).
    
    Combinations include single room types, pairs, and all three together.
    The ratio is computed as (total area of selected spaces) / (convex hull area of those spaces)
    and adjusted by a weight based on the total number of spaces.
    
    Returns:
        dict: Mapping of combination names (e.g. "bathroom,corridor") to a tuple:
              (ratio, hull_area, total_area)
    """
    relevant_room_types = {"bathroom", "corridor", "kitchen"}
    polygons_by_type = {rt: [] for rt in relevant_room_types}
    total_rooms = 0

    for space_info in data.get("spaces", {}).values():
        room_type = space_info.get("room_type", "").lower()
        total_rooms += 1
        if room_type in relevant_room_types:
            coords = space_info.get("coordinates", [])
            poly = Polygon([(c["x"], c["y"]) for c in coords])
            polygons_by_type[room_type].append(poly)

    active_room_types = [rt for rt in ["bathroom", "corridor", "kitchen"] if polygons_by_type[rt]]
    if not active_room_types:
        return {}

    results = {}
    for r in range(1, len(active_room_types) + 1):
        for combo in combinations(active_room_types, r):
            combo_name = ",".join(sorted(combo))
            combo_polygons = []
            for room in combo:
                combo_polygons.extend(polygons_by_type[room])

            if not combo_polygons:
                results[combo_name] = (0.0, 0.0, 0.0)
                continue

            total_area = sum(poly.area for poly in combo_polygons)
            multi_poly = MultiPolygon(combo_polygons)
            hull_area = multi_poly.convex_hull.area

            # Compute a weight based on the total number of spaces and number in this combo.
            weight = 1 / (((total_rooms + 1) / 2) - len(combo))
            ratio = (total_area / hull_area) * weight if hull_area != 0 else 0.0

            results[combo_name] = (ratio, hull_area, total_area)

    return results


def compute_space_combinations_ratios_by_apartment(data, weight_flag=False):
    """
    Compute area ratios by apartment for every combination of room types (bathroom, corridor, kitchen).
    
    For each apartment, only the room types present are considered. For a combination containing only
    one polygon, the convex hull area is forced to equal the polygon's area.
    
    Args:
        data (dict): JSON data containing spaces with their coordinates, room type, and apartment name.
        weight_flag (bool): Whether to adjust the ratio by a computed weight.
    
    Returns:
        dict: Mapping of apartment names to another dict that maps combination names to a tuple:
              (ratio, total_rooms, hull_area, total_area)
    """
    relevant_room_types = {"bathroom", "corridor", "kitchen"}
    apartments = {}
    total_rooms = 0

    for space_info in data.get("spaces", {}).values():
        room_type = space_info.get("room_type", "").lower()
        total_rooms += 1
        if room_type not in relevant_room_types:
            continue

        apartment = space_info.get("apartment", "Unknown")
        poly = polygon_from_coords(space_info.get("coordinates", []))

        if apartment not in apartments:
            apartments[apartment] = {rt: [] for rt in relevant_room_types}
        apartments[apartment][room_type].append(poly)

    results = {}
    for apartment, poly_dict in apartments.items():
        active_types = [rt for rt in ["bathroom", "corridor", "kitchen"] if poly_dict[rt]]
        if not active_types:
            continue

        apt_results = {}
        for r in range(1, len(active_types) + 1):
            for combo in combinations(active_types, r):
                combo_key = ",".join(sorted(combo))
                combo_polygons = []
                for rt in combo:
                    combo_polygons.extend(poly_dict[rt])

                if not combo_polygons:
                    apt_results[combo_key] = (0.0, 0.0, 0.0)
                    continue

                total_area = sum(poly.area for poly in combo_polygons)
                weight = (
                    1 / (((total_rooms + 1) / 2) - len(combo))
                    if weight_flag
                    else 1
                )
                if len(combo_polygons) == 1:
                    hull_area = total_area
                else:
                    multi_poly = MultiPolygon(combo_polygons)
                    hull_area = multi_poly.convex_hull.area

                ratio = (total_area / hull_area) * weight if hull_area != 0 else 0.0
                apt_results[combo_key] = (ratio, total_rooms, hull_area, total_area)

        results[apartment] = apt_results

    return results


def process_json_file(file_path):
    """
    Process a JSON file to compute apartment-level ratios.
    
    Args:
        file_path (str): Path to the JSON file.
    
    Returns:
        list: A list of dictionaries representing computed records.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    apartment_results = compute_space_combinations_ratios_by_apartment(data, weight_flag=False)

    records = []
    for apt, combos in apartment_results.items():
        for combo, (ratio, rooms_number, hull_area, total_area) in combos.items():
            records.append({
                "file": os.path.basename(file_path),
                "apartment": apt,
                "combination": combo,
                "ratio": ratio,
                "rooms_number": rooms_number,
                "hull_area": hull_area,
                "total_area": total_area
            })
    return records


def process_all_jsons(base_folder):
    """
    Recursively process all .json files in the specified base folder.
    
    Args:
        base_folder (str): The directory to search for JSON files.
    
    Returns:
        list: A list of records aggregated from all JSON files.
    """
    all_records = []
    for root, _, files in os.walk(base_folder):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    records = process_json_file(file_path)
                    all_records.extend(records)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    return all_records


def load_jsons_and_compute_ratios(base_json_folder):
    """
    Process JSON files within subfolders starting with 'GenericDesign_' and compute ratios.
    
    Only files matching the pattern '<number>.json' are processed.
    
    Returns:
        dict: A dictionary mapping folder names to file ratios and hull area.
    """
    json_filename_pattern = re.compile(r'^\d+\.json$')
    results = {}

    for folder_name in os.listdir(base_json_folder):
        if folder_name.startswith("GenericDesign_"):
            folder_path = os.path.join(base_json_folder, folder_name)
            if not os.path.isdir(folder_path):
                continue

            for file_name in os.listdir(folder_path):
                if json_filename_pattern.match(file_name):
                    file_path = os.path.join(folder_path, file_name)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    except (json.JSONDecodeError, OSError) as e:
                        print(f"Error loading {file_path}: {e}")
                        continue

                    ratio, hull_area, individual_areas = compute_spaces_convex_hull_ratio(data)
                    maximum_area = 3.2 * 14.0
                    weight = maximum_area / hull_area if hull_area > maximum_area else 1.0

                    results.setdefault(folder_name, {})[file_name] = ratio
                    results.setdefault(folder_name, {})["area"] = hull_area

    return results


def save_records_to_csv(records, csv_path):
    """
    Save a list of dictionary records to a CSV file.
    
    Args:
        records (list): List of dictionaries representing records.
        csv_path (str): Path to the output CSV file.
    """
    fieldnames = ["file", "apartment", "combination", "ratio", "rooms_number", "hull_area", "total_area"]
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record)


if __name__ == "__main__":
    # Define paths for JSON files and CSV output.
    json_folder_path = "/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/2025-AEC-Hackathon/json"
    csv_output_path = "/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/2025-AEC-Hackathon/results/naive_ratios.csv"

    # Process all JSON files and save the results to CSV.
    records = process_all_jsons(json_folder_path)
    save_records_to_csv(records, csv_output_path)
    print(f"Saved results for {len(records)} records to {csv_output_path}")

    # Example usage for additional computations.
    reference_json_path = "/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/2025-AEC-Hackathon/json/ReferenceDesign_02/Reference02.json"
    with open(reference_json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    iou = compute_space_combinations_ratios(data)
    apartment_ratios = compute_space_combinations_ratios_by_apartment(data)

    for apartment, combos in apartment_ratios.items():
        print(f"Apartment: {apartment}")
        for combo, (ratio, rooms_number, hull_area, total_area) in combos.items():
            print(f"  Combination: {combo}")
            print(f"    Ratio:      {ratio:.3f}")
            print(f"    Hull Area:  {hull_area:.2f}")
            print(f"    Total Area: {total_area:.2f}")
        print()
