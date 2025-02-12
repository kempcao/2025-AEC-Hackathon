import networkx as nx
import matplotlib.pyplot as plt
import argparse  # Included if you later want to add command-line arguments.
import json
import numpy as np
import math


def get_room_or_apartment_nodes(G):
    """
    Return nodes whose label contains 'room' or 'apartment' (case-insensitive).

    Args:
        G (networkx.Graph): The input graph.

    Returns:
        list: A list of nodes (labels) containing "room" or "apartment".
    """
    matches = []
    for node in G.nodes():
        if "room" in str(node).lower() or "apartment" in str(node).lower():
            matches.append(node)
    return matches


def compute_centroid(points):
    """
    Compute the centroid of a list of points.

    Each point is a dict with keys 'x', 'y', and 'z'. The centroid is computed
    as the average of all x, y, and z coordinates.

    Args:
        points (list): List of dicts representing points, e.g.:
            [{'x': 33.13, 'y': 11.76, 'z': 0}, {'x': 33.96, 'y': 11.21, 'z': 0}, ...]

    Returns:
        list: The centroid coordinates as [centroid_x, centroid_y, centroid_z].

    Raises:
        ValueError: If the input list is empty.
    """
    if not points:
        raise ValueError("The list of points is empty.")

    n = len(points)
    centroid_x = sum(p['x'] for p in points) / n
    centroid_y = sum(p['y'] for p in points) / n
    centroid_z = sum(p['z'] for p in points) / n
    return [centroid_x, centroid_y, centroid_z]


def euclidean_distance(coord1, coord2):
    """
    Compute the 3D Euclidean distance between two coordinates.

    Args:
        coord1 (list/tuple): First coordinate as [x, y, z].
        coord2 (list/tuple): Second coordinate as [x, y, z].

    Returns:
        float: The Euclidean distance.
    """
    return math.sqrt(
        (coord2[0] - coord1[0])**2 +
        (coord2[1] - coord1[1])**2 +
        (coord2[2] - coord1[2])**2
    )


def get_distances(G_target):
    """
    Compute and assign Euclidean distances as edge attributes for a graph.

    The function reads the 'coordinates' attribute of each node to compute the
    distance for every edge and stores it as the "distance" attribute on that edge.

    Args:
        G_target (networkx.Graph): The input graph with node attribute "coordinates".

    Returns:
        networkx.Graph: The graph with updated edge attributes.
    """
    for u, v in G_target.edges():
        coord_u = G_target.nodes[u]["coordinates"]
        coord_v = G_target.nodes[v]["coordinates"]
        dist = euclidean_distance(coord_u, coord_v)
        G_target[u][v]["distance"] = dist

    return G_target


# =============================================================================
# Load JSON data for both the reference and generic designs.
# =============================================================================

# Load the reference design JSON.
with open('/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/hackathon/2025-AEC-Hackathon/json/ReferenceDesign_01/Reference01.json', 'r') as file:
    data = json.load(file)
spaces = data["spaces"]

# Load the generic design JSON.
with open('/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/hackathon/2025-AEC-Hackathon/json/GenericDesign_11001/11001.json', 'r') as file:
    data_generic = json.load(file)
spaces_generic = data_generic["spaces"]

# =============================================================================
# Create Graphs for the Reference Design and the Generic Design.
# =============================================================================

# Create a graph for the reference design.
G_target_1 = nx.Graph()
# Create a graph for the generic design.
G_target_g = nx.Graph()

# Define room types of interest for the reference design.
ref_room_types = ["bathroom", "corridor", "kitchen"]

# Add nodes to the reference graph based on the spaces.
# Each node is identified by its room type and stores the centroid of its coordinates.
for key in spaces:
    space = spaces[key]
    space_type = space["room_type"]
    coordinates = space["coordinates"]
    centroid = compute_centroid(coordinates)
    if space_type in ref_room_types:
        G_target_1.add_node(space_type, coordinates=centroid)

# Add edges between the rooms in the reference design.
G_target_1.add_edge("bathroom", "corridor")
G_target_1.add_edge("corridor", "kitchen")
G_target_1.add_edge("kitchen", "bathroom")

# Compute and store distances for each edge in the reference graph.
for u, v in G_target_1.edges():
    coord_u = G_target_1.nodes[u]["coordinates"]
    coord_v = G_target_1.nodes[v]["coordinates"]
    dist = euclidean_distance(coord_u, coord_v)
    G_target_1[u][v]["distance"] = dist

# Visualize the reference design graph.
nx.draw(G_target_1, with_labels=True, node_color='lightblue',
        edge_color='gray', node_size=2500, font_size=10)
plt.show()

# Define room types of interest for the generic design.
gen_room_types = ["bathroom", "corridor", "kitchen", "living room", "bedroom"]

# Add nodes to the generic graph based on the spaces.
for key in spaces_generic:
    space = spaces_generic[key]
    space_type = space["room_type"]
    coordinates = space["coordinates"]
    centroid = compute_centroid(coordinates)
    if space_type in gen_room_types:
        G_target_g.add_node(space_type, coordinates=centroid)

# Add edges between selected rooms in the generic design.
G_target_g.add_edge("bathroom", "corridor")
G_target_g.add_edge("corridor", "kitchen")
G_target_g.add_edge("kitchen", "bathroom")

# Compute and store distances for each edge in the generic graph.
for u, v in G_target_g.edges():
    coord_u = G_target_g.nodes[u].get("coordinates")
    coord_v = G_target_g.nodes[v].get("coordinates")
    if coord_u is not None and coord_v is not None:
        dist = euclidean_distance(coord_u, coord_v)
        G_target_g[u][v]["distance"] = dist

# Visualize the generic design graph.
nx.draw(G_target_g, with_labels=True, node_color='lightblue',
        edge_color='gray', node_size=2500, font_size=10)
plt.show()

# =============================================================================
# Compare the two graphs and save one of them.
# =============================================================================

# Compute the graph edit distance between the two graphs.
ged = nx.graph_edit_distance(G_target_1, G_target_g)
print("Graph edit distance between reference and generic designs:", ged)

# Save the reference design graph as a GraphML file.
nx.write_graphml(
    G_target_1,
    '/Users/diego/Desktop/Escritorio_MacBook_Pro_de_Diego/hackathon/2025-AEC-Hackathon/json/ReferenceDesign_01/target01.graphml'
)
