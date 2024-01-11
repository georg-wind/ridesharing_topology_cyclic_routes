import numpy as np
from collections import Counter


def get_stats_dict(some_list, percentiles=None, freq_counts=False, weights=None):
    # if percentiles is None:
    #     percentiles = [5, 25, 50, 75, 95, 99]
    if freq_counts:
        counts = Counter(some_list)
    if weights:
        some_list = list(np.repeat(some_list, weights))
    try:
        stats_dict = {"mean": np.mean(some_list),
                      "std": np.std(some_list),
                      "min": np.min(some_list),
                      "max": np.max(some_list),
                      "median": np.median(some_list),
                      # "percentiles": {str(p): np.percentile(some_list, p) for p in percentiles},
                      "count": sum(weights) if weights else len(some_list)
                      }
    except ValueError:
        stats_dict = {"mean": 0,
                      "std": 0,
                      "min": 0,
                      "max": 0,
                      "median": 0,
                      # "percentiles": {str(p): 0 for p in percentiles},
                      "count": 0
                      }
        print("get_stats_dict(): Encountered ValueError while trying to generate stats-dict. Returned empty stats dict.")
    if freq_counts:
        stats_dict["counts"] = counts
    return stats_dict
