from pip import get_installed_distributions


def check():
    return {
        'distribution_list': [
            {'name': i.project_name, 'version': i.version} for i in
            get_installed_distributions()
        ]
    }
