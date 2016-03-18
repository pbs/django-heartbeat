from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from pkg_resources import get_distribution, DistributionNotFound


def check(request):
    package_name = settings.HEARTBEAT.get('package_name')
    if not package_name:
        raise ImproperlyConfigured(
            'Missing package_name key from heartbeat configuration')

    try:
        distro = get_distribution(package_name)
    except DistributionNotFound:
        return dict(error='no distribution found for {}'.format(package_name))

    return dict(name=distro.project_name, version=distro.version)
