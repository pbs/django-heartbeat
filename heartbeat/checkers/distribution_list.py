from pip import get_installed_distributions


def check():
    distros = [{'name': i.project_name,
                'version': i.version} for i in get_installed_distributions()]
    return {'distribution_list': distros}
