import os
import re

def get_all_x(topology, mode, function):
    # Define the root directory to start the search
    root_directory = "./data/"

    # Pattern to match the filenames. Assumes `x` is a number in the filename.
    pattern = f"{topology}_{mode}_([0-9]+(?:\.[0-9]+)?)_{function}\.dill"

    # Initialize an empty list to store matched filenames
    filelist = []

    # Walk through the directory and its subdirectories
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            if re.match(pattern, filename):
                filelist.append(os.path.join(dirpath, filename))

    if filelist == []:
        print("No files found during get_all_x. Please check root-directory setting! (.. or . sometimes relevant diff)")
    # Extract the 'x' value from each filename
    xrange = [re.search(pattern, filename).group(1) for filename in filelist]

    # Convert extracted 'x' values to float
    xrange = [float(x) for x in xrange]
    # make sure values are unique
    xrange = set(xrange)
    xrange = list(xrange)

    # Sort them in ascending order
    xrange = sorted(xrange)

    return xrange
