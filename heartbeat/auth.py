import base64

from functools import wraps

from django.conf import settings
from django.http import HttpResponse


def http_basic_auth(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        if request.META.get('HTTP_AUTHORIZATION'):
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ')
            if authmeth.lower() == 'basic':
                auth = base64.b64decode(auth).decode('utf-8')
                username, password = auth.split(':')
                if (username == settings.HEARTBEAT['auth']['username'] and
                        password == settings.HEARTBEAT['auth']['password']):
                    return func(request, *args, **kwargs)
        response = HttpResponse(
            "your not wise enough to be in PonYLaNd 1337", status=401)
        response['WWW-Authenticate'] = 'Basic realm="Welcome to PonYLaNd 1337"'
        return response
    return _decorator
