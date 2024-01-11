import matplotlib
import matplotlib.pyplot as plt
import networkx as nx

from utils import graphics_dir


def draw_hamilton_cycle(G, pos, construction, ax):
    color_network = "black"
    cmap = matplotlib.colormaps["tab10"]

    # Draw all edges with base color
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='black')
    nx.draw_networkx_nodes(G, pos=pos, ax=ax, node_color=color_network, node_size=40)

    edge_labels = dict((n, "") for n in G.edges())

    for step in construction.keys():
        routenodes = construction[step]["route"]
        routeedges = [(routenodes[i], routenodes[i + 1]) for i in range(len(routenodes) - 1)]
        edge_labels[routeedges[len(routeedges) // 2]] = str(step)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, label_pos=0.57, font_size=18, ax=ax, rotate=False)

    for step in construction.keys():
        if any(letter in str(step) for letter in ["a", "b", "c", "d"]):
            col_key = 2
        elif "I" in str(step):
            col_key = 3
        elif "&" in str(step):
            col_key = 1
        elif step in [5, 6, 9]:
            col_key = 4
        else:
            col_key = 0
        color = cmap(col_key)
        """ Draw highlighted edges with shaded area. """
        routenodes = construction[step]["route"]
        routeedges = [(routenodes[i], routenodes[i + 1]) for i in range(len(routenodes) - 1)]

        if step == 1:
            start_node = routenodes[0]
            # make the first node of the route a square
            nx.draw_networkx_nodes(G, pos=pos, ax=ax, nodelist=[start_node], node_color=color_network,
                                   node_size=80, node_shape='s')

        # CYCLE-edges
        if col_key in [0, 4, 1]:
            nx.draw_networkx_edges(G, pos, edgelist=routeedges, ax=ax, edge_color=color,
                                   alpha=0.4, width=12)
        else:
            nx.draw_networkx_edges(G, pos, edgelist=routeedges, ax=ax, edge_color=color,
                                   alpha=0.4, width=12, style="--")


# Create a figure with 4 subplots
fig, axs = plt.subplots(1, 2, figsize=(14, 5))
# ad legend to the figure


# Plot both graphs
# Graph 1
# Define the base graph and positions
m = 5
n = 6

base_net_graph = nx.grid_2d_graph(m, n)
pos = dict((n, (n[1], n[0])) for n in base_net_graph.nodes())

construction = {
    1: {"route": [(0, 0), (m - 1, 0)]},
    2: {"route": [(m - 1, 0), (m - 1, n - 1)]},
    3: {"route": [(m - 1, n - 1), (0, n - 1)]},
    4: {"route": [(0, n - 1), (0, n - 2)]},
    "a.1": {"route": [(0, n - 2), (m - 2, n - 2)]},
    "b.1": {"route": [(m - 2, n - 2), (m - 2, n - 3)]},
    "c.1": {"route": [(m - 2, n - 3), (0, n - 3)]},
    "d.1": {"route": [(0, n - 3), (0, n - 4)]},
    "a.2": {"route": [(0, n - 4), (m - 2, n - 4)]},
    "b.2": {"route": [(m - 2, n - 4), (m - 2, n - 5)]},
    "c.2": {"route": [(m - 2, n - 5), (0, n - 5)]},
    "d.2": {"route": [(0, n - 5), (0, n - 6)]},
}

draw_hamilton_cycle(base_net_graph, pos, construction, axs[0])
axs[0].set_xlabel(f"Horizontal axis, $n = {n}$", fontsize=20)
axs[0].set_ylabel(f"Vertical axis, $m = {m}$", fontsize=20)

# Graph 2
# Define the base graph and positions
m = 5
n = 7

base_net_graph = nx.grid_2d_graph(m, n)
pos = dict((n, (n[1], n[0])) for n in base_net_graph.nodes())

construction = {
    # 1: {"route": [(0, 0), (m - 1, 0)]},
    2: {"route": [(m - 1, 0), (m - 1, n - 1)]},
    3: {"route": [(m - 1, n - 1), (0, n - 1)]},
    4: {"route": [(0, n - 1), (0, n - 2)]},
    "a.1": {"route": [(0, n - 2), (m - 2, n - 2)]},
    "b.1": {"route": [(m - 2, n - 2), (m - 2, n - 3)]},
    "c.1": {"route": [(m - 2, n - 3), (0, n - 3)]},
    "d.1": {"route": [(0, n - 3), (0, n - 4)]},
    "a.2": {"route": [(0, n - 4), (m - 2, n - 4)]},
    "b.2": {"route": [(m - 2, n - 4), (m - 2, n - 5)]},
    "c.2": {"route": [(m - 2, n - 5), (0, n - 5)]},
    "d.2": {"route": [(0, n - 5), (0, n - 6)]},
    5: {"route": [(0, n - 6), (0, 0)]},
    6: {"route": [(0, 0), (1, 0)]},
    "I.1": {"route": [(1, 0), (1, 1)]},
    "II.1": {"route": [(1, 1), (2, 1)]},
    "III.1": {"route": [(2, 1), (2, 0)]},
    "IV.1": {"route": [(2, 0), (3, 0)]},
    "7 & 8": {"route": [(3, 0), (3, 1)]},
    9: {"route": [(3, 0), (4, 0)]}
}

draw_hamilton_cycle(base_net_graph, pos, construction, axs[1])
axs[1].set_xlabel(f"Horizontal axis, $n = {n}$", fontsize=20)
axs[1].set_ylabel(f"Vertical axis, $m = {m}$", fontsize=20)

for i in range(2):
    axs[i].set_frame_on(False)
    label = "abcdefgh"[i]
    axs[i].set_title(f"({label})", loc='left', y=1, size=25)  # Use set_title to display the label

    # axpos = axs[i].get_position()  # Get the original position
    # axpos.x0 += 0.05  # Increase the left start position
    # axs[i].set_position(axpos)  # Set the new position

# Place the legend on the figure
plt.tight_layout()
plt.savefig(
    fr"{graphics_dir}\07_hamilton_grid.png",
    dpi=300)
plt.show()
