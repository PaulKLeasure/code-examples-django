from django.contrib import admin
#from admin_searchable_dropdown.filters import AutocompleteFilter
from .models import Filter, FilterGroup, FilterGroupItem
from core.models  import Option as CoreOption

admin.site.register(Filter)
#admin.site.register(FilterGroup)
#admin.site.register(FilterGroupItem)

@admin.register(FilterGroup)
class FilterGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "Name")
    search_fields = ["Name"]

@admin.register(FilterGroupItem)
class FilterGroupItemAdmin(admin.ModelAdmin):
    list_display = ("id", "Name")
    search_fields = ['Name']





