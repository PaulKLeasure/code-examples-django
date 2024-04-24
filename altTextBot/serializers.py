from rest_framework import serializers
from .models import AltTextTemplate, AltTextCache
from pprint import pprint

class AltTextTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AltTextTemplate 
        fields = ['id', 'path', 'requiredIds', 'grpHeader', 'template', 'isRecursive', 'timestamp']

class AltTextCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = AltTextCache
        fields = ['id', 'assetId','templateId', 'fileName', 'path', 'altText', 'timestamp']