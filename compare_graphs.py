#!/usr/bin/env python3
import argparse
import networkx as nx
import numpy as np
import random
import netlsd
import sys
import matplotlib.pyplot as plt
from sklearn.manifold import SpectralEmbedding
from itertools import product  # Required for the simrank function below

def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments containing file_path_1 and file_path_2.
    """
    parser = argparse.ArgumentParser(
        description="Load two GraphML files into NetworkX and compare them."
    )
    parser.add_argument("file_path_1", type=str, help="Path to the first GraphML file")
    parser.add_argument("file_path_2", type=str, help="Path to the second GraphML file")
    return parser.parse_args()


def node_simrank_scores(G):
    """
    Compute SimRank scores for all node pairs in graph G.

    Returns a dictionary mapping each node to its aggregated SimRank score,
    computed as the average similarity to all other nodes.

    Args:
        G (networkx.Graph): The input graph.

    Returns:
        dict: Mapping of node -> average SimRank score.
    """
    # Compute pairwise SimRank similarity (returns a dict-of-dicts)
    sim = nx.simrank_similarity(G)
    scores = {}
    for u in G.nodes():
        # Exclude self-similarity and compute average similarity for node u.
        similarities = [sim[u][v] for v in sim[u] if v != u]
        scores[u] = np.mean(similarities) if similarities else 0.0
    return scores


def simrank(G, u, v, C=0.8):
    """
    Recursively compute SimRank between nodes u and v in a directed graph G.
    
    NOTE: This is a placeholder function and may not be efficient or converge
          for general graphs. It is not used in the main example.

    Args:
        G (networkx.DiGraph): A directed graph.
        u: Node u.
        v: Node v.
        C (float): Decay factor for SimRank.

    Returns:
        float: SimRank score between nodes u and v.
    """
    in_neighbors_u = list(G.predecessors(u))
    in_neighbors_v = list(G.predecessors(v))
    if not in_neighbors_u or not in_neighbors_v:
        return 0.0

    scale = C / (len(in_neighbors_u) * len(in_neighbors_v))
    return scale * sum(
        simrank(G, w, x, C) for w, x in product(in_neighbors_u, in_neighbors_v)
    )


def draw_graph_with_simrank(G, ax, title="Graph (SimRank Coloring)", cmap=plt.cm.Blues):
    """
    Draw graph G on a given matplotlib Axes (ax), coloring nodes by their average SimRank score.

    Args:
        G (networkx.Graph): The input graph.
        ax (matplotlib.axes.Axes): The axes to draw the graph.
        title (str): Title for the plot.
        cmap: Colormap to use for node coloring.
    """
    # 1) Compute aggregated SimRank scores.
    scores_dict = node_simrank_scores(G)
    
    # 2) Build a color array in the same order as G.nodes()
    node_list = list(G.nodes())
    scores = [scores_dict[node] for node in node_list]
    
    # 3) Normalize scores for a proper color mapping.
    max_score = max(scores) if scores else 1
    node_colors = [score / max_score for score in scores]
    
    # 4) Compute node layout (using a spring layout here)
    pos = nx.spring_layout(G, seed=42)
    
    # 5) Draw the graph with the chosen colormap.
    nx.draw(
        G,
        pos,
        ax=ax,
        with_labels=True,
        node_color=node_colors,
        cmap=cmap,
        edge_color="gray"
    )
    ax.set_title(title)


def netlsd_distance(G1, G2):
    """
    Compute the netLSD distance between two graphs G1 and G2.

    This function converts each graph to a NumPy adjacency matrix,
    computes the netLSD signature for each, and then returns the
    Euclidean distance between the signatures.

    Args:
        G1 (networkx.Graph): First graph.
        G2 (networkx.Graph): Second graph.

    Returns:
        float: The Euclidean distance between the netLSD signatures.
    """
    A1 = nx.to_numpy_array(G1)
    A2 = nx.to_numpy_array(G2)
    
    sig1 = netlsd.signature(A1, timescales=250)
    sig2 = netlsd.signature(A2, timescales=250)
    
    return netlsd.compare(sig1, sig2, metric='euclid')


def main():
    # Parse command-line arguments.
    args = parse_arguments()

    # Load graphs from the provided GraphML files.
    G_1 = nx.read_graphml(args.file_path_1, force_multigraph=True)
    G_2 = nx.read_graphml(args.file_path_2, force_multigraph=True)
    
    # Compute and print the graph edit distance between G_1 and G_2.
    ged = nx.graph_edit_distance(G_1, G_2)
    print(f"Graph Edit Distance: {ged}")
    
    # Compute netLSD signature for the first graph and print it.
    descriptor = netlsd.heat(G_1)
    print("netLSD Signature for Graph 1:")
    print(descriptor)
    
    # Create a figure with two subplots to visualize both graphs.
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Draw each graph with nodes colored by their SimRank scores.
    draw_graph_with_simrank(G_1, ax1, title="Graph 1 (SimRank Coloring)")
    draw_graph_with_simrank(G_2, ax2, title="Graph 2 (SimRank Coloring)")
    
    plt.show()


if __name__ == "__main__":
    main()


descriptor = netlsd.heat(G_1) # compute the signature
print(descriptor)

