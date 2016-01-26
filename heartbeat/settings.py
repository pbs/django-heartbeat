from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def prepare_heartbeat():
    heartbeat = getattr(settings, 'HEARTBEAT', {})
    if not heartbeat.get('checkers'):
        heartbeat['checkers'] = [
            'heartbeat.checkers.distribution_list',
            'heartbeat.checkers.debug_mode',
        ]

    auth = heartbeat.get('auth')
    if not auth:
        raise ImproperlyConfigured('Missing auth configuration for heartbeat')

    if 'username' not in auth or 'password' not in auth:
        raise ImproperlyConfigured(
            'Username or password missing from auth configuration '
            'for heartbeat')

    return heartbeat


HEARTBEAT = prepare_heartbeat()
