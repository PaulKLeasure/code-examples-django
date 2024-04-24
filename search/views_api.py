from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from core.models import Asset, Option, Category
from django.db.models import Q # filter using operators '&' or '|'
from django.db.models import Count
from pprint import pprint
from search.views import SearchAssetsOptions
from core.serializers import AssetSerializer
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from altTextBot.views_altText_crud_api import fetchAssetsAltTexts, fetchAssetAltTextById

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
def SearchAssetsByFilename(request, format=None):
    context = {}
    context['S3_iVault_uri'] = settings.S3_IVAULT_URI
    searchResults = ''
    fileNameString = request.GET.get('filename')
    quanPerPage = 10
    if(request.GET.get('limit')):
        quanPerPage = request.GET.get('limit')
    
    # Set default mode
    mode = 'AND'

    if request.GET.get('mode'):
        mode = request.GET.get('mode') 

    # Turn list of values into list of Q objects
    if fileNameString:
        assetSearchResults = Asset.objects.filter(fileName__contains=fileNameString).order_by('fileName')
        serializer = AssetSerializer( assetSearchResults, many=True)
        
        #Pagination
        paginator = Paginator(assetSearchResults, quanPerPage)
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

        serializer = AssetSerializer(searchResults, many=True)
        context['data'] = serializer.data
        context['pageCount'] = pageCount
        context['quanPerPage'] = quanPerPage
        context['pageNumber'] = page_number
        context['pageSeqLength'] = 8
        context['queryString'] = '/api/search?filename='+ fileNameString
        return JsonResponse(context, safe=False)


# ///////////////////////////

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
def SearchAssets(request, format=None):
    context = {}
    context['S3_iVault_uri'] = settings.S3_IVAULT_URI
    searchResults = ''
    fileNameString = ''
    queryString = request.GET.get('q')
    if(request.GET.get('filestr')):
        fileNameString = request.GET.get('filestr')

    quanPerPage = 10
    if(request.GET.get('limit')):
        quanPerPage = request.GET.get('limit')
    
    # Set default mode
    mode = 'AND'

    if request.GET.get('mode'):
        mode = request.GET.get('mode') 

    # Turn list of values into list of Q objects
    if queryString:
        if(len(fileNameString)):
            fileNameParts = fileNameString.split(",")
            andedContains = Q()
            for part in fileNameParts:
                andedContains &= Q(fileName__contains=part) 
            assets = Asset.objects.filter(andedContains).order_by('fileName')
        else:
            # Initial set based on all
            assets = Asset.objects.all().order_by('fileName')

        searchResultsData = SearchAssetsOptions(queryString, assets, mode)
        #serializer = AssetSerializer(searchResults, many=True)
        searchResults = searchResultsData["searchResults"]

        #Pagination
        paginator = Paginator(searchResults, quanPerPage)
        page_number = request.GET.get('page', 1)
        try:
            searchResultsPaginator = paginator.get_page(page_number)
            pageCount = paginator.num_pages
            objectsCount = paginator.count
            serializer = AssetSerializer(searchResultsPaginator, many=True)
        except PageNotAnInteger:
            searchResultsPaginator = paginator.get_page(page_number)
            pageCount = paginator.num_pages
            objectsCount = paginator.count
        except EmptyPage:
            searchResultsPaginator = paginator.get_page(paginator.num_pages)
            pageCount = paginator.num_pages
            objectsCount = paginator.count
        
        if request.GET.get('path') :
            data = fetchAssetsAltTexts(serializer.data, request.GET.get('path'))
        elif(request.GET.get("testAltTextPath")):
            data = fetchAssetsAltTexts(serializer.data, request.GET.get("testAltTextPath"))
        else:
            data = serializer.data

        print("response data")
        pprint(data)

        #context['data'] = serializer.data
        context['data'] = data
        context['objectsCount'] = searchResultsData["count"]
        context['pageCount'] = pageCount
        context['quanPerPage'] = quanPerPage
        context['pageNumber'] = page_number
        context['pageSeqLength'] = 8
        context['queryString'] = '/api/search?q='+queryString
        return JsonResponse(context, safe=False)

