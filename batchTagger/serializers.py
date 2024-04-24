from rest_framework import serializers
from .models import History
from pprint import pprint


class HistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = History
        fields = ['id', 'timestamp', 'state', 'asset_ids',
                  'oids_added', 'oids_removed', 'username']
