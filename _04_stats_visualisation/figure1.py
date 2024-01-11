import matplotlib.pyplot as plt
import numpy as np

from utils import graph_constructor


def create_figure1(x_arr, topology, mode, n_reqs, stats_df):
    base_net_graph = graph_constructor(topology)
    n_nodes_total = len(base_net_graph.nodes())

    ####### FIGURE 1 #######
    fig, ax = plt.subplots()
    ax.set_ylim(0, n_nodes_total * 1.5)

    # 1. Service Time
    ax.plot(x_arr, stats_df.loc["s_t_arr_50"], color="blue", label="t_s: service time [simulation] - median (shaded: "
                                                                   "1st "
                                                                   "& 3rd quantiles)")

    # ax.plot(x_arr, stats_df.loc["s_t_arr_mean"], color="lightblue", label="t_s: service time [simulation] - mean")
    ax.fill_between(x_arr, stats_df.loc["s_t_arr_25"], stats_df.loc["s_t_arr_75"], color="blue", alpha=0.2)

    # # 2. Stop-list length
    ax.plot(x_arr, stats_df.loc["n_arr"], "--", color="purple", label="n: stop-list length [simulation]")

    # 4. Route Volume
    ax.plot(x_arr, stats_df.loc["route_vol_arr"], "--", color="yellow", label="vol: route-volume [simulation]")

    # 5.1 unique nodes in stoplist - simulation results
    ax.plot(x_arr, stats_df.loc["mean_unique_stoplist_length"], "--", color="green", label="no. unique stops in "
                                                                                           "stoplist "
                                                                                           "[simulation]")

    # 5.2 unique nodes in stoplist - expected (stochastically)
    # https://stats.stackexchange.com/a/296053  n[1−((n−1)/n)**k]
    # but NB: stops are drawn at random but whether they are still no a list where the continuous 
    # drawings are random but the dropouts are not, is not an overall random process
    expected_unique_stops_stoplist_arr = n_nodes_total * (
            1 - (np.power((n_nodes_total - 1) / n_nodes_total, stats_df.loc["n_arr"])))

    ax.plot(x_arr, expected_unique_stops_stoplist_arr, ",", color="green", label="E(unique stops in stoplist | n) ["
                                                                                 "stochastics]: n * [1 − ((n−1) / "
                                                                                 "n)^k]")
    del expected_unique_stops_stoplist_arr

    # 3. Bus and taxi
    ax.plot(x_arr, [n_nodes_total for _ in x_arr], ",", color="red", label="avg. service time public transport bus "
                                                                           "visiting all nodes")

    ax.set_xlabel('request rate parameter x')
    fig.legend(fontsize=8, loc="upper left")
    fig.savefig(f'./data/plots/figure_1_{topology}_{mode}_maxx_{x_arr[-1]}_nreq_{n_reqs}.svg', bbox_inches='tight')
    plt.close()
    print("Figure 1 created and saved.")
