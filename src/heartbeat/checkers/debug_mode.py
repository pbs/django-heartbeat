from django.conf import settings


def check():
    return {'debug_mode': settings.DEBUG}
