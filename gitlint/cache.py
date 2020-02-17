class PropertyCache(object):
    """ Mixin class providing a simple cache. """

    def __init__(self):
        self._cache = {}

    def _try_cache(self, cache_key, cache_populate_func):
        """ Tries to get a value from the cache identified by `cache_key`.
            If no value is found in the cache, do a function call to `cache_populate_func` to populate the cache
            and then return the value from the cache. """
        if cache_key not in self._cache:
            cache_populate_func()
        return self._cache[cache_key]


def cache(original_func=None, cachekey=None):
    """ Cache decorator. Caches function return values.
        Requires the parent class to extend and initialize PropertyCache.
        Usage:
            # Use function name as cache key
            @cache
            def myfunc(args):
                ...

            # Specify cache key
            @cache(cachekey="foobar")
            def myfunc(args):
                ...
    """

    # Decorators with optional arguments are a bit convoluted in python, especially if you want to support both
    # Python 2 and 3. See some of the links below for details.

    def cache_decorator(func):

        # If no specific cache key is given, use the function name as cache key
        if not cache_decorator.cachekey:
            cache_decorator.cachekey = func.__name__

        def wrapped(*args):
            def cache_func_result():
                # Call decorated function and store its result in the cache
                args[0]._cache[cache_decorator.cachekey] = func(*args)
            return args[0]._try_cache(cache_decorator.cachekey, cache_func_result)

        return wrapped

    # Passing parent function variables to child functions requires special voodoo in python2:
    # https://stackoverflow.com/a/14678445/381010
    cache_decorator.cachekey = cachekey  # attribute on the function

    # To support optional kwargs for decorators, we need to check if a function is passed as first argument or not.
    # https://stackoverflow.com/a/24617244/381010
    if original_func:
        return cache_decorator(original_func)

    return cache_decorator
