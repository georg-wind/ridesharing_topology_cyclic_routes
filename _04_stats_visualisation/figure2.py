def create_figure2(*args, **kwargs):
    print("create_figure2 not implemented.")
    pass
### FIGURE 2 ### something is off here atm
# fig, ax = plt.subplots()

# # 1. Number of visits to a node over 100 requests
# avg_time_between_N_requests = x_arr # this is wrong!
# visits_to_node_per_N_reqs = np.multiply(avg_time_between_N_requests, stats_df.loc["node_visit_frequency_arr_50"])
# ax.plot(x_arr, visits_to_node_per_N_reqs, ":", color="orange", label=
# "(1) LEFT: stops at a specific node over the time of N requests being generated [simulation] - median (shaded: 1st "
# "& 3rd "
# "quantiles)")

# ax.fill_between(x_arr, np.multiply(avg_time_between_N_requests, stats_df.loc["node_visit_frequency_arr_25"]),
#                 np.multiply(avg_time_between_N_requests, stats_df.loc["node_visit_frequency_arr_75"]),
#                 color="orange", alpha=0.2)

# expected_avg_no_pickups_dropoffs_per_stop = np.divide(stats_df.loc["n_arr"], n_nodes_total)

# # ax2 = ax.twinx()
# # ax2.plot(x_arr, avg_time_between_N_requests, "--", color="blue", label="RIGHT: avg time between N requests (2 * l_avg * N / x)")

# ax.plot(x_arr, stats_df.loc["hops_at_visit_arr"], "--", color="blue", label="(2) avg. no of hop-on/-offs at each "
#                                                                               "stop [simulation] - mean")

# ax.plot(x_arr, expected_avg_no_pickups_dropoffs_per_stop, "--", color="purple",
#         label="(3) E(avg. no of hop-on/-offs at each stop | (conditionality neglected!)) [stochastics]: n / N")

# ax.plot(x_arr, np.multiply(stats_df.loc["hops_at_visit_arr"], visits_to_node_per_N_reqs), "--", color="green", 
#         label="(4): (1) * (2)")

# delta_t = 1
# ax.plot(x_arr, np.divide(stats_df.loc["hops_at_visit_arr"], delta_t), ":", color="green",
#         label="(5): hop-on/-offs served per delta t = 1")

# ax.set_xlabel('x')
# # ax.set_ylabel('visits')
# # ax2.set_ylabel('delta t')

# fig.legend(fontsize=8, loc="upper left")
# fig.savefig(f'./data/plots/figure_2_{topology}_{mode}_maxx_{sub_range[-1]}_nreq_{n_reqs}.svg', bbox_inches='tight')