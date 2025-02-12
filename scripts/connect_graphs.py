#!/usr/bin/env python3
import networkx as nx
import matplotlib.pyplot as plt
import json
import numpy as np
import re
import argparse
from pyvis.network import Network


def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments with attribute 'file_path'.
    """
    parser = argparse.ArgumentParser(
        description="Load a GraphML file into NetworkX and process it."
    )
    parser.add_argument("file_path", type=str, help="Path to the GraphML file")
    return parser.parse_args()


def visualize_graph_pyvis(G, output_html):
    """
    Visualize a NetworkX graph using PyVis.
    
    Args:
        G (networkx.Graph): The graph to visualize.
        output_html (str): The output HTML file name.
    """
    net = Network(
        notebook=False,
        height="750px",
        width="100%",
        bgcolor="#222222",  # background color
        font_color="white"   # font color
    )
    net.from_nx(G)
    net.show_buttons(filter_=["physics"])
    net.show(output_html, notebook=False)


def visualize_graph_matplotlib(G):
    """
    Visualize a NetworkX graph using matplotlib.
    
    Args:
        G (networkx.Graph): The graph to visualize.
    """
    nx.draw(
        G,
        with_labels=True,
        node_color='lightblue',
        edge_color='gray',
        node_size=2500,
        font_size=10
    )
    plt.show()


def extract_dimension_from_panel(panel):
    """
    Extract the 2D Euclidean distance (dimension) between the start and end points of a panel.
    
    The function assumes that panel["start_point"] and panel["end_point"] are strings
    containing numeric values. It uses regex to extract numbers, converts them to numeric
    values, and computes the distance based on the first two coordinates.
    
    Args:
        panel (dict): Node attributes containing "start_point" and "end_point".
    
    Returns:
        float: The computed Euclidean distance. Returns None if extraction fails.
    """
    # Extract numbers from start and end point strings.
    start_nums = re.findall(r"\d+\.\d+|\d+", panel.get("start_point", ""))
    end_nums = re.findall(r"\d+\.\d+|\d+", panel.get("end_point", ""))
    if not start_nums or not end_nums:
        return None

    # Convert string numbers to floats (or int if appropriate)
    start_point = [float(num) if '.' in num else int(num) for num in start_nums]
    end_point = [float(num) if '.' in num else int(num) for num in end_nums]

    # Compute 2D vector difference using the first two coordinates
    vector = np.array([end_point[0] - start_point[0], end_point[1] - start_point[1]])
    return np.linalg.norm(vector)


def add_similar_wall_connections(G, dimensions):
    """
    Add new connections between panels (walls) that are very similar in dimension and alignment.
    
    For each panel, the function looks for other panels with identical dimensions. It then
    checks if the panels belong to the same apartment and have aligned start/end points (in the
    same or reversed order). If so, it finds room nodes connected to these panels and, if not
    already connected, adds an edge between the room nodes.
    
    Args:
        G (networkx.Graph): The input graph containing panel nodes.
        dimensions (np.array): Array of computed dimensions for each panel. The index order is
                               assumed to match the order of nodes when iterating over G.nodes().
    """
    new_connections = {}

    # Iterate over each panel using its index (converted to string as node identifier)
    for i, dim in enumerate(dimensions):
        # Find indices of panels with the same dimension
        similar_indices = np.where(dimensions == dim)[0]

        node_i = str(i)
        if node_i not in G.nodes:
            continue

        panel_i = G.nodes[node_i]
        start_point_i = panel_i.get("start_point")
        end_point_i = panel_i.get("end_point")
        apartment_i = panel_i.get("apartment")

        for k in similar_indices:
            if k == i:
                continue  # Skip self-comparison

            node_k = str(k)
            if node_k not in G.nodes:
                continue

            panel_k = G.nodes[node_k]
            start_point_k = panel_k.get("start_point")
            end_point_k = panel_k.get("end_point")
            apartment_k = panel_k.get("apartment")

            # Ensure both panels are from the same apartment.
            if apartment_i != apartment_k:
                continue

            # Check if segments are aligned (either in the same order or reversed).
            aligned = (
                (start_point_i == start_point_k and end_point_i == end_point_k) or
                (start_point_i == end_point_k and end_point_i == start_point_k)
            )
            if not aligned:
                continue

            # Get neighboring nodes assumed to be room nodes.
            neighbors_i = list(G.neighbors(node_i))
            neighbors_k = list(G.neighbors(node_k))

            room_neighbor_i = next((n for n in neighbors_i if "room" in n.lower()), None)
            room_neighbor_k = next((n for n in neighbors_k if "room" in n.lower()), None)
            if not room_neighbor_i or not room_neighbor_k:
                continue  # Skip if valid room neighbors are not found

            # Add a new edge between the room nodes if not already connected.
            if room_neighbor_i in new_connections:
                print("Already connected")
                continue

            G.add_edge(room_neighbor_i, room_neighbor_k)
            new_connections[room_neighbor_i] = room_neighbor_k


def main():
    # -------------------------------------------------------------------------
    # 1. Parse arguments and load the GraphML file.
    # -------------------------------------------------------------------------
    args = parse_arguments()
    G = nx.read_graphml(args.file_path, force_multigraph=True)

    # -------------------------------------------------------------------------
    # 2. Initial visualization of the input graph.
    # -------------------------------------------------------------------------
    visualize_graph_pyvis(G, "my_interactive_graph.html")
    visualize_graph_matplotlib(G)

    # -------------------------------------------------------------------------
    # 3. Compute dimensions for panels based on start and end points.
    # -------------------------------------------------------------------------
    dimensions_list = []
    for node in G.nodes():
        panel = G.nodes[node]
        # Process only if both "start_point" and "end_point" exist.
        if "start_point" in panel and "end_point" in panel:
            dim = extract_dimension_from_panel(panel)
            dimensions_list.append(dim if dim is not None else 0)
        else:
            dimensions_list.append(0)
    dimensions_array = np.array(dimensions_list)

    # -------------------------------------------------------------------------
    # 4. Add new connections between similar walls (panels).
    # -------------------------------------------------------------------------
    add_similar_wall_connections(G, dimensions_array)

    # -------------------------------------------------------------------------
    # 5. Visualize the updated graph.
    # -------------------------------------------------------------------------
    visualize_graph_pyvis(G, "my_interactive_graph_2.html")
    visualize_graph_matplotlib(G)

    # -------------------------------------------------------------------------
    # 6. Save the updated graph in the same folder as the input file.
    # -------------------------------------------------------------------------
    folder = "/".join(args.file_path.split("/")[:-1])
    output_path = f"{folder}/reference_connected.graphml"
    nx.write_graphml(G, output_path)
    print(f"Updated graph saved to {output_path}")


if __name__ == "__main__":
    main()
