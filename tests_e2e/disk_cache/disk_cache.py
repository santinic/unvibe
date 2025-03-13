from typing import Set

from unvibe import ai


@ai
def disk_cache():
    """
    @disk_cache is a decorator that caches the return value of a function to a file on disk cache_file.
    cache_file will be used for all functions.
    Save the keys in the cache_file as function_name_args_kwargs"""
    pass


@ai
def get_keys() -> Set[str]:
    """this function returns all the keys in cache_file"""
    pass
