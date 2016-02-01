import pytest
from mock import mock, Mock
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from pkg_resources import DistributionNotFound


class ConnectionError(Exception):
    pass

import sys
sys.modules['redis'] = mock.Mock()
sys.modules['redis.connection'] = mock.Mock()
sys.modules['redis.connection'].ConnectionError = ConnectionError

from .checkers import (
    build_version, debug_mode, distribution_list, redis_status)
settings.configure()


class TestCheckers(object):
    @pytest.mark.parametrize('pkg', [{'no_package_name_key': ''},
                                     {'package_name': ''},
                                     {'package_name': None}],
                             ids=['no_pkg_key', 'empty_pkg_name', 'None'])
    def test_build_version_missing_package_name(self, pkg):
        setattr(settings, 'HEARTBEAT', pkg)
        with pytest.raises(ImproperlyConfigured) as e:
            build_version.check()
        assert 'Missing package_name key from heartbeat configuration' in str(e)

    @mock.patch('heartbeat.checkers.build_version.get_distribution')
    def test_build_version_invalid_package_name(self, dist):
        setattr(settings, 'HEARTBEAT', {'package_name': 'django'})
        dist.side_effect = DistributionNotFound
        distro = build_version.check()
        assert distro['project_version'] == 'no distribution found for django'

    @mock.patch('heartbeat.checkers.build_version.get_distribution')
    def test_build_version_with_valid_package_name(self, dist):
        setattr(settings, 'HEARTBEAT', {'package_name': 'foo'})
        dist.return_value.project_name = 'foo'
        dist.return_value.version = '1.0.0'
        distro = build_version.check()
        assert distro['project_version'] == 'foo==1.0.0'

    @pytest.mark.parametrize('mode', [True, False])
    def test_debug_mode(self, mode):
        setattr(settings, 'DEBUG', mode)
        debug = debug_mode.check()
        assert debug['debug_mode'] == mode

    @mock.patch(
        'heartbeat.checkers.distribution_list.get_installed_distributions')
    def test_get_distribution_list(self, dist_list):
        dist_list.return_value = [
            Mock(project_name=i, version='1.0.0') for i in range(3)]
        distro = distribution_list.check()
        assert {'version': '1.0.0', 'name': 1} in distro['distribution_list']
        assert {'version': '1.0.0', 'name': 2} in distro['distribution_list']

    @mock.patch('heartbeat.checkers.redis_status.redis.StrictRedis')
    def test_redis_status(self, mock_redis):
        setattr(settings, 'CACHEOPS_REDIS', {'host': 'foo', 'port': 1337})
        mock_redis.return_value.ping.return_value = 'PONG'
        mock_redis.return_value.info.return_value = {'redis_version': '1.0.0'}
        status = redis_status.check()
        assert status['redis']['ping'] == 'PONG'
        assert status['redis']['version'] == '1.0.0'

    @mock.patch('heartbeat.checkers.redis_status.redis')
    def test_redis_connection_error(self, mock_redis):
        setattr(settings, 'CACHEOPS_REDIS', {'host': 'foo', 'port': 1337})
        mock_redis.StrictRedis.side_effect = ConnectionError('foo')
        status = redis_status.check()
        assert status['redis']['error'] == 'foo', status

    @mock.patch('heartbeat.checkers.redis_status.redis')
    def test_redis_import_error(self, mock_redis):
        mock_redis.StrictRedis.side_effect = NameError
        status = redis_status.check()
        assert status['redis']['error'] == 'cannot import redis library'
