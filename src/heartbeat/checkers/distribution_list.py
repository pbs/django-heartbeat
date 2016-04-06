from pkg_resources import WorkingSet


def check(request):
    return [
        {'name': distribution.project_name, 'version': distribution.version}
        for distribution in WorkingSet()
    ]
