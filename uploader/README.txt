========================
UPLOADER  APP  NOTES
========================
README.txt  for Uplaoder

See settings.py for configuration of:
MEDIA_ROOT
MEDIA_URL

See urls.py for:

# How to handle media for DEV
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)