import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from matplotlib.lines import Line2D

from _06_motif_case_study_utils import heatmap, annotate_heatmap
from utils import pickle_loader, topo_color, casestudy_params, graph_constructor, graphics_dir

# motif plotting params
n_motifs = 6
spmode = "all_volume_info"

# dist-plot params
max_len_sorted_motifs = casestudy_params["max_len_sorted_motifs"]

for topology, xlist in casestudy_params["topologies"].items():
    graph_type, N = topology.split('_')
    #0. load data
    print(f"Plotting {topology}")
    topocolor = topo_color(topology)

    pickle_path = f'./data/03_casestudy/{topology}_{spmode}_{str(sum(xlist))}_casestudy_motif_frequs.dill'
    sorted_maxx_motifs, motiffrequencydict = pickle_loader(pickle_path)

    # 1. plot motifs
    motifs_to_plot = sorted_maxx_motifs[:n_motifs]

    base_net_graph = graph_constructor(topology)
    pos = nx.get_node_attributes(base_net_graph, 'pos')
    if topology == "wheel_5":
        pos = {0: (0, 0), 1: (-1, 1), 2: (1, 1), 3: (1, -1), 4: (-1, -1)}

    # Get all edge frequencies to determine the range of the colormap
    all_edge_frequencies = [data['edge_frequency'] for motif in motifs_to_plot for u, v, data in
                            motif['graph'].edges(data=True)]

    for i, motif in enumerate(motifs_to_plot):
        print("Plotting motif ", i)
        fig, ax = plt.subplots(figsize=(8, 8))

        # draw_highlighted_edges(G, pos, plot_highlighting, ax, icon):
        color_cycle = '#f8f01d'
        color_cycle_nodes = '#f8cc1d'

        # """ Draw highlighted edges with shaded area. """
        # routeedges = plot_highlighting["route"]
        # cycleedges = plot_highlighting["cycle"]
        # route_nodes = [edge[0] for edge in routeedges]
        # cycle_nodes = [edge[0] for edge in cycleedges]
        # start_node = routeedges[0][0]
        # route_nodes.remove(start_node)

        # Draw all edges with base color
        nx.draw_networkx_edges(base_net_graph, pos, ax=ax, edge_color="black", width=5)
        nx.draw_networkx_nodes(base_net_graph, pos=pos, ax=ax, node_color="black", node_size=400)

        # Draw nodes
        nx.draw_networkx_nodes(motif["graph"], pos=pos, ax=ax, node_color=color_cycle_nodes, node_size=500)
        # Draw curved edges without arrow heads
        ##


        for j in range(max(all_edge_frequencies)):
            # color = ['#f8f01d', '#fab416', '#fc780e', '#fd3c07', '#ff0000'][j]
            color = ['#f8f01d', '#fc780e', '#fd3c07', '#ff0000'][j]
            edgelist = [(u, v) for u, v, data in motif['graph'].edges(data=True) if data['edge_frequency'] == j+1]
            nx.draw_networkx_edges(motif["graph"], pos=pos, ax=ax, edge_color=color, connectionstyle="arc3,rad=0.1",
                                   arrows=True, arrowstyle='-',
                                   edgelist=edgelist, alpha=0.8, width=40)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        fig.tight_layout()
        plt.savefig(
            fr"{graphics_dir}\casestudy_{topology}\motif_{i}.png",
            dpi=300)
        # plt.show()
        plt.close()

    # 2. plot heatmap
    heatmap_prep_dict = {
        f"$x = {xlist[0]:.2f}$\n $t_s(x) \\lesssim t_s^{{taxi}}$": motiffrequencydict[str(xlist[0])][:n_motifs],
        f"$x = {xlist[1]:.2f}$\n $efficient\ odrs$": motiffrequencydict[str(xlist[1])][:n_motifs],
        f"$x = {xlist[2]:.2f}$\n $t_s(x) \\approx t_s^{{cpt}}$": motiffrequencydict[str(xlist[2])][:n_motifs],
        f"$x = {xlist[3]:.2f}$\n $\\frac{{\\delta t_s(x)}}{{\\delta x}} \\approx 0$": motiffrequencydict[str(xlist[3])][:n_motifs],
        f"$x = {xlist[4]:.2f}$\n $\lim_{{x \\to \infty}} t_s(x) = t_s^{{cpt, +}}$": motiffrequencydict[str(xlist[4])][:n_motifs]
    }
    df = pd.DataFrame(heatmap_prep_dict)

    # Transpose the DataFrame so that keys become the row indices
    df = df.T

    # we want a structure with two rows and the second row having n_motif columns
    fig, ax = plt.subplots(figsize=(8, 8))

    row_labels = list(df.index)
    col_labels = [f"\makecell{{\insertfig{{{i}}} \\\\ Motif ${i + 1}$ [\%]}}" for i in range(n_motifs)]

    if topology == "wheel_5":
        vmax = 0.2
    elif topology == "grid_16":
        vmax = 0.02
    elif topology == "cycle_10":
        vmax = 0.06

    im, _ = heatmap(df, row_labels, topology, ax=ax,
                    cmap="viridis", vmin=0, vmax=vmax,  # set this to 1 if this leads to problems
                    cbarlabel="")

    def func(x, pos):
        return f"{x:.3f}".replace("0.", ".").replace("1.00", "")

    annotate_heatmap(im, textcolors=("black", "black"),
                     valfmt=matplotlib.ticker.FuncFormatter(func), size=12)

    colors = ['#f8f01d', '#fc780e', '#fd3c07', '#ff0000']

    line1 = Line2D([0], [0], linestyle='-', color=colors[0], label='1', alpha=0.8)
    line2 = Line2D([0], [0], linestyle='-', color=colors[1], label='2',
                   alpha=0.8)
    # Set the line width
    line1.set_linewidth(5)
    line2.set_linewidth(5)
    legend = ax.legend(handles=[line1, line2], fontsize=10, loc="upper right", bbox_to_anchor=(0, 0),
                       frameon=True, title="No. edge-traversals")

    plt.xlabel("6 most frequent motifs for large x", fontsize=12, labelpad=65)
    plt.title(f"relative motif-frequencies in cycles driven on {graph_type}-{N}", fontsize=12, pad=20)

    plt.tight_layout()
    plt.savefig(fr"{graphics_dir}\casestudy_{topology}\heatmap.png",
            dpi=300)
    plt.show()
    plt.close()
