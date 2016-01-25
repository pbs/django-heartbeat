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
                if (username == settings.BASICAUTH_USERNAME and
                        password == settings.BASICAUTH_PASSWORD):
                    return func(request, *args, **kwargs)
        response = HttpResponse('Auth Required', status=401)
        realm = getattr(settings, 'BASICAUTH_REALM', 'Secure heartbeat')
        response['WWW-Authenticate'] = 'Basic realm="{}"'.format(realm)
        return response
    return _decorator
