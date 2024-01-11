import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils import pickle_loader


def plot_3d_surface(x, y, z, ax, labels, view_init=(20, -90)):
    ax.plot_surface(x, y, z, cmap='viridis')
    ax.set_xlabel(labels['x'])
    ax.set_ylabel(labels['y'])
    ax.set_zlabel(labels['z'])
    ax.view_init(*view_init)


def create_figure4(topology, mode, x_range, n_reqs, output_dir='./data/plots', data_dir='./data/stats'):
    chunk_size = n_reqs // 100 if n_reqs > 1000 else 10

    pickle_path = os.path.join(data_dir, f'{topology}_{mode}_xfrom_{x_range[0]}_xto_{x_range[1]}_nreq_'
                                         f'{n_reqs}_rolling_{chunk_size}_mean_servicetime.pkl')
    service_time_over_t = pickle_loader(pickle_path)

    x_nt_arr = np.tile(x_range, (n_reqs, 1)).T
    n_xt_arr = pd.DataFrame([list(range(1, n_reqs + 1))] * len(x_range))
    t_xn_arr = pd.DataFrame(service_time_over_t).T

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    labels = {'x': 'x', 'y': 'requests', 'z': f'service time mean over last {chunk_size} requests.'}
    plot_3d_surface(x_nt_arr, n_xt_arr, t_xn_arr, ax, labels)

    output_file = os.path.join(output_dir,
                               f'figure_4_{topology}_{mode}_maxx_{x_range[-1]}_nreq_{n_reqs}_chunk_{chunk_size}.svg')
    fig.savefig(output_file, bbox_inches='tight')
    plt.close()
    print(f"Figure created and saved at {output_file}.")
