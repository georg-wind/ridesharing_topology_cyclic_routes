import pickle
import glob
import sys


if __name__ == '__main__':
    topology = sys.argv[1]
    if topology.endswith('/'):
        topology = topology[:-1]
    # search for pickles in ./<topology>
    print(f"searcing for pickles in {topology}/")
    result = dict()
    for single_pickle in glob.glob(f"./{topology}/*.pkl"):
        with open(single_pickle, 'rb') as f:
            data = pickle.load(f)
        result.update(data)
    # now result is the combined data. Save it
    big_pickle_path = f"./{topology}.pkl"
    with open(big_pickle_path, 'wb') as f:
        pickle.dump(result, f)
