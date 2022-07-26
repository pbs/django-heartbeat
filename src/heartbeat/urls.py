try:
    from django.conf.urls import url
except:
    from django.urls import re_path as url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^1337/$', views.details, name='1337'),
]
