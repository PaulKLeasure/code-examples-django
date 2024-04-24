#from django.contrib import admin
from django.urls import path, re_path, include
from search import views_api 

"""
Search Assets with a special query string language
explained in search/views.py
 eg.

  /api/search/?oids=^Finish%20Categories^~Cabinets,-171:-167,166

  READS:" Assets having any values in the Finish Catigories OR 
          Cabinets groups, EXCLUDING any combination of 
          171 OR 167, AND requiring the option ID of 166"

"""
urlpatterns = [
    path('api/search/', views_api.SearchAssets),
    path('api/search/batchTagger/assets/', views_api.SearchBatchTaggerAssets),
    path('api/search/assets/by-filename/', views_api.SearchAssetsByFilename),
    path('api/search/assets/by-options/', views_api.SearchAssetsByOptions),
]
