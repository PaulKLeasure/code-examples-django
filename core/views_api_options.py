from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from core.models import Asset, Option, Category
from django.db.models import Q # filter using operators '&' or '|'
from django.db.models import Count
from pprint import pprint
from search.views import SearchAssetsOptions
from core.serializers import AssetSerializer
from core.serializers import OptionSerializer
#from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response


"""
List all file assets Options.
"""
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def FilteredAssetOptionGroups(request, format=None):
    context = {}
    optionGroups = []
    context['success'] = False
    filteringString = False
    if request.method == 'GET' and 'filteringString' in request.GET:
        filteringString = request.GET['filteringString']
        if filteringString is not None and filteringString != '':
            filteringString = request.GET['filteringString']
            filteringString.replace("%20", " ")
            optionsData = Option.objects.filter(groupName__icontains=filteringString).values('groupName').distinct().order_by('groupName')
            if(optionsData):
                for opt in optionsData:
                    optionGroups.append(dict(groupName=opt['groupName']))
                    context['success'] = True
    
                context['optionGroups'] = optionGroups
    
    return JsonResponse(context, safe=False)


@api_view(['GET'])
def FilteredAssetOptionAny(request, format=None):
    context = {}
    options = []
    context['success'] = False

    filteringString = False
    if request.method == 'GET' and 'filteringString' in request.GET:
        filteringString = request.GET['filteringString']
        if filteringString is not None and filteringString != '':
            filteringString.replace("%20", " ")
            optionsData = Option.objects.filter(Q(groupName__icontains=filteringString)| Q(definition__icontains=filteringString)).order_by('groupName','definition')
            serializedOtions = OptionSerializer(optionsData, many=True)
            context['optionGroups'] = serializedOtions.data
            context['success'] = True 

    return JsonResponse(context, safe=False)


"""
List all file assets Options.
"""
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def AssetOptionGroups(request, format=None):
    context = {}
    optionGroups = []
    context['success'] = False
    optionsData = Option.objects.all().values('id','groupName').distinct().order_by('groupName')
    if(optionsData):
        for opt in optionsData:
            if not any( d['groupName'] == opt['groupName'] for d in optionGroups ):
                optionGroups.append(dict(id=opt['id'], code=opt['id'], groupName=opt['groupName'], name=opt['groupName']))
                context['success'] = True 

    context['optionGroups'] = optionGroups 
    return JsonResponse(context, safe=False)


"""
    This returns a JSON object of all the values for 
    a given Asset Option Group based on the optionGroupName
    in the request object.

    This seems to be a duplicate of def get_option_group_values(request):

"""
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AssetOptionGroupValues(request):
    data = []
    context = {}
    success = False 
    error = 'No optionGroupName parameter was provided'

    if request.method == 'GET' and 'optionGroupName' in request.GET:
        optionGroupName = request.GET['optionGroupName']
        if optionGroupName is not None and optionGroupName != '':  
            optionGroupName.replace("%20", " ")
            options  = Option.objects.filter(groupName=optionGroupName).order_by('definition')
            for dat in options:
                # Make a list of dictionaries to be converted to JSON
                # safe=False must be set for JsonResponse(data, safe=False) to work 
                # with a list of dictionaries
                data.append({'id':dat.id,'groupName': dat.groupName, 'definition':dat.definition})
            success = True      
            error = ''

    context['data'] = data
    context['success'] = success
    context['error'] = error
    return JsonResponse(context, safe=False)


#def trimListEmptyEnds(theList):
#    while theList[0] == '':
#        theList.pop(0)
#    
#    while theList[-1] == '':
#        theList.pop(-1)
#
#    return theList



