from django.contrib import admin
from django.urls import path, include
from uploader import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', views.upload, name="uploader_page"),
    path('ajax/opt-grp-values/', views.ajax_option_group_values, name="ajax_option_group_values"),
    path('ajax/add-asset-def/', views.ajax_add_option_val_to_asset, name="ajax_add_option_val_to_asset"),
    path('ajax/remove-asset-def/', views.ajax_remove_option_val_to_asset, name="ajax_remove_option_val_to_asset"),
    path('ajax/commit-batch/', views.ajax_commit_file_asset_uploads, name="ajax_commit_file_asset_uploads"),
    path('ajax/cancel-batch/', views.ajax_delete_upload_temp_files, name="ajax_delete_upload_temp_files"),
]
