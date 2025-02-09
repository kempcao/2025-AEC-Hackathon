import argparse
import networkx as nx
import numpy as np
import random
import netlsd
import sys
import matplotlib.pyplot as plt
from sklearn.manifold import SpectralEmbedding
# Visualizing the embedding

parser = argparse.ArgumentParser(description="Load a GraphML file into NetworkX.")
parser.add_argument("file_path_1", type=str, help="Path to the GraphML file")
parser.add_argument("file_path_2", type=str, help="Path to the GraphML file")

# Parse arguments
args = parser.parse_args()

G_1 = nx.read_graphml(args.file_path_1, force_multigraph = True)
G_2 = nx.read_graphml(args.file_path_2, force_multigraph = True)

nx.graph_edit_distance(G_1, G_2)
#similarity = nx.simrank_similarity(G_1, G_2)

sys.exit()
#Comparison of level 1

def node_simrank_scores(G):
    """
    Computes SimRank for all node pairs in G,
    then returns a dictionary of node -> aggregated score
    (e.g., average similarity to all other nodes).
    """
    sim = nx.simrank_similarity(G)  # sim is a dict of dicts: sim[u][v]
    
    scores = {}
    for u in G.nodes():
        # Compute an aggregated similarity for node u
        # e.g., average similarity to all other nodes
        similarities = [sim[u][v] for v in sim[u] if v != u]
        if similarities:
            scores[u] = np.mean(similarities)
        else:
            # If it's an isolated node, fallback to 0 or None
            scores[u] = 0.0
    return scores

def simrank(G, u, v):
    in_neighbors_u = G.predecessors(u)
    in_neighbors_v = G.predecessors(v)
    scale = C / (len(in_neighbors_u) * len(in_neighbors_v))
    return scale * sum(
        simrank(G, w, x) for w, x in product(in_neighbors_u, in_neighbors_v)
    )




def draw_graph_with_simrank(G, ax, title="Graph", cmap=plt.cm.Blues):
    """
    Draw graph G on a given matplotlib Axes (ax),
    color-coding nodes by their aggregated SimRank scores.
    """
    # 1) Compute aggregated SimRank scores
    scores_dict = node_simrank_scores(G)
    
    # 2) Make a color list in the same order as G.nodes()
    node_list = list(G.nodes())
    scores = [scores_dict[node] for node in node_list]
    
    # 3) Normalize scores for a color map
    max_score = max(scores) if scores else 1
    node_colors = [score / max_score for score in scores]
    
    # 4) Draw the graph
    pos = nx.spring_layout(G, seed=42)  # or any layout you prefer
    nx.draw(
        G, pos, ax=ax, 
        with_labels=True,
        node_color=node_colors,
        node_cmap=cmap,
        edge_color="gray"
    )
    ax.set_title(title)

def netlsd_distance(G1, G2):
    # Convert to adjacency matrix or remain as Nx graph
    A1 = nx.to_numpy_array(G1)
    A2 = nx.to_numpy_array(G2)
    
    sig1 = netlsd.signature(A1, timescales=250)  # netLSD signature
    sig2 = netlsd.signature(A2, timescales=250)
    
    return netlsd.compare(sig1, sig2, metric='euclid')

def draw_graph_with_simrank(G, ax, title="Graph (SimRank coloring)", cmap=plt.cm.Blues):
    """
    Draw graph G on a given matplotlib Axes (ax),
    coloring each node by its average SimRank score.
    """
    # 1) Get the average SimRank score per node
    scores_dict = node_simrank_scores(G)
    
    # 2) Build a color array in the same order as G.nodes()
    node_list = list(G.nodes())
    scores = [scores_dict[node] for node in node_list]
    
    # 3) Normalize scores so the highest becomes 1.0 (for better color range)
    max_score = max(scores) if scores else 1
    node_colors = [score / max_score for score in scores]
    
    # 4) Choose a layout
    pos = nx.spring_layout(G, seed=42)
    
    # 5) Draw the graph
    nx.draw(
        G,
        pos,
        ax=ax,
        with_labels=True,
        node_color=node_colors,
        cmap=cmap,             # <-- use cmap=..., not node_cmap=...
        edge_color="gray"
    )
    ax.set_title(title)

# Example usage:

# Suppose you've already loaded your graphs:
# G_1 = nx.read_graphml("path_to_graph_1.graphml")
# G_2 = nx.read_graphml("path_to_graph_2.graphml")

# Then compare them side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

scores = node_simrank_scores(G_1)


#draw_graph_with_simrank(G_1, ax1, title="Graph 1 (SimRank coloring)")
#draw_graph_with_simrank(G_2, ax2, title="Graph 2 (SimRank coloring)")

#plt.show()

#comparisons = netlsd_distance(G_1, G_2)


descriptor = netlsd.heat(G_1) # compute the signature
print(descriptor)

