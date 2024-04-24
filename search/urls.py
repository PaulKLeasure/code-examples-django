from django.contrib import admin
from django.urls import path, include
from search import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', views.SearchAssets, name="search_page"),
    path('ajax/opt-grp-values/', views.ajax_option_group_values, name="ajax_option_group_values"), 
    path('byfilename/', views.search_by_filename, name="search_by_filename")
]