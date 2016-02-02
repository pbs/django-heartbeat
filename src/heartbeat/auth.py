import base64

from functools import wraps

from .settings import HEARTBEAT
from django.http import HttpResponse
from django.core.exceptions import ImproperlyConfigured


def http_basic_auth(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        prepare_auth()
        if request.META.get('HTTP_AUTHORIZATION'):
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ')
            if authmeth.lower() == 'basic':
                auth = base64.b64decode(auth).decode('utf-8')
                username, password = auth.split(':')
                if (username == HEARTBEAT['auth']['username'] and
                        password == HEARTBEAT['auth']['password']):
                    return func(request, *args, **kwargs)
        response = HttpResponse(
            "your not wise enough to be in PonYLaNd 1337", status=401)
        response['WWW-Authenticate'] = 'Basic realm="Welcome to PonYLaNd 1337"'
        return response
    return _decorator


def prepare_auth():
    auth = HEARTBEAT.get('auth')
    if not auth:
        raise ImproperlyConfigured('Missing auth configuration for heartbeat')

    if not all([auth.get('username'), auth.get('password')]):
        raise ImproperlyConfigured(
            'Username or password missing from auth configuration '
            'for heartbeat')
