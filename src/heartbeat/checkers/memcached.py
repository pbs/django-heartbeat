from django.conf import settings
from collections import OrderedDict
try:
    from django.core.cache import caches
except ImportError:
    from django.core.cache import get_cache as caches


def check(request):
    all_stats = {}
    for cache_profile in settings.CACHES:
        server_stats = []
        cache_backend = get_cache(cache_profile)
        for server, stats in cache_backend._cache.get_stats():
            server_stats.append(OrderedDict(
                details=stats, summary=get_summary(stats), location=server))
        all_stats[cache_profile] = debyteify(server_stats)
    return all_stats


def get_summary(stats):
    return {
        'load': get_width_ratio(stats['bytes'], stats['limit_maxbytes']),
        'miss_ratio': get_width_ratio(stats['get_misses'], stats['cmd_get'])}


def get_width_ratio(value, max_value, max_width=100):
    try:
        value = float(value)
        max_value = float(max_value)
        ratio = (value / max_value) * max_width
    except ZeroDivisionError:
        return '0'
    except (ValueError, TypeError, OverflowError):
        return ''
    return ratio


def debyteify(input):
    if isinstance(input, dict):
        return {debyteify(key): debyteify(value)
                for key, value in input.items()}
    elif isinstance(input, list):
        return [debyteify(element) for element in input]
    elif isinstance(input, bytes):
        return input.decode('utf-8')
    else:
        return input


def get_cache(cache_name):
    if hasattr(caches, '__call__'):
        return caches(cache_name)
    return caches[cache_name]
