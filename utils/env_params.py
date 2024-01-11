import numpy as np

topologies = ["line_5", "line_10", "line_16", "line_100",
              "star_5", "star_10", "star_16", "star_100",
              "cycle_5", "cycle_10", "cycle_16", "cycle_100",
              "wheel_5", "wheel_10", "wheel_16", "wheel_100",
              "grid_9", "grid_16", "grid_100"]

# We investigated the differences between different shortest path modes - but it did not lead to visible differences in resulting service times
shortest_path_modes = ["all_volume_info"]  # , "staticmin", "staticmax", "originalpaper"]

# the number k of requests to simulate
# numreqs = 1 * 10 ** 5
# only used for wheel 16 and grids 9 and 16
numreqs = 1 * 10 ** 6


# the topology-adjusted request rates x simulated
# as our computational capacities are limited, we incremently adjusted the ranges and preserve the values we actually used.
# It can be easily reduced.

xrange_1 = [0.1, 39.9, 39]
x_arr_1 = list(np.linspace(*xrange_1))
xrange_2 = [0.1, 5, 20]
x_arr_2 = list(np.linspace(*xrange_2))
xrange_3 = [39.9, 120, 39]
x_arr_3 = list(np.linspace(*xrange_3))
xrange_4 = [120, 250, 10]
x_arr_4 = list(np.linspace(*xrange_4))
# only used for wheel 16 and grids 9 and 16
xrange_5 = [250, 500, 10]
x_arr_5 = list(np.linspace(*xrange_5))
xrange_6 = [500, 1000, 10]
x_arr_6 = list(np.linspace(*xrange_6))

# xrange = x_arr_1 + x_arr_2 + x_arr_3 + x_arr_4
xrange = x_arr_1 + x_arr_2 + x_arr_3 + x_arr_4 + x_arr_5 + x_arr_6

# enter a directory below for the graphics to be saved in
graphics_dir = r"C:\Users\XXXXX\Masterarbeit_Latex\src\fig\graphics"

# casestudy contains dict with format "topology: [x_small, x_good_operation_phase, x_cut_t_s_cpt, x_turning_point, x_asymptotic]
casestudy_params = {
    "topologies": {
        "wheel_5": [x_arr_2[2], x_arr_2[5], x_arr_2[16], x_arr_1[9], x_arr_1[34]],
        "grid_16": [x_arr_2[2], x_arr_2[5], x_arr_2[13], x_arr_1[13], x_arr_1[34]],
        "cycle_10": [x_arr_2[2], x_arr_2[5], x_arr_2[7], x_arr_1[5], x_arr_1[34]]
    },
    "max_len_sorted_motifs": 50
}
