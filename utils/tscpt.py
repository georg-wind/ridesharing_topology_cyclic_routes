def tscpt_by_topo(topology):
    graph_type, N = topology.split('_')
    N = int(N)
    if any(hamiltontype in topology for hamiltontype in ["grid", "wheel", "cycle"]):
        tscpt = N
        if graph_type == "grid" and (tscpt % 2) != 0:
            tscpt = N + 1/(N - 1) - 5/(2*N) + 1
    elif graph_type == "line":
        tscpt = 4*N/3 - 2/3
    elif graph_type == "star":
        tscpt = 2*N - 4 + 4/N
    else:
        tscpt = N

    return tscpt
