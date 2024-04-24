from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views_api as views_api

urlpatterns = [
    path('api/batchtagger', views_api.batch_tagger),
    path('api/batchtagger/history', views_api.history),
]


# REST API Related
urlpatterns = format_suffix_patterns(urlpatterns)

