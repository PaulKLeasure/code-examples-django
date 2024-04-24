from django.contrib import admin
from django.urls import path, include

#from . import views as coreviews
from core import views

urlpatterns = [
    path('', views.home, name="home"),
    path('secret/', views.secret_page, name="secret_page"),
    path('secret2/', views.secretPage.as_view(), name="secret2_page"),
    path('signup/', views.signup, name="signup"),
    path('create/option/', views.option_create_view, name="option_create")
]

