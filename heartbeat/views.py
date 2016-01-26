from django.conf import settings
from django.utils.importlib import import_module
from django.http import HttpResponse, JsonResponse

from .auth import http_basic_auth


def index(request):
    return HttpResponse(content='all good in the hood')


@http_basic_auth
def details(request):
    data = {}
    for checker in settings.HEARTBEAT['checkers']:
        checker_module = import_module(checker)
        data.update(checker_module.check())
    return JsonResponse(data)
