from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views_template_crud_api
from . import views_altText_crud_api

"""  
Fetch Template(s):
  api/alttext/template  get all templates data 
  api/alttext/template/?id=<id>  get specific templates data 

Fetch Alt Text:
  api/alttext/text?assetId=<asset id>&path=<path>&overrideCache=<boole default false>
  api/alttext/text?assetId=595310&path=/cabinet-finishes-browser

Test Alt Text By Image (returns all templates that apply to image):
  /api/alttext/template-test?assetId=<ID>
  /api/alttext/template-test?assetId=<Filename>

Build Cache:
  api/textbot/build-alttext-cache  (defaults to ALL templates)
  api/textbot/build-alttext-cache/?templateId=<id> (specific template)
  RECOMMENDATIONS:
  - Run this in its own util instance so that it can refresh cache often 
    without casuing latency on the primary iVault Service API

"""
urlpatterns = [
    path('api/alttext/template', views_template_crud_api.altTextTemplate),
    path('api/alttext/text', views_altText_crud_api.getAltText),
    path('api/alttext/template-test', views_altText_crud_api.altTextTemplateTest),
    path('api/textbot/build-alttext-cache', views_altText_crud_api.cacheBuilder),
]

# REST API Related
urlpatterns = format_suffix_patterns(urlpatterns)
