from pkg_resources import Requirement, WorkingSet

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def check(request):
    package_name = settings.HEARTBEAT.get('package_name')
    if not package_name:
        raise ImproperlyConfigured(
            'Missing package_name key from heartbeat configuration')

    sys_path_distros = WorkingSet()
    package_req = Requirement.parse(package_name)

    distro = sys_path_distros.find(package_req)
    if not distro:
        return dict(error='no distribution found for {}'.format(package_name))

    return dict(name=distro.project_name, version=distro.version)
