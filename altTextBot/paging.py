from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from . import models
from . import serializers


def get_page(page):
    data = {}
    # For now until this is updated to handle
    # both paging and non-paging queries
    page_size = 100

    try:
        AltTextTemplate_items = models.AltTextTemplate.objects.all().order_by('-id')
    except models.AltTextTemplate.DoesNotExist:
        AltTextTemplate_items = None

    if AltTextTemplate_items:
        paginator = Paginator(AltTextTemplate_items, per_page=page_size)
        page_obj = paginator.get_page(number=page)
        items = serializers.AltTextTemplateSerializer(page_obj.object_list, many=True)
        data = items.data
    return data


