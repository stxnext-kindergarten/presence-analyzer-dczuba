# -*- coding: utf-8 -*-
"""
Helper functions used in templates.
"""


def generate_cache_key(func, args, kwargs):
    """
    Returns key used in cache
    """
    return '%s.%s:%s:%s' % (func.__module__, func.__name__, args.__hash__(),
                            frozenset(kwargs.items()).__hash__())
