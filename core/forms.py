from django import forms
from rest_framework import fields 
from .models import Asset, Option



class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ('groupName','definition')
        excludes = 'groupSort'


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ('fileName', 'search_string')


