from django.conf import settings


def check(request):
    return settings.DEBUG
