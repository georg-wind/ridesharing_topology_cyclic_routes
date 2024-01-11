import matplotlib.pyplot as plt
import numpy as np


def create_figure3(x_arr, topology, mode, n_reqs, stats_df):
    ### FIGURE 3 ###
    fig, ax = plt.subplots()
    ax.plot(x_arr,
            stats_df.loc["node_visit_frequency_arr_mean"],
            ":", color="blue", label="Mean node-visit frequencies over time (shaded "
                                     "area: +/- 1SD)")

    ax.fill_between(x_arr,
                    np.add(stats_df.loc["node_visit_frequency_arr_mean"],
                           stats_df.loc["node_visit_frequency_arr_std"]),
                    np.subtract(stats_df.loc["node_visit_frequency_arr_mean"],
                                stats_df.loc["node_visit_frequency_arr_std"]),
                    color="blue",
                    alpha=0.2)

    ax2 = ax.twinx()

    ax2.plot(x_arr, stats_df.loc["node_visit_frequency_arr_mean_of_individual_stds"], ":", color="orange",
             label="Mean of node-level standard-deviations of node-visit frequency over time (shaded "
                   "area: +/- 1SD")

    ax2.fill_between(x_arr, np.add(stats_df.loc["node_visit_frequency_arr_mean_of_individual_stds"], stats_df.loc[
        "node_visit_frequency_arr_std_of_individual_stds"]),
                     np.subtract(stats_df.loc["node_visit_frequency_arr_mean_of_individual_stds"], stats_df.loc[
                         "node_visit_frequency_arr_std_of_individual_stds"]),
                     color="orange", alpha=0.2)

    ax.set_xlabel('x')
    ax.set_ylabel('mean of avg. node visit frequencies')
    ax2.set_ylabel('mean of SDs of node visit frequencies')

    fig.legend(fontsize=8, loc="upper left")
    fig.savefig(f'./data/plots/figure_3_{topology}_{mode}_maxx_{x_arr[-1]}_nreq_{n_reqs}.svg', bbox_inches='tight')
    plt.close()
    print("Figure 3 created and saved.")
