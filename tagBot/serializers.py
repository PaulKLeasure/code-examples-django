from rest_framework import serializers
from .models import TagBotMapping, TagBotModes
from pprint import pprint

class TagBotModesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagBotModes 
        fields = ['id', 'name', 'description']

class TagBotMappingSerializer(serializers.ModelSerializer):
    #mode = TagBotModesSerializer(read_only=True, many=True)

    class Meta:
        model = TagBotMapping 
        fields = ['id', 'mode', 'nomenclature', 'optionIds', 'logic' ]