from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views_api as views_api

urlpatterns = [
    path('api/filternav', views_api.filter_nav),
    path('api/filternav-group', views_api.filter_group_nav)
]


# REST API Related
urlpatterns = format_suffix_patterns(urlpatterns)