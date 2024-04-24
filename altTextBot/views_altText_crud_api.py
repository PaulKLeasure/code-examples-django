from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Cast
from django.core.exceptions import ObjectDoesNotExist
from .models import AltTextTemplate, AltTextCache
from .paging import get_page
from .functions import fetchAltText, getAllAltTextTemplates, fetchAltTextTemplateResults, getSerialAssetDataByFilename, getSerialAssetDataById
from altTextBot.functions_altText_mongo_crud import mongoSaveAltTextCache, mongoRecallAltText, mongoDeleteAltTextCache
from .cache_functions_mongo import buildTextBotTemplateCache
from .serializers import AltTextTemplateSerializer, AltTextCacheSerializer
from pprint import pprint
import json
from operator import itemgetter
import traceback

def get_user_from_token(request):
    token_key = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
    user = Token.objects.get(key=token_key).user
    return user

#  /api/altText/template?id=<id>
# 
#  returns: json data
#
# @api_view(["GET", "PUT"])
# @permission_classes([IsAuthenticated])
# @csrf_exempt
# def altTextTemplate(request):
#     user = get_user_from_token(request=request)
#     # READ ACCESS OPEN with API Auth Token
#     if(request.method == "GET"):
#         return getAltText(request)
#     # "POST","PUT","DELETE" Only authorized for user is admin
#     if not user.is_admin:
#         context = {"response_code": 401, "message": "Not authorized! " + user.username + " is not an admin.",
#                    "success": "false"}
#         return JsonResponse(context, safe=False)
#     if(request.method == "POST"):
#         return False
#     if(request.method == "PUT"):
#         return False
#     if(request.method == "DELETE"):
#         return False

#  /api/altText/template?id=<id>
# 
#  returns: json data
#
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@csrf_exempt
def cacheBuilder(request):
    print("INSDIE buildCache(request)   -->   buildAltTextCache(request) ")
    user = get_user_from_token(request=request)
    if not user.is_admin:
        context = {"response_code": 401, "message": "Not authorized! " + user.username + " is not an admin.",
                   "success": "false"}
        return JsonResponse(context, safe=False)
    # READ ACCESS OPEN with API Auth Token
    if(request.method == "GET"):
        print("INSDIE buildCache(request)   -->   buildAltTextCache(request) ")
        return buildAltTextCache(request)

"""  
This function will fetch
Make a list of one item for single look up

"""
def fetchAssetsAltTexts(assetsList=[], path="/", multi=True):
    print("*****************")
    print("  def fetchAssetsAltTexts()  ")
    print("*****************")
    responseData = []
    altText = False
    for assetOrderedDict in assetsList:
        assetDict = dict(assetOrderedDict)
        altText = mongoRecallAltText(assetDict["id"], path)
        if altText and isinstance(altText, dict):
            assetDict["altText"] = altText["altText"]
        responseData.append(assetDict)
    return responseData

def fetchAssetAltTextById(assetId=False, path=False):
    print("*****************")
    print(" altTextBot.views_altText_crud_api :: fetchAssetAltTextById()  ")
    print("*****************")
    altText = False
    if path and assetId:
        altText = mongoRecallAltText(assetId, path)
    if altText and isinstance(altText, dict):
        altText = altText["altText"]
    return altText
    


"""

"""
def buildAltTextCache(request):
    print("INSIDE:  buildAltTextCache(request)")
    success = False
    error = False
    templateId = False
    overrideAltTextCache = False
    context = {}
    context["REST_VERB"] = request.method
    context["templateId"] = templateId
    context["overrideAltTextCache"] = overrideAltTextCache
    

    if request.method == 'PUT':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        context["payload"] = body
        if body["templateId"] and isinstance(body["templateId"], int):
            templateId = int(body["templateId"])
            context["templateId"] = templateId
        if overrideAltTextCache in body:
            overrideAltTextCache = int(body["overrideAltTextCache"])
            context["overrideAltTextCache"] = overrideAltTextCache

    if request.method == 'GET':
        if request.GET.get("templateId") and int(request.GET.get("templateId")) > 0:
            templateId = int(request.GET.get("templateId"))
            context["templateId"] = templateId
        if request.GET.get("overrideAltTextCache"):
            overrideAltTextCache = request.GET.get("overrideAltTextCache")
            context["overrideAltTextCache"] = overrideAltTextCache

    context["data"] = buildTextBotTemplateCache(templateId,overrideAltTextCache)
    print("DONE:: buildAltTextCache() for template: "+str(templateId))
    return JsonResponse(context, safe=False)


# ===========================================================

#  /api/altText/template-test?img=<id>
# 
#  returns: json data
#
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@csrf_exempt
def altTextTemplateTest(request):
    user = get_user_from_token(request=request)
    # READ ACCESS OPEN with API Auth Token
    if(request.method == "GET"):
        return getAllAltTextByImage(request)

"""
READ  Alt Text Template
  curl -X "GET" /api/alttext/text?altTextOnly&assetId=<int>&asCached=True
"""
def getAltText(request):
    success = False
    error = False
    REST_VERB = request.method
    data = {}
    assetId = request.GET.get('assetId')
    # Alt Text Processing
    isRecursiveMatch = False
    data = fetchAltText(assetId, request, isRecursiveMatch)
    # metadata = {
    #     'verb': REST_VERB,
    #     'success': success,
    #     'endpoint': request.META['HTTP_HOST']+request.META['PATH_INFO']+"?"+request.META['QUERY_STRING']
    # }
    return JsonResponse({'data': data}, safe=False)


"""
READ  Alt Text 
  curl -X "GET" /api/alttext/template-test?assetId=<int>
  
  RE-WORK the TESTING
  1) Process the image against altTextBot
  2) Pull all instances of altText for the given instance
  3) Display a list of results

"""
def getAllAltTextByImage(request):
    success = False
    error = False
    REST_VERB = request.method
    data = {}
    altTextResults = []
    assetId = request.GET.get('assetId')
    assetFilename = request.GET.get('filename')
    allSerializedTemplates = getAllAltTextTemplates()
    mergingResults = []
    if assetFilename:
        serialAssetData = getSerialAssetDataByFilename(assetFilename)
    else:
        serialAssetData = getSerialAssetDataById(assetId)

    for serializedTemplateData in allSerializedTemplates:
        tempId = serializedTemplateData["id"]
        path = serializedTemplateData["path"].value
        isRecursiveMatch = serializedTemplateData["isRecursive"]
        altTextResult = fetchAltTextTemplateResults(serialAssetData, request, isRecursiveMatch, path, isTest=True)      
        for resObj in altTextResult:
            if resObj not in mergingResults:
                mergingResults.append(resObj)
    metadata = {
        'verb': REST_VERB,
        'success': success,
        'endpoint': request.META['HTTP_HOST']+request.META['PATH_INFO']+"?"+request.META['QUERY_STRING']
    }
    data['metadata'] = metadata
    data['altTextTestResults'] =  mergingResults
    return JsonResponse({'data': data}, safe=False)

