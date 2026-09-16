from importlib.metadata import PackageNotFoundError, distribution

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def check(request):
    package_name = settings.HEARTBEAT.get('package_name')
    if not package_name:
        raise ImproperlyConfigured(
            'Missing package_name key from heartbeat configuration')

    try:
        dist = distribution(package_name)
        return dict(name=dist.metadata['Name'], version=dist.metadata['Version'])
    except PackageNotFoundError:
        return dict(error='no distribution found for {}'.format(package_name))
