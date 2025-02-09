import networkx as nx 
import matplotlib.pyplot as plt
import json
import numpy as np
import re
import argparse
from pyvis.network import Network

# Set up argument parser
parser = argparse.ArgumentParser(description="Load a GraphML file into NetworkX.")
parser.add_argument("file_path", type=str, help="Path to the GraphML file")

# Parse arguments
args = parser.parse_args()

G = nx.read_graphml(args.file_path, force_multigraph = True)
nodes = G.nodes()
edges = G.edges()

# 2. Initialize PyVis Network
net = Network(notebook=False, 
              height="750px", 
              width="100%", 
              bgcolor="#222222",  # background color
              font_color="white") # font color

# 3. Convert NetworkX graph to PyVis
net.from_nx(G)

# 4. (Optional) Tweak appearance
# For example, set node colors or physics settings
net.show_buttons(filter_=['physics'])

# 5. Show or save

net.show("my_interactive_graph.html", notebook=False)

nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2500, font_size=10)
plt.show()

dimensions = []

for node in nodes:
    panel = G.nodes[node]
    valid = panel.get("start_point")
    if valid:
        # Use regex to extract numbers (both integers and decimals)
        start_point = re.findall(r"\d+\.\d+|\d+", panel["start_point"])
        start_point = [float(num) if '.' in num else int(num) for num in start_point]
        end_point = re.findall(r"\d+\.\d+|\d+", panel["start_point"])
        end_point = [float(num) if '.' in num else int(num) for num in end_point]

        vector = [end_point[0] - start_point[0], end_point[1] - start_point[1]] 
        vector = np.array(vector)
        dimensions.append(np.linalg.norm(vector))

dimensions = np.array(dimensions)


#Walls that are very similar

new_connections = {}
for i, dim in enumerate(dimensions):
    pos_1 = np.where(dimensions == dim)[0]
    
    start_point = G.nodes[str(i)]["start_point"]
    end_point = G.nodes[str(i)]["end_point"]
    apartment_1 = G.nodes[str(i)]["apartment"]

    for k in pos_1:
        if k == i:
            continue  # Skip self-comparison

        start_point_test = G.nodes[str(k)]["start_point"]
        end_point_test = G.nodes[str(k)]["end_point"]
        apartment_2 = G.nodes[str(k)]["apartment"]

        if apartment_1 != apartment_2:
            continue  # Ensure they are in the same apartment

        # Check if segments align correctly (forward or reverse)
        aligned = (start_point == start_point_test and end_point == end_point_test) or \
                  (start_point == end_point_test and end_point == start_point_test)

        if not aligned:
            continue

        # Get connected rooms
        neighbors_1 = list(G.neighbors(str(i)))
        neighbors_2 = list(G.neighbors(str(k)))

        room_neighbors_1 = next((node for node in neighbors_1 if "room" in node.lower()), None)
        room_neighbors_2 = next((node for node in neighbors_2 if "room" in node.lower()), None)

        if not room_neighbors_1 or not room_neighbors_2:
            continue  # Ensure valid rooms exist

        # Modify graph only if connection doesn't exist
        if room_neighbors_1 in new_connections:
            print("Already connected")
            continue

        G.add_edge(room_neighbors_1, room_neighbors_2)
        new_connections[room_neighbors_1] = room_neighbors_2



# 2. Initialize PyVis Network
net = Network(notebook=False, 
              height="750px", 
              width="100%", 
              bgcolor="#222222",  # background color
              font_color="white") # font color

# 3. Convert NetworkX graph to PyVis
net.from_nx(G)

# 4. (Optional) Tweak appearance
# For example, set node colors or physics settings
net.show_buttons(filter_=['physics'])

# 5. Show or save
net.show("my_interactive_graph_2.html", notebook=False)


nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2500, font_size=10)
plt.show()

# Save the updated graph
folder = args.file_path.split("/")[:-1]
folder = "/".join(folder)
nx.write_graphml(G, f"{folder}/reference_connected.graphml")
