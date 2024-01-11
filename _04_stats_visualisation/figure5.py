import matplotlib.pyplot as plt
from utils import pickle_loader


def create_figure5(service_time_over_t, topology, mode, xrange, n_reqs):
    chunk_size = n_reqs // 100 if n_reqs > 1000 else 10
    ## figure 5

    fig, ax = plt.subplots()

    n_arr = list(range(1, n_reqs//10**3 + 1))

    ax.plot(n_arr, service_time_over_t[xrange[-1]])

    ax.set_xlabel('thsd. requests')
    ax.set_ylabel(f'avg. service time last {chunk_size} requests.')

    # fig.legend(fontsize=8, loc="upper left")
    fig.savefig(f'./data/plots/figure_5_{topology}_{mode}_x_{xrange[-1]}_nreq_{n_reqs}_chunk_{chunk_size}.svg',
                bbox_inches='tight')
    plt.close()
    print("Figure 5 created and saved.")
