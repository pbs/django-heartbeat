import pytest
from django.conf import settings
if not settings.configured:
    settings.configure()

from heartbeat.auth import is_authorized

def test_is_authorized_with_exact_valid_ip():
    authorized_ips = ['1.3.3.7']
    assert is_authorized('1.3.3.7', authorized_ips)


def test_is_authorized_with_exact_not_authorized_ip():
    authorized_ips = ['1.0.0.0', '1.3.3.0', '1.3.3.6']
    assert not is_authorized('1.3.3.7', authorized_ips)


def test_is_authorized_with_invalid_ip_address():
    authorized_ips = ['1.3.3.7']
    with pytest.raises(ValueError) as e:
        is_authorized('foo', authorized_ips)
    msg = '\'foo\' does not appear to be an IPv4 or IPv6 address'
    assert msg in str(e)


def test_is_authorized_with_invalid_ip_network():
    authorized_ips = ['1.3.3.7/foo', '1.3.3.7/33', '1.3.3.7/1337']
    assert not is_authorized('1.3.3.7', authorized_ips)


@pytest.mark.parametrize('ip', ['1.3.3.1', '1.3.3.127'])
def test_is_authorized_valid_ip_with_valid_ip_network(ip):
    authorized_ips = ['1.3.3.0/25']
    assert is_authorized(ip, authorized_ips)


@pytest.mark.parametrize('ip', ['1.3.3.8', '1.3.3.255'])
def test_is_authorized_invalid_ip_with_valid_ip_network(ip):
    authorized_ips = ['1.3.3.0/29']
    assert not is_authorized(ip, authorized_ips)


def test_is_authorized_bad_authorized_ips_config_does_not_raise():
    authorized_ips = ['foo', '1.3.3.7/foo', '1']
    assert not is_authorized('1.3.3.7', authorized_ips)
