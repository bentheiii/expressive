from functools import lru_cache, partial, singledispatch
from itertools import filterfalse, takewhile, groupby, dropwhile

try:
    from functools import cache
except ImportError:
    cache = None

try:
    from functools import cached_property
except ImportError:
    cached_property = None

from expressive.single import e

__all__ = ['classmethod_e',
           'dropwhile_e',
           'filter_e', 'filterfalse_e',
           'groupby_e',
           'list_sort_e', 'lru_cache_e',
           'map_e', 'max_e', 'min_e',
           'partial_e', 'property_e',
           'singledispatch_e', 'singledispatch_register_e', 'sorted_e',
           'takewhile_e']

if cache:
    __all__.append('cache_e')

    def cache_e(expression):
        return cache(e(expression))

if cached_property:
    __all__.append('cached_property_e')

    def cached_property_e(expression):
        return cached_property(e(expression))


def classmethod_e(expression):
    return classmethod(e(expression))


def dropwhile_e(expression, *args, **kwargs):
    return dropwhile(e(expression), *args, **kwargs)


def filter_e(expression, *args, **kwargs):
    return filter(e(expression), *args, **kwargs)


def filterfalse_e(expression, *args, **kwargs):
    return filterfalse(e(expression), *args, **kwargs)


def groupby_e(iterable, expression):
    return groupby(iterable, e(expression))


def list_sort_e(self: list, *, key, **kwargs):
    return self.sort(key=e(key), **kwargs)


def _lru_cache_inner(exp, *args, **kwargs):
    return lru_cache(*args, **kwargs)(e(exp))


def lru_cache_e(maxsize=128, *args, **kwargs):
    if isinstance(maxsize, int):
        return lambda x: _lru_cache_inner(x, *args, maxsize=maxsize, **kwargs)
    return _lru_cache_inner(maxsize)


def map_e(expression, *args, **kwargs):
    return map(e(expression), *args, **kwargs)


def max_e(*args, key, **kwargs):
    return max(*args, key=e(key), **kwargs)


def min_e(*args, key, **kwargs):
    return min(*args, key=e(key), **kwargs)


def partial_e(expression, arg):
    return partial(e(expression), arg)


def property_e(get_expression, doc=None):
    return property(fget=e(get_expression), doc=doc)


def singledispatch_e(expression):
    return singledispatch(e(expression))


def singledispatch_register_e(self, cls, expression=None):
    def ret(expression):
        return self.register(cls, e(expression))

    if expression is None:
        return ret
    return ret(expression)


def sorted_e(*args, key, **kwargs):
    return sorted(*args, key=e(key), **kwargs)


def takewhile_e(expression, *args, **kwargs):
    return takewhile(e(expression), *args, **kwargs)
