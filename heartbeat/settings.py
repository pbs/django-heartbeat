from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def default_checkers():
    heartbeat = getattr(settings, 'HEARTBEAT', {})
    if not heartbeat.get('checkers'):
        heartbeat['checkers'] = [
            'heartbeat.checkers.distribution_list',
            'heartbeat.checkers.debug_mode',
        ]
    prepare_auth(heartbeat)
    prepare_redis(heartbeat)

    return heartbeat


def prepare_auth(heartbeat):
    auth = heartbeat.get('auth')
    if not auth:
        raise ImproperlyConfigured('Missing auth configuration for heartbeat')

    if not all([auth.get('username'), auth.get('password')]):
        raise ImproperlyConfigured(
            'Username or password missing from auth configuration '
            'for heartbeat')


def prepare_redis(heartbeat):
    if 'heartbeat.checkers.redis_status' in heartbeat['checkers']:
        redis = getattr(settings, 'CACHEOPS_REDIS', None)
        if redis is None:
            raise ImproperlyConfigured(
                'Missing CACHEOPS_REDIS in project settings')

HEARTBEAT = default_checkers()
