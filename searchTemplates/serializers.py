from rest_framework import serializers
from .models import SearchTemplate

class SearchTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SearchTemplate 
        fields = ['id', 'name', 'descr', 'data', 'sort']