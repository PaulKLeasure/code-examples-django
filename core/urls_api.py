from django.contrib import admin
from django.urls import path, include
#from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

#from . import views as coreviews
from . import views_api_classes as class_views
from . import views_api_options as options_views
from . import views_api_asset_crud as core_asset_crud
from . import views_api_option_crud as core_option_crud
from . import views_api_batch_asset as core_asset_batch

#router = routers.DefaultRouter()
#router.register(r'users', coreviews.UserViewSet)
#router.register(r'groups', coreviews.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('api/asset/', core_asset_crud.router),
    path('api/asset/option/', core_option_crud.router),
    path('api/asset/option/group/', options_views.AssetOptionGroups ),
    path('api/asset/option/group/filtered', options_views.FilteredAssetOptionGroups ),
    path('api/asset/option/group/values/', options_views.AssetOptionGroupValues ),
    path('api/asset/option/filtered/any', options_views.FilteredAssetOptionAny ),
    path('api/asset/update/batch', core_asset_batch.router),
]

# REST API Related
urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]