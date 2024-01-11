# https://matplotlib.org/stable/users/prev_whats_new/dflt_style_changes.html#colors-color-cycles-and-colormaps
def topo_color(topology):
    if "line" in topology:
        return "C9"
    elif "cycle" in topology:
        return "C2"
    elif "star" in topology:
        return "C6"
    elif "wheel" in topology:
        return "C0"
    elif "grid" in topology:
        return "C1"
    elif "route" in topology:
        return "C3"
    # else
    else:
        return "C7"

def n_marker(N):
    N = int(N)
    if N <= 5:
        return "o" #circle
    elif N <= 10:
        return "v" # triangle_down
    elif N <= 25:
        return "P" # plus(filled)
    elif N <= 50:
        return "X" # x(filled
    elif N <= 100:
        return "D" # diamond
    else:
        return "s" # square
