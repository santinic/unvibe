import os
import pickle

from unvibe.config import config_get_or

cache_file = 'unvibe_cache.pkl'


def disk_cached(func):
    if config_get_or('search', 'cache', True) is False:
        return func

    def wrapper(*args, **kwargs):
        key = f"{func.__name__}_{args}_{kwargs}"

        # Create cache file if it doesn't exist
        if not os.path.exists(cache_file):
            with open(cache_file, 'wb') as f:
                pickle.dump({}, f)

        # Read existing cache
        with open(cache_file, 'rb') as f:
            cache = pickle.load(f)

        # Check if result is cached
        if key in cache:
            return cache[key]

        # Compute result
        result = func(*args, **kwargs)

        # Store result in cache
        cache[key] = result
        with open(cache_file, 'wb') as f:
            pickle.dump(cache, f)

        return result

    return wrapper


def reset_cache():
    if os.path.exists(cache_file):
        os.remove(cache_file)


def get_keys():
    if not os.path.exists(cache_file):
        return set()

    with open(cache_file, 'rb') as f:
        cache = pickle.load(f)

    return set(cache.keys())
