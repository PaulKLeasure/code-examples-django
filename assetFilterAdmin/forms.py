from django import forms
from rest_framework import fields 
from .models import Filter, FilterGroup, FilterGroupIem, Location


class FilterForm(forms.ModelForm):
    class Meta:
        model = FilterGroup
        fields = ('Name', 'Description', 'FilterGroups', 'Location')
        excludes = 'Sort'


class FilterGroupForm(forms.ModelForm):
    class Meta:
        model = FilterGroup
        fields = ('Name', 'Description','FilterGroupItems')
        excludes = 'Sort'

class FilterGroupItemForm(forms.ModelForm):
    class Meta:
        model = FilterGroupItem
        fields = ('Name', 'Description', 'CoreOption')
        excludes = 'Sort'

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ('Name','Path', 'Description')
        excludes = 'Sort'