# -*- coding: utf-8 -*-
"""
Decorators
"""
from functools import wraps
from datetime import datetime, timedelta
from threading import Lock
import logging
from presence_analyzer.helpers import generate_cache_key

log = logging.getLogger(__name__)  # pylint: disable=C0103


def cache(time=60*60):
    """
    Cache in local mem for given time
    """

    # structure:
    #   indexes are generated keys
    #   value is dict: {'valid_till': <datetime.datetime>, 'data': <dict>}
    cached_data = {}

    def decorator(func):

        @wraps(func)
        def wrapped_function(*args, **kwargs):
            """ Wrapper """
            key = generate_cache_key(func, args, kwargs)

            refresh_key = (
                key not in cached_data or
                (cached_data[key]['valid_till']-datetime.now()).seconds <= 0
            )
            if refresh_key:
                log.debug('Refreshing cache for %s' % key)
                lock = Lock()
                with lock:
                    cached_data[key] = {
                        'valid_till': datetime.now()+timedelta(seconds=time),
                        'data': func(*args, **kwargs)
                    }
            else:
                log.debug('Retrieving from cache %s' % key)

            return cached_data[key]['data']

        return wrapped_function

    return decorator
