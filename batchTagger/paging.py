from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from . import models
from . import serializers


def get_page(page):
    data = {}
    # For now until this is updated to handle
    # both paging and non-paging queries
    page_size = 1000

    try:
        history_items = models.History.objects.all().order_by('-id')
    except models.History.DoesNotExist:
        history_items = None

    if history_items:
        paginator = Paginator(history_items, per_page=page_size)
        page_obj = paginator.get_page(number=page)
        items = serializers.HistorySerializer(page_obj.object_list, many=True)
        data = items.data
    return data


