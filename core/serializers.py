
from rest_framework import serializers
from .models import Category
from .models import Option
from .models import Asset
from pprint import pprint



class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option 
        fields = ['id', 'groupName', 'definition']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class AssetSerializer(serializers.ModelSerializer):
    options = OptionSerializer(read_only=True, many=True)
    #fileName = serializers.SerializerMethodField()

    #def get_fileName(self, obj):
    #    print("========== SERIALIZER: obj.fileName:=========")
    #    pprint(obj.fileName)
    #    return obj.fileName

    #category = CategorySerializer(read_only=True, many=True)
    class Meta:
        model = Asset 
        fields = ['id', 'fileName', 'search_string', 'timestamp', 'options']
