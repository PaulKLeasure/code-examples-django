from . import models
from . import serializers


def get_item(item_id):
    data = {}
    try:
        history_item = models.History.objects.get(id=item_id)
    except models.History.DoesNotExist:
        history_item = None

    if history_item:
        item = serializers.HistorySerializer(history_item, many=False)
        data = item.data

    return data


def save_history(data, username):
    applied = 1
    # data will have assets, added, removed
    history = models.History(state=applied, asset_ids=data["assets"], oids_added=data["added"], oids_removed=data["removed"], username=username)
    history.save()

    return True

