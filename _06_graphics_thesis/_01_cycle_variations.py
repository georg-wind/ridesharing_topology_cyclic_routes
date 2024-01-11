import matplotlib.lines as mlines
import matplotlib.offsetbox as offsetbox
import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image

from utils import graph_constructor, topo_color, graphics_dir


def draw_highlighted_edges(G, pos, plot_highlighting, ax, icon):
    color_route = topo_color("route")
    color_cycle = '#f8f01d'
    color_cycle_nodes = '#f8cc1d'
    color_topology = topo_color("wheel")

    """ Draw highlighted edges with shaded area. """
    routeedges = plot_highlighting["route"]
    cycleedges = plot_highlighting["cycle"]
    route_nodes = [edge[0] for edge in routeedges]
    cycle_nodes = [edge[0] for edge in cycleedges]
    start_node = routeedges[0][0]
    route_nodes.remove(start_node)

    # Draw all edges with base color
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='black')
    nx.draw_networkx_nodes(G, pos=pos, ax=ax, node_color=color_topology, node_size=40)

    # CYCLE-Nodes
    nx.draw_networkx_nodes(G, pos=pos, ax=ax, nodelist=[node for node in cycle_nodes if node != start_node],
                           node_color=color_cycle_nodes,
                           node_size=120)
    if start_node in cycle_nodes:
        nx.draw_networkx_nodes(G, pos=pos, ax=ax, nodelist=[start_node], node_color=color_cycle_nodes,
                               node_size=150, node_shape='s')

    # ROUTE
    nx.draw_networkx_edges(G, pos, edgelist=routeedges, ax=ax, edge_color=color_route,
                           arrows=True, arrowstyle="-|>",
                           arrowsize=20)

    nx.draw_networkx_nodes(G, pos=pos, ax=ax, nodelist=[node for node in route_nodes if node in cycle_nodes],
                           node_color=color_route,
                           node_size=50)
    nx.draw_networkx_nodes(G, pos=pos, ax=ax, nodelist=[node for node in route_nodes if node not in cycle_nodes],
                           node_color=color_route,
                           node_size=120)

    # make the first node of the route a square
    nx.draw_networkx_nodes(G, pos=pos, ax=ax, nodelist=[start_node], node_color=color_route,
                           node_size=80, node_shape='s')

    # first_edge = plot_highlighting["route"][0]
    # x1, y1 = pos[first_edge[0]]
    # icon = icon.resize((35, 35))  # Resizing the icon
    # icon = icon.rotate(-90)  # Rotating the icon
    # imagebox = offsetbox.AnnotationBbox(offsetbox.OffsetImage(icon), (x1 + 0.1, y1 - 0.6), frameon=False)
    # ax.add_artist(imagebox)

    edge_labels = {routeedges[i]: str(i + 1) for i in range(len(routeedges))}
    nx.draw_networkx_edge_labels(G, pos, ax=ax, edge_labels=edge_labels, font_size=25,
                                 font_color=color_route, rotate=False)

    # CYCLE-edges
    nx.draw_networkx_edges(G, pos, edgelist=cycleedges, ax=ax, edge_color=color_cycle, connectionstyle="arc3,rad=0.06",
                           arrows=True, arrowstyle="-", alpha=0.4, width=12)


# Define the base graph and positions
base_net_graph = graph_constructor("wheel_5")
pos = {0: (0, 0), 1: (-1, 1), 2: (1, 1), 3: (1, -1), 4: (-1, -1)}

# Define routes to highlight on each graph
plot_highlighting = {
    1: {"route": [(1, 4), (4, 3), (3, 2), (2, 1)],
        "cycle": [(1, 2), (2, 3), (3, 4), (4, 1)]},

    2: {"route": [(1, 4), (4, 3), (3, 2), (2, 0), (0, 1)],
        "cycle": [(1, 0), (0, 2), (2, 3), (3, 4), (4, 1)]},

    3: {"route": [(1, 4), (4, 0), (0, 3), (3, 2), (2, 0), (0, 1)],
        "cycle": [(0, 3), (3, 2), (2, 0)]},

    4: {"route": [(1, 4), (4, 0), (0, 3), (3, 2), (2, 0), (0, 1)],
        "cycle": [(1, 4), (4, 0), (0, 3), (3, 2), (2, 0), (0, 1)]}
}

bus_icon = Image.open('notUsed/icons8-bus-50.png')

# Create a figure with 4 subplots
fig, axs = plt.subplots(1, 4, figsize=(18, 4))
# ad legend to the figure

plt.subplots_adjust(left=0.18, wspace=0.08)  # Adjust these parameters as needed

# Plot each graph
for i in range(4):
    axs[i].set_frame_on(False)
    label = "abcdefgh"[i]
    axs[i].set_title(f"({label})", loc='left', y=1, size=25)  # Use set_title to display the label
    draw_highlighted_edges(base_net_graph, pos, plot_highlighting[i+1], axs[i], icon=bus_icon)
    # axpos = axs[i].get_position()  # Get the original position
    # axpos.x0 += 0.05  # Increase the left start position
    # axs[i].set_position(axpos)  # Set the new position

# Create custom legend handles and labels
route_handle = mlines.Line2D([], [], color='#fa8767', label='Route')
cycle_handle = mlines.Line2D([], [], color='#f8f01d', label='"Cycle"', alpha=0.4, linewidth=8)
# bus_icon_handle = mlines.Line2D([], [], color='black', marker='o', markersize=10, label='ODRS-vehicle')

# Place the legend on the figure
fig.legend(handles=[route_handle, cycle_handle], loc='center left', fontsize=30)
plt.tight_layout(rect=(0.16, 0, 1, 1))
plt.savefig(
    fr"{graphics_dir}\01_cycle_variations.png",
    dpi=300)
plt.show()
