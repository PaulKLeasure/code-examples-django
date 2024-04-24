from django.contrib import admin
from django.urls import path, include

from core import views as coreviews
from search import views as searchviews
from uploader import views as uploaderviews
from django.conf import settings
from django.conf.urls.static import static


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [

    path('', include('core.urls')),
    path('', include('core.urls_api')),
    path('', include('tagBot.urls_api')),
    path('', include('search.urls_api')),
    path('', include('core.urls_user_account')),
    path('', include('iv_user.urls_api')),
    path('upload/', include('uploader.urls')),
    path('search/', include('search.urls')),
    path('api/logs/', include('iv_logger.urls_api')),
    
    path('api/search/template/', include('searchTemplates.urls_api')),
    path('admin/', admin.site.urls),
    path('api/uploader/', include('uploader.urls_api')),
    path('tagbot/', include('tagBot.urls')),
    path('', include('batchTagger.urls_api')),
    path('', include('assetFilterAdmin.urls_api')),
    path('', include('altTextBot.urls_api'))
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

