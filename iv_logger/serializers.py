
from rest_framework import serializers
from .models import IvaultLog
#from pprint import pprint

class IvaultLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = IvaultLog 
        fields = ['id', 'filename', 'data', 'logged_user', 'timestamp']