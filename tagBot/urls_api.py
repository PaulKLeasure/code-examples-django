from django.contrib import admin
from django.urls import path, include
#from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from . import views_api_tagbot_crud as tagbot_crud
from . import views_api_process as tagbot_process
from . import views_search as tagbot_search

urlpatterns = [
    path('api/tagbot/', tagbot_crud.router),
    path('api/tagbot/search/', tagbot_search.searchTagBotMappingsByNomenclature),
    path('api/tagbot/process/', tagbot_process.getTagsByFilename)
]


# REST API Related
urlpatterns = format_suffix_patterns(urlpatterns)

