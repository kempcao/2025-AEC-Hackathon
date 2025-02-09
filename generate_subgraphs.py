import networkx as nx
import matplotlib.pyplot as plt
import argparse
import json
import numpy as np
import math


def get_room_or_apartment_nodes(G):
    """
    Returns a list of nodes whose labels contain
    'room' or 'apartment' (case-insensitive).
    """
    matches = []
    for node in G.nodes():  # node is usually a string or int
        # Convert to lower-case and check for substring
        node_lower = str(node).lower()
        if "room" in node_lower or "apartment" in node_lower:
            matches.append(node)
    return matches



"""
panels = data["panels"]
hasht = {}
for panel in panels:
    panels[panel]["start_point"]
    panels[panel]["end_point"]
    hasht[panel] = {}
"""

def compute_centroid(points):
    """
    Computes the centroid of a list of points, where each point is
    a dict with keys 'x', 'y', and 'z'. Returns a dict with keys
    'x', 'y', and 'z' corresponding to the centroid coordinates.
    
    Example:
        points = [
            {'x': 33.13, 'y': 11.76, 'z': 0},
            {'x': 33.96, 'y': 11.21, 'z': 0},
            ...
        ]
        centroid = compute_centroid(points)
    """
    if not points:
        raise ValueError("The list of points is empty.")

    # Sum up x, y, z separately
    sum_x = sum(p['x'] for p in points)
    sum_y = sum(p['y'] for p in points)
    sum_z = sum(p['z'] for p in points)

    # Compute the average for each coordinate
    n = len(points)
    centroid_x = sum_x / n
    centroid_y = sum_y / n
    centroid_z = sum_z / n

    return [centroid_x, centroid_y, centroid_z]

def euclidean_distance(coord1, coord2):
    """Compute 3D distance between two points (dicts with x,y,z)."""
    print(coord2)
    return math.sqrt(
        (coord2[0] - coord1[0])**2 +
        (coord2[1] - coord1[1])**2 +
        (coord2[2] - coord1[2])**2
    )


def get_distances(G_target):
    """
    Compute and store distances in edge attributes for a given graph G_target.
    """
    for u, v in G_target.edges():
        print(" previous  ", G_target.nodes[u])
        type_object_u = G_target.nodes[u].get("type")
        type_object_v = G_target.nodes[v].get("type")


        coord_u = G_target.nodes[u]["coordinates"]
        coord_v = G_target.nodes[v]["coordinates"]
        dist = euclidean_distance(coord_u, coord_v)
        G_target[u][v]["distance"] = dist

    # Print out edges to verify the distance attribute
    for edge in G_target.edges(data=True):
        print(edge)
    return G_target

with open('/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/hackathon/2025-AEC-Hackathon/json/ReferenceDesign_01/Reference01.json', 'r') as file:
    data = json.load(file)

spaces = data["spaces"]
with open('/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/hackathon/2025-AEC-Hackathon/json/GenericDesign_11001/11001.json', 'r') as file:
    data_generic = json.load(file)
spaces_generic = data_generic["spaces"]


#G_2 = nx.read_graphml("/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/hackathon/2025-AEC-Hackathon/json/GenericDesign_11001/reference_connected.graphml")
#G_2 = get_distances(G_2)
#nx.draw(G_2, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2500, font_size=10)


#First reference design
G_target_1 = nx.Graph()

G_target_g = nx.Graph()

dicti = ["bathroom", "corridor", "kitchen"]
for keys in spaces:
    space_type = spaces[keys]["room_type"]
    coordinates = spaces[keys]["coordinates"]
    #Centroid taking all the coordinates
    centroid = compute_centroid(coordinates)
    if space_type in dicti:
        G_target_1.add_node(space_type, coordinates = centroid)

G_target_1.add_edge("bathroom", "corridor")
G_target_1.add_edge("corridor", "kitchen")
G_target_1.add_edge("kitchen", "bathroom")

# Now compute and store distances in edge attributes
for u, v in G_target_1.edges():
    print(G_target_1.nodes[u]["coordinates"])
    coord_u = G_target_1.nodes[u]["coordinates"]
    coord_v = G_target_1.nodes[v]["coordinates"]
    dist = euclidean_distance(coord_u, coord_v)
    G_target_1[u][v]["distance"] = dist

# Print out edges to verify the distance attribute
for edge in G_target_1.edges(data=True):
    print(edge)

#Save the graph
nx.draw(G_target_1, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2500, font_size=10)
plt.show()

dicti = ["bathroom", "corridor", "kitchen", "living room", "bedroom"]
for keys in spaces_generic:
    space_type = spaces_generic[keys]["room_type"]
    coordinates = spaces_generic[keys]["coordinates"]
    #Centroid taking all the coordinates
    centroid = compute_centroid(coordinates)

    if space_type in dicti:

        G_target_g.add_node(space_type, coordinates = centroid)

G_target_g.add_edge("bathroom", "corridor")
G_target_g.add_edge("corridor", "kitchen")
G_target_g.add_edge("kitchen", "bathroom")

# Now compute and store distances in edge attributes
for u, v in G_target_g.edges():
    coordinates = G_target_g.nodes[u].get("coordinates")
    coordinates_2 = G_target_g.nodes[v].get("coordinates")
    if coordinates is not None and coordinates_2 is not None:
        print(G_target_g.nodes[u]["coordinates"])
        coord_u = G_target_g.nodes[u]["coordinates"]
        coord_v = G_target_g.nodes[v]["coordinates"]
        dist = euclidean_distance(coord_u, coord_v)
        G_target_g[u][v]["distance"] = dist

# Print out edges to verify the distance attribute
for edge in G_target_g.edges(data=True):
    print(edge)

#Save the graph
nx.draw(G_target_g, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2500, font_size=10)
plt.show()

#Compare the two graphs

nx.graph_edit_distance(G_target_1, G_target_g)

nx.write_graphml(G_target_1, '/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/hackathon/2025-AEC-Hackathon/json/ReferenceDesign_01/target01.graphml')







