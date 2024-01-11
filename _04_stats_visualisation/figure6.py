import matplotlib.pyplot as plt
import numpy as np

from utils import graph_constructor


def create_figure6(x_arr, topology, mode, n_reqs, stats_df, opt_df):
    base_net_graph = graph_constructor(topology)
    n_nodes_total = len(base_net_graph.nodes())

    ####### FIGURE 6 #######
    fig, ax = plt.subplots()
    # ax.set_ylim(0, n_nodes_total * 1.5)

    # 1. Service Time
    ax.plot(x_arr, stats_df.loc["s_t_arr_50"], color="blue", label="avg. service time [simulation] - median (shaded: "
                                                                   "1st "
                                                                   "& 3rd quantiles)")

    # ax.plot(x_arr, stats_df.loc["s_t_arr_mean"], color="lightblue", label="t_s: service time [simulation] - mean")
    ax.fill_between(x_arr, stats_df.loc["s_t_arr_25"], stats_df.loc["s_t_arr_75"], color="blue", alpha=0.2)

    # 5.1 optimality scores
    # we penalize roundtrips visiting few nodes
    opt_b1 = opt_df.loc["opt_b_nodes_mean"] / n_nodes_total

    # we reward roundtrips  visiting nodes on a short paths
    opt_b2 = np.divide(opt_df.loc["opt_b_nodes_mean"] - 1, opt_df.loc["opt_b_edges_mean"])
    optimality_b = np.multiply(opt_b1, opt_b2)
    optimality_c = np.divide(opt_df.loc["opt_b_nodes_mean"], opt_df.loc["opt_b_edges_mean"])

    ax.plot(x_arr, opt_df.loc["opt_a"], "--", color="purple", label="Optimality A: avg. length \"real motifs\"")

    ax.plot(x_arr, opt_df.loc["opt_b_nodes_mean"], "--", color="olivedrab",
            label="B1: avg. no. nodes (unreal motifs) - more is better")

    ax.plot(x_arr, opt_df.loc["opt_b_edges_mean"], "--", color="yellowgreen",
            label="B2: avg. no. edges (unreal motifs) - less is better")

    ax2 = ax.twinx()
    # ax2.plot(x_arr, optimality_b, "--", color="yellow", label="RIGHT: Penalize short round-trips, "
    #                                                           "reward efficiency: \n"
    #                                                           "(B1 / N) * ((B1-1) / B2).")
    ax2.plot(x_arr, optimality_c, "--", color="yellow", label="RIGHT: Nodes / Edges")

    # 3. Bus and taxi
    ax.plot(x_arr, [n_nodes_total for _ in x_arr], ",", color="red",
            label="avg. service time public transport bus "
                  "visiting all nodes")

    ax.set_xlabel('request rate parameter x')
    fig.legend(fontsize=8, loc="upper left")
    fig.savefig(f'./data/plots/figure_6_{topology}_{mode}_maxx_{x_arr[-1]}_nreq_{n_reqs}.svg', bbox_inches='tight')
    plt.close()
    print("Figure 6 created and saved.")
