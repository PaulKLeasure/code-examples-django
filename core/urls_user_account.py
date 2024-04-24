from django.contrib import admin
from django.urls import path, include
from core import views
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('accounts/', include('django.contrib.auth.urls')),
]

# ========================================
# NOTE:
# Using the Django authentication system
# There are many built in URLs (shown below)
# and config settings for settings.py
# eg.
#    LOGIN_REDIRECT_URL  = 'home'
#    LOGOUT_REDIRECT_URL = 'home'
# ========================================
# https://docs.djangoproject.com/en/3.0/topics/auth/default/
#
# accounts/login/ [name='login']
# accounts/logout/ [name='logout']
# accounts/password_change/ [name='password_change']
# accounts/password_change/done/ [name='password_change_done']
# accounts/password_reset/ [name='password_reset']
# accounts/password_reset/done/ [name='password_reset_done']
# accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
# accounts/reset/done/ [name='password_reset_complete']