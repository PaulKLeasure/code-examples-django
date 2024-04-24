from django.contrib import admin
from django.urls import path, include
from . import views, functions

urlpatterns = [
    path('test/', functions.test),
    path('fix_nomenclature/', functions.fix_nomenclature)
]
