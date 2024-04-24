from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

#from . import views as coreviews
from iv_user.views_api import (
    router,
    registration_view
    ) 

app_name = "iv_user"


urlpatterns = [
    path('api/user/register/', registration_view, name="api-register"),
    path('api/user/login/', obtain_auth_token, name="api-login"),
    path('api/user/', router, name="api-user-data"),
]

'''

NOTE for API AUTHENTICATION

1) USER LOGIN on the VUE JS side using /api/user/login
    returns a token
2) send this token with API calls

in Djang use :
per https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
'''