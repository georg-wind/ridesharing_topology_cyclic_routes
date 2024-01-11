import hashlib
import os
import pickle
import sys
from functools import wraps

import dill


def save2pickle(data, pickle_path):
    if pickle_path[-4:] == "dill":
        with open(pickle_path, 'wb') as f:
            print("Saving pickle, don't interrupt!")
            dill.dump(data, f)
            print("Pickle saved.")
    else:
        with open(pickle_path, 'wb') as f:
            print("Saving pickle, don't interrupt!")
            pickle.dump(data, f)
            print("Pickle saved.")


def pickle_loader(pickle_path):
    if pickle_path[-4:] == "dill":
        with open(pickle_path, 'rb') as f:
            result = dill.load(f)
    else:
        with open(pickle_path, 'rb') as f:
            result = pickle.load(f)
    return result


def run_or_get_pickle(ext_identifier, data_folder="pickles"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            base_path = f"./data/{data_folder}/"
            if not os.path.exists(base_path):
                os.makedirs(base_path)
                print(f"Folder '{base_path}' created.")

            dill_path = f"{base_path}{ext_identifier}_{func.__name__}.dill"
            if os.path.exists(dill_path):
                print(f"{dill_path} path exists, returning pickle.")
                return pickle_loader(dill_path)
            else:
                result = func(*args, **kwargs)
                save2pickle(result, dill_path)
                return result

        return wrapper

    return decorator



def estimate_size(obj):
    """
    Estimate the size of an object in bytes (basic implementation).
    """
    try:
        return sys.getsizeof(obj)
    except TypeError:
        return len(str(obj))  # Fallback for objects that don't support getsizeof


def generate_hash(args, kwargs, size_threshold=1024):
    """
    Generate a hash for a function call, considering only arguments smaller than size_threshold.
    """
    hasher = hashlib.sha256()

    # Process args
    for arg in args:
        if estimate_size(arg) <= size_threshold:
            hasher.update(hashlib.sha256(str(arg).encode()).digest())
        else:
            # For large objects, use a placeholder in the hash
            hasher.update(f"large_object_{type(arg)}".encode())

    # Process kwargs
    for key, value in kwargs.items():
        if estimate_size(value) <= size_threshold:
            hasher.update(hashlib.sha256(str(value).encode()).digest())
        else:
            hasher.update(f"large_object_{key}_{type(value)}".encode())

    return hasher.hexdigest()
