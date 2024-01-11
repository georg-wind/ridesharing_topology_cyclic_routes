import hashlib
import os
import pickle
import time
import zlib
from collections.abc import Iterable
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()
username = os.environ.get('MONGO_DB_USERNAME')
password = os.environ.get('MONGO_DB_PASSWORD')
dbname = os.environ.get('MONGO_DB_NAME')
cluster_url = os.environ.get('MONGO_DB_CLUSTER_URL')

uri = f"mongodb+srv://{username}:{password}@{cluster_url}/{dbname}?retryWrites=true&w=majority"

# ## delete all data in the collection
# client = MongoClient(uri, server_api=ServerApi('1'))
# client.admin.command('ping')
# db = client[dbname]
# wrapper_collected_data_collection = db["wrapper_collected_data_collection"]
# result = wrapper_collected_data_collection.delete_many({}) 
# print(result)

def is_simple_type(obj):
    # Define simple types that don't need to be separated
    simple_types = (int, float, str, bool)
    return isinstance(obj, simple_types)


def custom_serializer(obj):
    return zlib.compress(pickle.dumps(obj))


def custom_deserializer(data):
    return pickle.loads(zlib.decompress(data))


def cache_to_mongodb(collection_name="wrapper_collected_data_collection"):
    # Access your database
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        db = client[dbname]
    
        # Access a collection (similar to a table in relational databases)
        collection = db[collection_name]
    except Exception as e:
        print(e)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            arg_names = [arg if is_simple_type(arg) else repr(arg) for arg in args]
            kwarg_names = [value if is_simple_type(value) else key for key, value in kwargs.items()]

            # Create a unique key based on the function's name and its arguments
            key = hashlib.sha256(pickle.dumps((func.__name__, args, kwargs))).hexdigest()

            # Check if the result is already cached, if so, load and return it
            try:
                start_time = time.time()
                cached_results = list(collection.find({'parent_key': key}).sort('index', 1))
                if cached_results:
                    return getting_cached_result(cached_results, start_time)
            except Exception as e:
                print(e)
            # Run the actual function
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Cache the result
            try:
                print(f"Adding result for function {func.__name__} to MongoDB")
                if isinstance(result, Iterable) and not isinstance(result, (str, bytes)) and not all(
                        is_simple_type(item) for item in result):
                    # Cache each item in the iterable separately
                    cache_entries = [{
                        '_id': hashlib.sha256(pickle.dumps((key, index))).hexdigest(),
                        'parent_key': key,
                        'index': index,
                        'function_name': func.__name__,
                        'args': arg_names,
                        'kwargs': kwarg_names,
                        'result': custom_serializer(item),
                        'timestamp': datetime.utcnow(),
                        'execution_time': execution_time,
                        'is_separated': True,
                        'result_type': type(result).__name__
                    } for index, item in enumerate(result)]
                    collection.insert_many(cache_entries)
                else:
                    # Cache non-iterable results or iterables with simple types normally
                    collection.insert_one({
                        '_id': key,
                        'parent_key': key,
                        'index': 0,
                        'function_name': func.__name__,
                        'args': arg_names,
                        'kwargs': kwarg_names,
                        'result': custom_serializer(result),
                        'timestamp': datetime.utcnow(),
                        'execution_time': execution_time,
                        'is_separated': False
                    })
            except Exception as e:
                print(f"Couldn't add result for function {func.__name__} to MongoDB,"
                      f"got exception {e}.")

            # Return the result
            return result

        return wrapper

    return decorator


def getting_cached_result(cached_results, start_time):
    is_separated = cached_results[0].get('is_separated', False)

    if is_separated:
        # Reconstruct the result from cached results
        result_type = cached_results[0]['result_type']
        result_elements = [custom_deserializer(res['result']) for res in cached_results]
        if result_type == 'list':
            result = list(result_elements)
        elif result_type == 'tuple':
            result = tuple(result_elements)
        else:
            raise ValueError(f"Not implemented result type: {result_type} for result-retrieval (MongoDB-caching).")

    else:
        result = custom_deserializer(cached_results[0]['result'])

    loading_cached_result_execution_time = time.time() - start_time
    saved_time = cached_results[0]['execution_time'] - loading_cached_result_execution_time
    print(f"Using cached result. Saved time: {saved_time} s")
    return result
