from django.contrib import admin
from .models import AltTextTemplate

@admin.register(AltTextTemplate)
class AltTextTemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "path", "requiredIds")
    search_fields =[ "path", "requiredIds", "template"]

