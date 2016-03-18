from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def default_checkers():
    heartbeat = getattr(settings, 'HEARTBEAT', {})
    if not heartbeat.get('checkers'):
        heartbeat['checkers'] = [
            'heartbeat.checkers.distribution_list',
            'heartbeat.checkers.debug_mode',
            'heartbeat.checkers.python',
        ]
    prepare_redis(heartbeat)
    return heartbeat


def prepare_redis(heartbeat):
    if 'heartbeat.checkers.redis' in heartbeat['checkers']:
        redis = getattr(settings, 'CACHEOPS_REDIS', None)
        if redis is None:
            raise ImproperlyConfigured(
                'Missing CACHEOPS_REDIS in project settings')

HEARTBEAT = default_checkers()
