import numpy as np


def rolling_mean_servicetime(req_data_dict, chunk_size):
    
    n = 10 ** 3

    # Create NumPy arrays for 'dropoff_epoch' and 'req_epoch' for all records
    dropoff_epochs = np.array([record_data["dropoff_epoch"] for record_data in req_data_dict.values()])
    req_epochs = np.array([record_data["req_epoch"] for record_data in req_data_dict.values()])

    # Compute 'service_time' for all records
    service_times = dropoff_epochs - req_epochs

    # Calculate the rolling mean of the downsampled data
    rm_st = np.convolve(service_times, np.ones(chunk_size) / chunk_size, mode='valid')

    # Downsample the data by keeping exactly n data points
    idx = np.round(np.linspace(0, len(rm_st) - 1, n)).astype(int)
    downsampled_service_time = rm_st[idx]

    return downsampled_service_time
