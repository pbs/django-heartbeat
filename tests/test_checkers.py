import sys

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from pkg_resources import DistributionNotFound

try:
    from unittest import mock
    from unittest.mock import Mock
except ImportError:
    from mock import mock, Mock


class ConnectionError(Exception):
    pass

sys.modules['redis'] = mock.Mock()
sys.modules['redis.connection'] = mock.Mock()
sys.modules['redis.connection'].ConnectionError = ConnectionError

if not settings.configured:
    settings.configure()
from heartbeat.checkers import (
    build_version, debug_mode, distribution_list, redis_status, databases,
    memcached)

from heartbeat import settings as heartbeat_settings


class TestCheckers(object):
    @pytest.mark.parametrize('pkg', [{'no_package_name_key': ''},
                                     {'package_name': ''},
                                     {'package_name': None}],
                             ids=['no_pkg_key', 'empty_pkg_name', 'None'])
    def test_build_version_missing_package_name(self, pkg):
        setattr(settings, 'HEARTBEAT', pkg)
        with pytest.raises(ImproperlyConfigured) as e:
            build_version.check(request=None)
        msg = 'Missing package_name key from heartbeat configuration'
        assert msg in str(e)

    @mock.patch('heartbeat.checkers.build_version.get_distribution')
    def test_build_version_invalid_package_name(self, dist):
        setattr(settings, 'HEARTBEAT', {'package_name': 'django'})
        dist.side_effect = DistributionNotFound
        distro = build_version.check(request=None)
        assert distro == 'no distribution found for django'

    @mock.patch('heartbeat.checkers.build_version.get_distribution')
    def test_build_version_with_valid_package_name(self, dist):
        setattr(settings, 'HEARTBEAT', {'package_name': 'foo'})
        dist.return_value.project_name = 'foo'
        dist.return_value.version = '1.0.0'
        distro = build_version.check(request=None)
        assert distro == 'foo==1.0.0'

    @pytest.mark.parametrize('mode', [True, False])
    def test_debug_mode(self, mode):
        setattr(settings, 'DEBUG', mode)
        debug = debug_mode.check(request=None)
        assert debug == mode

    @mock.patch(
        'heartbeat.checkers.distribution_list.get_installed_distributions')
    def test_get_distribution_list(self, dist_list):
        dist_list.return_value = [
            Mock(project_name=i, version='1.0.0') for i in range(3)]
        distro = distribution_list.check(request=None)
        assert {'version': '1.0.0', 'name': 1} in distro
        assert {'version': '1.0.0', 'name': 2} in distro

    @mock.patch('heartbeat.checkers.redis_status.redis.StrictRedis')
    def test_redis_status(self, mock_redis):
        setattr(settings, 'CACHEOPS_REDIS', {'host': 'foo', 'port': 1337})
        mock_redis.return_value.ping.return_value = 'PONG'
        mock_redis.return_value.info.return_value = {'redis_version': '1.0.0'}
        status = redis_status.check(request=None)
        assert status['ping'] == 'PONG'
        assert status['version'] == '1.0.0'

    @mock.patch('heartbeat.checkers.redis_status.redis')
    def test_redis_connection_error(self, mock_redis):
        setattr(settings, 'CACHEOPS_REDIS', {'host': 'foo', 'port': 1337})
        mock_ping = mock_redis.StrictRedis.return_value.ping
        mock_ping.side_effect = ConnectionError('foo')
        status = redis_status.check(request=None)
        assert status['error'] == 'foo', status

    @mock.patch('heartbeat.checkers.redis_status.redis')
    def test_redis_import_error(self, mock_redis):
        mock_redis.StrictRedis.side_effect = NameError
        status = redis_status.check(request=None)
        assert status['error'] == 'cannot import redis library'

    def test_prepare_redis(self):
        delattr(settings, 'CACHEOPS_REDIS')
        HEARTBEAT = {'checkers': ['heartbeat.checkers.redis_status']}
        with pytest.raises(ImproperlyConfigured) as e:
            heartbeat_settings.prepare_redis(HEARTBEAT)
        assert 'Missing CACHEOPS_REDIS in project settings' in str(e)

    # def test_dummy_databases(self):
    #     dbs = databases.check(request=None)
    #     engine = dbs['databases'][0]['default']['engine']
    #     assert engine == 'django.db.backends.dummy'

    def test_db_version(self):
        import django
        if django.VERSION >= (1, 7):
            cursor = 'django.db.backends.utils.CursorWrapper'
        else:
            cursor = 'django.db.backends.util.CursorWrapper'
        with mock.patch(cursor) as mock_cursor:
            mock_cursor.return_value.fetchone.return_value = ['1.0.0']
            dbs = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': 'foo'
                }
            }
            setattr(settings, 'DATABASES', dbs)
            dbs = databases.check(request=None)
        assert dbs[0]['default']['version'] == '1.0.0'

    @mock.patch('heartbeat.checkers.memcached.get_cache')
    @pytest.mark.parametrize('backend', ['MemcachedCache', 'PyLibMCCache'])
    def test_memcached(self, mock_get_cache, backend):
        caches = {
            'foo': {
                'BACKEND': 'django.core.cache.backends.memcached.{}'.format(
                    backend)}}
        server = 'foo:11211'
        stats = {'bytes': 1, 'limit_maxbytes': 10, 'get_misses': 10,
                 'cmd_get': 100, 'foo': 'bar'}

        mock_get_cache.return_value._cache.get_stats.return_value = [
            (server, stats)]
        setattr(settings, 'CACHES', caches)
        all_stats = memcached.check(request=None)
        assert all_stats['foo'][0]['location'] == server
        assert all_stats['foo'][0]['summary']['load'] == 10
        assert all_stats['foo'][0]['details']['foo'] == 'bar'
        assert len(all_stats['foo'][0]['details'].items()) == 5

    def test_memcached_with_no_profiles(self):
        setattr(settings, 'CACHES', dict())
        all_stats = memcached.check(request=None)
        assert all_stats['error'] == 'No memcached profiles found'

    def test_memcached_with_no_memcached_profiles(self):
        caches = {
            'foo': {'BACKEND': 'django.core.cache.backends.db.DatabaseCache'}
        }
        setattr(settings, 'CACHES', caches)
        all_stats = memcached.check(request=None)
        assert all_stats['error'] == 'No memcached profiles found'

    @mock.patch('heartbeat.checkers.memcached.get_cache')
    def test_memcached_with_different_cache_backends(self, mock_get_cache):
        backends = 'django.core.cache.backends'
        caches = {
            'foo': {'BACKEND': '{}.db.DatabaseCache'.format(backends)},
            'bar': {'BACKEND': '{}.memcached.MemcachedCache'.format(backends)}}
        server = 'foo:11211'
        stats = {'bytes': 1, 'limit_maxbytes': 10, 'get_misses': 10,
                 'cmd_get': 100, 'foo': 'bar'}

        mock_get_cache.return_value._cache.get_stats.return_value = (
            [(server, stats)])
        setattr(settings, 'CACHES', caches)
        all_stats = memcached.check(request=None)
        assert len(all_stats.items()) == 1
        assert all_stats['bar'][0]['location'] == server
        assert all_stats['bar'][0]['details']['foo'] == 'bar'
