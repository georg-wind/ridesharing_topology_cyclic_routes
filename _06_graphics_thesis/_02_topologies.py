import networkx as nx
import matplotlib.pyplot as plt

from utils import graph_constructor, topo_color, graphics_dir


topologies = ["line", "star", "cycle", "wheel", "grid"]
N = 9

# Create a figure for subplots
fig, axes = plt.subplots(1, len(topologies), figsize=(20, 4))  # Adjust figsize as needed


for i, topology in enumerate(topologies):
    # Construct the graph using your custom function
    graph = graph_constructor(f"{topology}_{N}")
    color_topology = topo_color(topology)

    # Extract the positions from node attributes
    pos = nx.get_node_attributes(graph, 'pos')

    # Choose the subplot
    ax = axes[i]

    # Draw the graph using the positions
    # nx.draw(graph, pos=pos, ax=ax, with_labels=False, node_color='#006080', node_size=80, edge_color='gray')
    nx.draw(graph, pos=pos, ax=ax, with_labels=False, node_color=color_topology, node_size=80, edge_color='gray')

    # Set the title for each subplot
    ax.set_title(topology.capitalize(), size=30)

# Adjust layout to not overlap and show the plot
plt.tight_layout()
plt.savefig(
    fr"{graphics_dir}\02_stylized_topologies_9.png",
    dpi=300)
plt.show()
