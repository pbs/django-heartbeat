from importlib.metadata import distributions


def check(request):
    return [
        {'name': dist.metadata['Name'], 'version': dist.metadata['Version']}
        for dist in distributions()
    ]
