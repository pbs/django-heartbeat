from django.conf import settings
try:
    import redis
    from redis.connection import ConnectionError
except ImportError:
    pass


def check(request):
    host = settings.CACHEOPS_REDIS.get('host', '')
    port = settings.CACHEOPS_REDIS.get('port', 0)
    db = settings.CACHEOPS_REDIS.get('db', 0)
    socket_timeout = settings.CACHEOPS_REDIS.get('socket_timeout')

    try:
        redis_con = redis.StrictRedis(
            host=host, port=port, db=db, socket_timeout=socket_timeout)
        ping = redis_con.ping()
    except NameError:
        return {'error': 'cannot import redis library'}
    except ConnectionError as e:
        return {'error': str(e)}

    return {
            'ping': ping,
            'version': redis_con.info().get('redis_version')
        }
