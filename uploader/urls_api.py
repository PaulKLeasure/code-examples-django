from django.contrib import admin
from django.urls import path, include
from uploader import views_api

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    #path('', views.upload, name="uploader_page"),
    path('fileToS3/',views_api.api_upload_single_file_to_s3),
    path('commit-batch/', views_api.api_process_asset_upload, name="api_somename01"),
    path('upload-assets/', views_api.api_initialUpload, name="api_file_upload"),
    path('remove-uploaded-temp-files/', views_api.api_removeUploadedTempFiles, name="api_remove_uploaded_temp_files")

]
