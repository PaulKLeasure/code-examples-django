from django.contrib import admin
from django.urls import path, include
from . import functions, views_api

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('asset', views_api.getAssetLogs)
]


