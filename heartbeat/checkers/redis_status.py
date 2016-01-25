from django.conf import settings
import_error = None
try:
    import redis
    from redis.connection import ConnectionError
except ImportError:
    pass


def check():
    cacheops_redis = settings.CACHEOPS_REDIS
    host = cacheops_redis.get('host', '')
    port = cacheops_redis.get('port', 0)
    kwargs = {
        'host': host,
        'port': port,
    }

    data = {'redis': {'version': redis.VERSION}}
    try:
        redis_con = redis.StrictRedis(**kwargs)
        data['redis']['ping'] = redis_con.ping()
        data['redis']['version'] = redis_con.info().get('redis_version')
    except ConnectionError as e:
        data['redis'] = str(e)
    except NameError:
        data['redis'] = 'Import error'
    return data
