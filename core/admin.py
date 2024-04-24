from django.contrib import admin
from .models import Asset, Option
#from admin_searchable_dropdown.filters import AutocompleteFilter



#class optionDefinitionFilter(AutocompleteFilter):
#    title = 'Defintion' # display title
#    field_name = 'definition' # name of the foreign key field


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ("id", "groupName", "definition")
    search_fields =[ "definition"]


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("id", "fileName")
    search_fields =[ "fileName", "search_string"]

#admin.site.register(Asset)
#admin.site.register(Option)