@api_view(['GET'])
@csrf_exempt
def SearchAssetsByOptions(request, format=None):

    optionIds = trimListEmptyEnds(request.GET.get('ids').split(","))

    # using list comprehension to convert nmbr strgs to integers
    # OFF optionIds = [int(i) for i in optionIds] 

    # Congigure a default page number
    pgNumber = 3
    # See if a limiter was passed in
    if(request.GET.get('page')):
        pgNumber = request.GET.get('page')
        int(pgNumber)

    # Congigure a default limiter for the query
    limitPerPg = 3
    # See if a limiter was passed in
    if(request.GET.get('limit')):
        limitPerPg = request.GET.get('limit')
        int(limitPerPg)

    context = {}
    context['S3_iVault_uri'] = settings.S3_IVAULT_URI

    serializedAssets = {'data': 'empty'}

    # This query returns assets that have ANY ONE or MORE of the IDs
    # assets = Asset.objects.filter(options__in=optionDefinition_ids)[:int(limitPerPg)]

    # This query returns assets that have ALL of the IDs
    andedContains = Q()
    for optId in optionIds:
        andedContains &= Q(search_string__contains="--"+optId+"--") 

    count = Asset.objects.filter(andedContains).count()
    context['count'] = count
    assets = Asset.objects.filter(andedContains)[:int(limitPerPg)]

    serializedAssets = AssetSerializer(assets, many=True)
    
    context['page'] = pgNumber
    context['limit'] = limitPerPg
    context['data'] = serializedAssets.data
    return JsonResponse(context, safe=False)

@api_view(['GET'])
@csrf_exempt
def SearchBatchTaggerAssets(request, format=None):
    tokenKey = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
    userByToken = Token.objects.get(key=tokenKey).user
    MaxResults = 2500
    context = {}
    context['action'] = 'do' # Valid = "do", "undo" 
    context['user'] = userByToken.username
    context['datetime'] = "datetime_placeholder"
    context['queryString'] = ''
    context['objectsCount'] = 0
    context['data'] = []
    searchResults = ''
    fileNameString = ''
    queryString = request.GET.get('q')
    if(request.GET.get('filestr')):
        fileNameString = request.GET.get('filestr')
    if(request.GET.get('limit')):
        quanPerPage = request.GET.get('limit')
    # Set default mode
    mode = 'AND'

    # Only authorized for user is admin
    if(not userByToken.is_admin):
        context["response_code"] = 401 
        context["message"] = "Not authorized! "+ userByToken.username +" is not an admin."
        context["success"] = "false" 
        return JsonResponse(context, safe=False) 

    if request.GET.get('mode'):
        mode = request.GET.get('mode') 
    
    # Turn list of values into list of Q objects
    if queryString:
        if(len(fileNameString)):
            fileNameParts = fileNameString.split(",")
            andedContains = Q()
            for part in fileNameParts:
                andedContains &= Q(fileName__contains=part) 

            assets = Asset.objects.filter(andedContains).order_by('fileName')
        else:
            # Initial set based on all
            assets = Asset.objects.all().order_by('fileName')

        searchResultsData = SearchAssetsOptions(queryString, assets, mode)

        if searchResultsData["count"] > MaxResults:
            context["response_code"] = 405 
            context["message"] = "Not Allowed! Search results greater than " + str(MaxResults) + " not permitted. Contact application developer for assistance."
            context["success"] = "false" 
            return JsonResponse(context, safe=False) 

        searchResults = searchResultsData["searchResults"]        
        context['data'] = {}
        context['data']['assets'] = []
        context['data']['asset_ids'] = []
        context['data']['options_added'] = []
        context['data']['options_removed'] = []
        context['objectsCount'] = searchResultsData["count"]
        context['queryString'] = '/api/search?q='+queryString
        serializer = AssetSerializer(searchResults, many=True)
        for asset in serializer.data:
            context['data']['assets'].append(asset)
            context['data']['asset_ids'].append(asset['id'])
        return JsonResponse(context, safe=False)


def trimListEmptyEnds(theList):
    while theList[0] == '':
        theList.pop(0)    
    while theList[-1] == '':
        theList.pop(-1)
    return theList



