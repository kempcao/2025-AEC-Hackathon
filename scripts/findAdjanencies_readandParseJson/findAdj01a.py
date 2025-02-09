import json
from collections import defaultdict

# json file path
file_path = 'C:/Users/panz/Documents/GitHub/2025-AEC-Hackathon/json/GenericDesign_21004/21004.json'  # Adjust the path to your file

# Load the JSON data from the file
try:
    with open(file_path, 'r') as f:  # Open the file in read mode
        data = json.load(f)  # Parse the JSON content into a Python dictionary
        print("JSON data loaded successfully!")
except Exception as e:
    print(f"Error loading JSON file: {e}")
    exit(1)  # Exit if the file loading fails

# Initialize a dictionary to store adjacency relations
room_adjacency = defaultdict(set)
#initialize a counter for the apartments
aptCount = 0



# Loop through all panels and add adjacency edges
for panel_id, panel_data in data.get("panels", {}).get("items", {}).items():
    apartment = panel_data.get("apartment")
    #print (apartment)
    
    try:
        room = panel_data["room"]  # Get the room associated with the wall
        start_point = panel_data["start_point"]
        end_point = panel_data["end_point"]
    except KeyError as e:
        print(f"Missing key in panel {panel_id}: {e}")
        continue  # Skip this panel if it has missing data


    # Iterate through other panels to find shared walls
    for other_panel_id, other_panel_data in data["panels"]["items"].items():
        other_apartment = other_panel_data.get("apartment")
        if apartment == other_apartment:
            if panel_id != other_panel_id:
                try:
                    other_room = other_panel_data["room"]
                    other_start_point = other_panel_data["start_point"]
                    other_end_point = other_panel_data["end_point"]
                except KeyError as e:
                    print(f"Missing key in panel {other_panel_id}: {e}")
                    continue  # Skip this panel if it has missing data

                # Check if both panels share the same room
                if other_room != room and (
                    start_point == other_start_point or 
                    end_point == other_end_point
                ):
                    # If they share a common point, they are adjacent
                    room_adjacency[room].add(other_room)
                    room_adjacency[other_room].add(room)
    
#loop through all the spaces
# Extract apartments from the panels and spaces
apartments = set()


    
# Check apartments in spaces
for space in data["spaces"].values():
    spaceType = space.get("apartment")
    if spaceType =="Apartment 1" or spaceType =="Apartment 2" or spaceType =="Apartment 3":
        apartments.add(space.get("apartment"))
print (apartments)
# Count unique apartments
apartment_count = len(apartments)
print(f"There are {apartment_count} apartments in the floorplan.")



# Convert sets to lists before saving to JSON
for room, adjacent_rooms in room_adjacency.items():
    room_adjacency[room] = list(adjacent_rooms)
    print(f"{room} is adjacent to: {', '.join(adjacent_rooms)}")

    
# Now, we'll add the adjacency information to the JSON data
# Creating a new key "room_adjacency" to store the adjacency information
data['room_adjacency'] = room_adjacency


# Save the updated data to a new JSON file
output_file = 'C:/Users/panz/Documents/updated_floorplan.json'
try:
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Updated adjacency information saved to {output_file}")
except Exception as e:
    print(f"Error saving JSON file: {e}")
