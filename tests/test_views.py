import json
import pytest

from django.conf import settings
if not settings.configured:
    settings.configure()

from django.test import RequestFactory
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured

from heartbeat.views import index, details

setattr(settings, 'ROOT_URLCONF', 'heartbeat.urls')


def test_index():
    factory = RequestFactory()
    request = factory.get(reverse('index'))
    response = index(request)
    assert response.status_code == 200


def check(request):
    return {'ping': 'pong'}


class TestDetailsView:

    def setup_method(self, method):
        from heartbeat.settings import HEARTBEAT

        HEARTBEAT.update({
            'checkers': ['tests.test_views'],
            'auth': {
                'username': 'foo',
                'password': 'bar',
                'authorized_ips': ['1.3.3.7'],
            }
        })
        self.heartbeat = HEARTBEAT

        basic_auth = {'HTTP_AUTHORIZATION': 'Basic Zm9vOmJhcg=='}

        self.factory = RequestFactory(**basic_auth)

    def test_200OK(self):
        request = self.factory.get(reverse('1337'))
        response = details(request)
        assert response.status_code == 200
        assert response['content-type'] == 'application/json'
        json_response = json.loads(response.content.decode('utf-8'))
        assert json_response['checkers']['test_views']['ping'] == 'pong'

    def test_with_invalid_basic_auth_credentials(self):
        self.factory.defaults.pop('HTTP_AUTHORIZATION')
        request = self.factory.get(reverse('1337'))
        response = details(request)
        assert response.status_code == 401

    def test_missing_auth_configuration(self):
        self.heartbeat.pop('auth')
        with pytest.raises(ImproperlyConfigured) as e:
            request = self.factory.get(reverse('1337'))
            details(request)
        msg = 'Missing auth configuration for heartbeat'
        assert msg == str(e.value)

    def test_missing_auth_credentials(self):
        self.heartbeat['auth'] = {'blow': 'fish'}
        with pytest.raises(ImproperlyConfigured) as e:
            request = self.factory.get(reverse('1337'))
            details(request)
        msg = ('Username or password missing from auth configuration '
               'for heartbeat')
        assert msg == str(e.value)

    def test_regex_rem_match(self):
        self.heartbeat['auth'].update(
            {
                'username': 'blow',
                'password': 'fish',
                'authorized_ips': ['1.+']
            }
        )
        request = self.factory.get(
            reverse('1337'), **{'REMOTE_ADDR': '1.3.3.7'})
        response = details(request)
        assert response.status_code == 200

    def test(self):
        self.heartbeat['auth'].update({'username': 'blow', 'password': 'fish'})
        request = self.factory.get(
            reverse('1337'), **{'REMOTE_ADDR': '1.3.3.7'})
        response = details(request)
        assert response.status_code == 200
