from django.conf import settings
try:
    import redis
    from redis.connection import ConnectionError
except ImportError:
    pass


def check():
    host = settings.CACHEOPS_REDIS.get('host', '')
    port = settings.CACHEOPS_REDIS.get('port', 0)

    try:
        redis_con = redis.StrictRedis(host=host, port=port)
        ping = redis_con.ping()
    except NameError:
        return {'redis': {'error': 'cannot import redis library'}}
    except ConnectionError as e:
        return {'redis': {'error': str(e)}}

    return {
        'redis': {
            'ping': ping,
            'version': redis_con.info().get('redis_version')
        }
    }
