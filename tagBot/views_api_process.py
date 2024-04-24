from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from tagBot.models import TagBotModes, TagBotMapping
from django.db.models import Q # filter using operators '&' or '|'
from django.db.models import Count
from pprint import pprint
from tagBot.serializers import TagBotMappingSerializer
from tagBot.functions import process_filename_codes
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

#from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response



@api_view(['GET'])
@csrf_exempt
def getTagsByFilename(request, format=None):
    context = {}
    dryrun = False
    context['tagCount'] = 0
    context["success"] = False
    context['data'] = []
    filename = request.GET.get('filename')
    mode = request.GET.get('mode')
    isdryun = request.GET.get('dryrun') 
    context['filename'] = ''
    context['mode'] = ''
    context['queryString'] = '/api/tagbot/process?mode='+ mode +'&filename='+filename
    if(filename and mode):
        context = process_filename_codes(filename, mode, dryrun)
        return JsonResponse(context, safe=False)
    else:
        return JsonResponse(context, safe=False)

