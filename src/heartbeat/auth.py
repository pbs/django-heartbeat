import re
import base64
import logging
from functools import wraps
from ipaddress import ip_address, ip_network

from .settings import HEARTBEAT
from django.http import HttpResponse
from django.core.exceptions import ImproperlyConfigured

logging.basicConfig(
    format='%(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


def auth(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        auth = get_auth()
        if auth.get('disable', False) is True:
            return func(request, *args, **kwargs)
        if 'authorized_ips' in auth:
            ip = get_client_ip(request)
            if is_authorized(ip, auth['authorized_ips']):
                return func(request, *args, **kwargs)
        prepare_credentials(auth)
        if request.META.get('HTTP_AUTHORIZATION'):
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ')
            if authmeth.lower() == 'basic':
                auth = base64.b64decode(auth).decode('utf-8')
                username, password = auth.split(':')
                if (username == HEARTBEAT['auth']['username'] and
                        password == HEARTBEAT['auth']['password']):
                    return func(request, *args, **kwargs)

        response = HttpResponse(
            "Authentication failed", status=401)
        response['WWW-Authenticate'] = 'Basic realm="Welcome to 1337"'
        return response

    return _decorator


def get_auth():
    auth = HEARTBEAT.get('auth')
    if not auth:
        raise ImproperlyConfigured('Missing auth configuration for heartbeat')
    return auth


def prepare_credentials(auth):
    if not all([auth.get('username'), auth.get('password')]):
        raise ImproperlyConfigured(
            'Username or password missing from auth configuration '
            'for heartbeat')


def get_access_route(request):
    meta = request.META
    return (
            meta.get('HTTP_X_FORWARDED_FOR') or meta.get('REMOTE_ADDR')
    ).split(',')


def get_client_ip(request):
    access_route = get_access_route(request)

    if len(access_route) == 1:
        return access_route[0]
    expression = r"""
        (^(?!(?:[0-9]{1,3}\.){3}[0-9]{1,3}$).*$)|  # will match non valid ipV4
        (^127\.0\.0\.1)|  # will match 127.0.0.1
        (^10\.)|  # will match 10.0.0.0 - 10.255.255.255 IP-s
        (^172\.1[6-9]\.)|  # will match 172.16.0.0 - 172.19.255.255 IP-s
        (^172\.2[0-9]\.)|  # will match 172.20.0.0 - 172.29.255.255 IP-s
        (^172\.3[0-1]\.)|  # will match 172.30.0.0 - 172.31.255.255 IP-s
        (^192\.168\.)  # will match 192.168.0.0 - 192.168.255.255 IP-s
    """
    regex = re.compile(expression, re.X)
    for ip in access_route:
        if not ip:
            # it's possible that the first value from X_FORWARDED_FOR
            # will be null, so we need to pass that value
            continue
        if regex.search(ip):
            continue
        else:
            return ip


def is_authorized(ip, authorized_ips):
    ip = ip_address(ip)

    for item in authorized_ips:
        try:
            if ip == ip_address(item):
                return True
        except ValueError:
            try:
                if ip in ip_network(item):
                    return True
            except ValueError:
                logger.warning('The "authorized_ip" list (settings.HEARTBEAT)'
                               'contains an item that is neither an ip address '
                               'nor an ip network: {}'.format(item))
