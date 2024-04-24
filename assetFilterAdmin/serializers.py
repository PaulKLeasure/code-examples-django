from rest_framework import serializers
from .models import Filter, FilterGroup, FilterGroupItem
from core.models  import Option


 
class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option 
        fields = ['id', 'groupName', 'definition']

class AssetFilterNavSerializer(serializers.ModelSerializer):
    #filterGroups =  AssetFilterNavGroupSerializer(read_only=True, many=True)
    class Meta:
        model = Filter
        fields = ['id', 'Name', 'Description', 'mach_name', 'LocationPath','Enabled','Sort']

class AssetFilterNavGroupSerializer(serializers.ModelSerializer):
    #filterGroupItems = AssetFilterNavGroupItemSerializer(read_only=True, many=True)
    #parentFilter = AssetFilterNavSerializer(read_only=True, many=True)
    class Meta:
        model = FilterGroup
        fields = ['id', 'parentFilter', 'Name', 'Sort', 'Description', 'selectionElement']

class AssetFilterNavGroupItemSerializer(serializers.ModelSerializer):
    coreOption =  OptionSerializer(read_only=True, many=False)
    parentGroup = AssetFilterNavGroupSerializer(read_only=True, many=False)
    class Meta:
        model = FilterGroupItem
        fields = ['id', 'parentGroup', 'Name', 'Description', 'coreOption',  'Sort']
