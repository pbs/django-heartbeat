from django.conf import settings


def check(request):
    return {'debug_mode': settings.DEBUG}
