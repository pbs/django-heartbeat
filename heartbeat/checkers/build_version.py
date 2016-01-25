from django.conf import settings
from pkg_resources import get_distribution, DistributionNotFound


def check():
    package_name = settings.HEARTBEAT.get('package_name')
    try:
        version = get_distribution(package_name)
    except DistributionNotFound:
        version = 'Unknown version'
    return {'project': '{}'.format(version)}
