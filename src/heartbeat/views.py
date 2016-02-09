from importlib import import_module
from django.http import HttpResponse, JsonResponse

from .settings import HEARTBEAT
from .auth import auth


def index(request):
    return HttpResponse(content='all good in the hood')


@auth
def details(request):
    data = {}
    for checker in HEARTBEAT['checkers']:
        checker_module = import_module(checker)
        data.update(checker_module.check(request))
    return JsonResponse(data)
