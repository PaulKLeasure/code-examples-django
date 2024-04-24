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
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

#from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response




# @api_view(['GET', 'POST'])
# def asset_list(request, format=None):
#     """
#     List all file assets, or create a new file asset.
#     """
#     if request.method == 'GET':
#         assets = Asset.objects.all()
#         serializer = AssetSerializer(assets, many=True)
#         return Response(serializer.data)

@api_view(['GET'])
@csrf_exempt
def searchTagBotMappingsByNomenclature(request, format=None):
    print('REQUEST OBJECT')
    pprint(request)
    context = {}
    tagBotHasResults = False
    #RESULTS_PER_PAGE = 12
    searchResults = ''
    searchMode = request.GET.get('mode')
    searchString = request.GET.get('str')
    quanPerPage = 100
    context['queryString'] = '/api/tagbot/search/?mode='+ searchMode +'&str='+searchString

    if(request.GET.get('limit')):
        quanPerPage = request.GET.get('limit')

    # Turn list of values into list of Q objects
    if len(searchMode) > 0 and len(searchString) > 0 :

        if searchMode == 'file-codes':
            try:
                tagBotSearchResults = TagBotMapping.objects.filter(nomenclature__contains=searchString).order_by('nomenclature')
                tagBotHasResults = True
            except ObjectDoesNotExist:
                err = searchMode +':: tagBotSearchResults: failed'
                print(err)
                context["error"] = err
                context["success"] = False
            
        if searchMode == 'logic':
            try:
                tagBotSearchResults = TagBotMapping.objects.filter(logic__contains=searchString).order_by('nomenclature')
                tagBotHasResults = True
            except ObjectDoesNotExist:
                err = searchMode +':: tagBotSearchResults: failed'
                print(err)
                context["error"] = err
                context["success"] = False

        if tagBotHasResults :
            #searchResultsData = SearchAssetsOptions(queryString, asset, mode)
            serializer = TagBotMappingSerializer( tagBotSearchResults, many=True)
            #searchResults =  assetSearchResults["searchResults"]
            
            #Pagination
            print('BEFORE: Paginator')
            paginator = Paginator(tagBotSearchResults, quanPerPage)
            page_number = request.GET.get('page', 1)
            try:
                searchResults = paginator.get_page(page_number)
                pageCount = paginator.num_pages
                objectsCount = paginator.count
            except PageNotAnInteger:
                searchResults = paginator.get_page(page_number)
                pageCount = paginator.num_pages
                objectsCount = paginator.count
            except EmptyPage:
                searchResults = paginator.get_page(paginator.num_pages)
                pageCount = paginator.num_pages
                objectsCount = paginator.count
            print('BEFOR: TagBotMappingSerializer')
            serializer = TagBotMappingSerializer(searchResults, many=True)
    
            context['objectsCount'] = objectsCount
            context['pageCount'] = pageCount
            context['quanPerPage'] = quanPerPage
            context['pageNumber'] = page_number
            context['pageSeqLength'] = 8
            context["success"] = True
            context['data'] = serializer.data
        else:
            context['pageCount'] = 1
            context['quanPerPage'] = quanPerPage
            context['pageNumber'] = 1
            context['objectsCount'] = 0
            context["success"] = True
            context['data'] = []
        print('BEFOR: JsonResponse')
        pprint(context)
        return JsonResponse(context, safe=False)
