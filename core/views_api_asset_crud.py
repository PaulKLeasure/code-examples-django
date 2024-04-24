from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpRequest, HttpResponse, JsonResponse
from rest_framework.authtoken.models import Token
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.views.decorators.csrf import csrf_exempt
from core.models import Asset, Option, Category
from core.serializers import AssetSerializer
from core.functions import assetOption_stringifier, selfHealAssetOptions, update_core_ivault_t_search_and_vals, delete_core_ivault_t_search_and_vals
from core.settings import BASE_DIR
from altTextBot.functions import fetchAltText
from django.core.exceptions import ObjectDoesNotExist
from iv_logger.functions import commitLogEntryToDatabase, build_log_text, ensureLog
from altTextBot.views_altText_crud_api import fetchAssetsAltTexts, fetchAssetAltTextById
from pprint import pprint
from datetime import datetime
import json
import os
import inspect

# Setup Relative path for feedback
os.chdir(os.path.dirname(__file__))
REL_PATH = __file__.replace(BASE_DIR, '')


"""
API ASSET ROUTER

NOTE:  TO ADD SINGLE FILE ASSET, USE UPLOADER
       See: uploader.views_api.api_process_asset_upload

NOTE: Need to add LOG entries functionality

"""
@api_view(["GET","PUT","DELETE"])
@csrf_exempt
def router(request):
    # Testing feedback print this function and the parent who called it.
    # print("Function " + inspect.stack()[0][3] +" was called by " + inspect.stack()[1][3] +" in " + REL_PATH )
    # print('    Request Headers:', request.headers)

    """
    AUTH TOKEN RELATED
    """
    #print('AUTH TOKEN RELATED')
    #pprint(request.META.get('HTTP_AUTHORIZATION'))
    tokenKey = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
    userByToken = Token.objects.get(key=tokenKey).user

    if(request.method == "GET"):
        print("*****************")
        print(" core.views_api_asset_crud :: router()  ")
        print("*****************")
        return fetch_assets(request)
    if(request.method == "PUT"):
        return update_asset(request, userByToken)
    if(request.method == "DELETE"):
        return delete_asset(request, userByToken)



"""
PUT  (with params as JSON in body)
curl -X PUT -H "Content-Type: application/json" 
     -d '{ <req'd>  "id":20, 
           <optn> "fileName" :"Some_file_name", 
           <optn> "options": [232,72,459,2225],
           <req'd>  "token": "23hf98y98y3b2y49823hb" }' 
     "http://ivault.mac/api/asset/?id=20"

    NOTE: This will auto stringinfy the options s_string) from the array of option IDs
"""
def update_asset(request, userAuthByToken):

    # Testing feedback print this function and the parent who called it.
    # print("Function " + inspect.stack()[0][3] +" was called by " + inspect.stack()[1][3] + " in " + REL_PATH ) 
    context = {}  
    logMode = 'default'
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    if(not userAuthByToken.is_admin):
        context["message"] = "Error: Not permitted. "+ userAuthByToken.username +" is not an admin."
        context["success"] = "false" 
        #pprint(context)
        return JsonResponse(context, safe=False) 

    if isinstance(body, dict):
        if 'logMode' in body.keys():
            logMode = body['logMode']

    if('id' in body):
        try:
            AssetData = fetch_asset(request, body["id"])
            log_text_before_update = build_log_text("before update","Asset",AssetData)
        except:
            context["message"] = "Error: Asset NOT FOUND for this ID!"
            context["success"] = "false"
            return JsonResponse(context, safe=False)            
    else:
        context["message"] = "Error: id parameter missing!"
        context["success"] = "false"
        return JsonResponse(context, safe=False)

    if(AssetData):
        serializedAssetPrev = AssetSerializer(AssetData, many=False)
        context["data_before_update"] = removePathFromFileName(serializedAssetPrev.data)

        if('fileName' in body):
        	AssetData.fileName = body["fileName"]

        # reset (disassociate) options before adding the updated options set
        AssetData.options.clear()
        AssetData.search_string = ''

        # Set all the new options
        for optId in body["options"]:
            if isinstance(optId, str) :
                optId = int(optId)
            #print('=========PKL TEST===================')
            #pprint(optId)
            #print('==========PKL TEST========================')
            AssetData.options.add( Option.objects.get(id=optId))

        # Stringify the new options and update the s_string
        AssetData.search_string = assetOption_stringifier(body["options"])

        # Commit the change
        try:
            AssetData.full_clean()
            AssetData.save()

        except ValidationError as e:
            pprint(e.message_dict)

        tokenKey = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
        commitLogEntryToDatabase(userAuthByToken.username, "update", "Asset", AssetData, logMode, log_text_before_update)

        context["success"] = "true"
        context["message"] = "Asset "+ str(body["id"])+" updated."
        serializedAsset = AssetSerializer(AssetData, many=False)
        context["data"] = removePathFromFileName(serializedAsset.data)

        """
        For backwards compatability with wellborn.com Curator
        """
        update_core_ivault_t_search_and_vals(serializedAsset.data)

    else:
        context["message"] = "Error: unable to access this asset as queried"
        context["success"] = "false"
        return JsonResponse(context, safe=False)

    context["api_path"] = request.META["PATH_INFO"]

    return JsonResponse(context, safe=False)


"""
DELETE By ID or fileName
  curl -X "DELETE" http://ivault.mac/testapi/asset/?fileName=(9C)-Open_R1_72m.jpg
  curl -X "DELETE" http://ivault.mac/testapi/asset/?id=<id>&token=23hf98y98y3b2y49823hb
  NOTE:
  settings.S3_TRASH_URI  exist for delting files without loosing them.
"""
def delete_asset(request, userAuthByToken):
    # Testing feedback print this function and the parent who called it.
    # print("Function " + inspect.stack()[0][3] +" was called by " + inspect.stack()[1][3] + " in " + REL_PATH) 
    context = {}
    logMode = "default"
    #AssetData = fetch_asset(request)
    aid = request.GET.get('id')

    if(not userAuthByToken.is_admin):
        context["message"] = "Error: Not permitted. "+ userAuthByToken.username +" is not an admin."
        context["success"] = "false" 
        #pprint(context)
        return JsonResponse(context, safe=False)       

    if 'logMode' in request.GET:
        logMode = request.GET.get('logMode')

    if(aid):
        try:
            AssetData = Asset.objects.get(id=aid)
        except ObjectDoesNotExist:
            context["error"] = "Asset " + str(aid) + " NOT found"
            context["success"] = " False "       
            context["message"] = "Error: " + str(aid) + " cannot be deleted becasue it does not exist in database!" 
            return JsonResponse(context, safe=False)
    else:
        context["message"] = "Error: id parameter missing!"
        context["success"] = "false"
        return JsonResponse(context, safe=False)

    if(AssetData):
        serializedAsset = AssetSerializer(AssetData, many=False)
        commitLogEntryToDatabase(userAuthByToken.username, "delete", "Asset", AssetData, logMode)
        context["deleted_file_data"] = removePathFromFileName(serializedAsset.data)
        """
        For backwards compatability with wellborn.com Curator
        """
        delete_core_ivault_t_search_and_vals(serializedAsset.data)
        AssetData.delete()
        context["message"] ="File deleted by "+ userAuthByToken.username +"."
        context["success"] = "true"
        return JsonResponse(context, safe=False)
    else:
    	context["message"] = "Error: unable to access this asset as queried"
    	context["success"] = "false"
    	return JsonResponse(context, safe=False)
        

"""
GET SINGLE FILE ASSET
eg. api call
    curl -X "GET" http://ivault.mac/testapi/asset/?id=17

NOTE: In order for the result to include appropriate alt text data for each image,
      include a "path" prameter in the API call.
      eg. api call
      curl -X "GET" http://ivault.mac/testapi/asset/?id=17&path=/<some-path>

"""
def get_single_asset_by_param(request):
 
    # Testing feedback print this function and the parent who called it.
    print("Function " + inspect.stack()[0][3] +" was called by " + inspect.stack()[1][3] + " in " + REL_PATH ) 

    context = {}
    AssetData = fetch_asset(request)

    # Alt Text Processing
    if(request.GET.get('path') or request.GET.get("testAltTextPath")):
        context["altText"] = fetchAssetAltTextById(AssetData.id, request.GET.get('path'))
    if(request.GET.get("testAltTextPath")):
        context["altText"] = fetchAssetAltTextById(AssetData.id, request.GET.get("testAltTextPath"))


    if(AssetData):

        # Make sure that the relationship is maintained in the
        # core_asset_options relational db table post migration
        #selfHealAssetOptions(AssetData)         
        
        # Ensures that a log of existing tags is created if 
        # it does not exist (for legacy migration)
        ensureLog(AssetData)

        serializedAsset = AssetSerializer(AssetData, many=False)
        print("== GET ASSET  context======")
        pprint(context)
        context["data"] = removePathFromFileName(serializedAsset.data)
        context["success"] = "true"

        
        return JsonResponse(context, safe=False)
    else:
        context["message"] = "Error: unable to access this asset as queried in get_single_asset_by_param(request) in " + REL_PATH 
        context["success"] = "false"
        #print('=-=-=-=-=-=-=-=-=-=')
        #print('get_single_asset_by_param:context')
        #pprint(context)

        return JsonResponse(context)


"""
////////////////////////
   UTILITY FUNCTIONS
////////////////////////
"""


def fetch_assets(request):
    
    # Testing feedback print this function and the parent who called it.
    # print("Function " + inspect.stack()[0][3] +" was called by " + inspect.stack()[1][3] + " in " + REL_PATH ) 

    context = {}
    if(request.GET.get('id')):
        print("*****************")
        print(" core.views_api_asset_crud :: router(GET[id])  ")
        print("*****************")
        return get_single_asset_by_param(request)
    elif(request.GET.get('ids')):
        stringOfIds = request.GET.get('ids')
        return fetch_assets_by_ids_string(request, stringOfIds)
    elif(request.GET.get('fileName')):
        fileName = request.GET.get('fileName')
        return get_single_asset_by_param(request)
    elif(request.GET.get('fileNames')):
    	stringOfFileNames = request.GET.get('fileNames')
    	return fetch_assets_by_filenames_string(request, stringOfFileNames)
    
    context["message"] = "Error: unable to access this asset as queried in fetch_assets(request) " + REL_PATH
    context["success"] = "false"
    return JsonResponse(context, safe=False)


def fetch_assets_by_ids_string(request, idsString, sep=","):
    
    # Testing feedback print this function and the parent who called it.
    # print("Function " + inspect.stack()[0][3] +" was called by " + inspect.stack()[1][3] + " in " + REL_PATH ) 

    assetObjects = []
    assetIds = []
    context = {}
    context["success"] = ""
    context["message"] = ""
    context["count"] = ""
    context["error"] = ""
    count = 0
    assetFileNames = []
    assetIdArray = idsString.split(sep)
    for assetId in assetIdArray:
        try:
            assetObj = Asset.objects.get(id=assetId)
            # Make sure that the relationship is maintained in the
            # core_asset_options relational db table post migration
            #selfHealAssetOptions(assetObj) 

            # Ensures that a log of existing tags is created if 
            # it does not exist (for legacy migration)
            ensureLog(assetObj)            

            serializedassetObj = AssetSerializer(assetObj, many=False)
            serializedAssetData = removePathFromFileName(serializedassetObj.data)
            # Alt Text Processing
            if(request.GET.get('path')):
                serializedAssetData["altText"] = fetchAssetAltTextById(serializedAssetData["id"], request.GET.get('path'))
            if(request.GET.get("testAltTextPath")):
                context["altText"] = fetchAssetAltTextById(AssetData.id, request.GET.get("testAltTextPath"))
            assetObjects.append(serializedAssetData) 
            assetIds.append(int(assetId))
            count = count + 1
            assetFileNames.append(serializedAssetData["fileName"])
            context["success"] += "indeterminate"
            context["message"] += ", Asset object, " + str(assetId) + " found"
        except ObjectDoesNotExist:
            context["error"] += ", Asset object NOT found in fetch_assets_by_ids_string() " + REL_PATH 

    context["data"] = assetObjects
    context["ids"] = assetIds
    context["assetFileNames"] = assetFileNames
    context["count"] = count
    context["success"] = "true"
    return JsonResponse(context, safe=False)    


def fetch_assets_by_filenames_string(request, fnString, sep=","):
    
    # Testing feedback print this function and the parent who called it.
    print("Function " + inspect.stack()[0][3] +" was called by " + inspect.stack()[1][3] + " in " + REL_PATH ) 

    assetObjects = []
    assetIds = []
    context = {}
    context["success"] = ""
    context["message"] = ""
    context["count"] = ""
    context["error"] = ""
    count = 0
    assetFileNames = []
    assetFnamesArray = fnString.split(sep)
    for assetFileName in assetFnamesArray:
        try:
            assetObj = Asset.objects.get(fileName=assetFileName)

            # Make sure that the relationship is maintained in the
            # core_asset_options relational db table post migration
            #selfHealAssetOptions(assetObj) 

            # Ensures that a log of existing tags is created if 
            # it does not exist (for legacy migration)
            ensureLog(assetObj)    

            serializedassetObj = AssetSerializer(assetObj, many=False)
            serializedAssetData = removePathFromFileName(serializedassetObj.data)
            # Alt Text Processing
            if(request.GET.get('path')):
                serializedAssetData["altText"] = fetchAssetAltTextById(serializedAssetData["id"], request.GET.get('path'))
            if(request.GET.get("testAltTextPath")):
                context["altText"] = fetchAssetAltTextById(AssetData.id, request.GET.get("testAltTextPath"))
            assetObjects.append(serializedAssetData) 
            assetIds.append(serializedAssetData['id'])
            count = count + 1
            assetFileNames.append(serializedAssetData["fileName"])
            context["success"] += "indeterminate"
            context["message"] += ", Asset object, " + str(assetFileName) + " found"
        except ObjectDoesNotExist:
            context["error"] += ", Asset object NOT found in fetch_assets_by_filenames_string(fnString, sep=",") " + REL_PATH

    context["data"] = assetObjects
    context["ids"] = assetIds
    context["assetFileNames"] = assetFileNames
    context["count"] = count
    context["success"] = "true"
    return JsonResponse(context, safe=False) 

def fetch_asset(request, assetId=None, fileName=None):
    context = {}
    # Testing feedback print this function and the parent who called it.
    print("Function " + inspect.stack()[0][3] +" was called by " + inspect.stack()[1][3] + " in " + REL_PATH ) 

    if(assetId or request.GET.get('id')):
        if(not assetId):
            assetId = request.GET.get('id')
        try:
            AssetData =  Asset.objects.get(id=assetId)
            # Make sure that the relationship is maintained in the
            # core_asset_options relational db table post migration
            selfHealAssetOptions(AssetData)   
            return AssetData
        except ObjectDoesNotExist:
            return False
    if(fileName or request.GET.get('fileName')):
        if(not fileName):
            fileName = request.GET.get('fileName')
        try:
            fileName.replace("%20", " ")
            AssetData = Asset.objects.get(fileName=fileName)
            # Make sure that the relationship is maintained in the
            # core_asset_options relational db table post migration
            selfHealAssetOptions(AssetData)   
            return AssetData
        except ObjectDoesNotExist:
            context["error"] += " File does not exist in fetch_asset(request, assetId, fileName) " + os.getcwd()
            return False
    
    return False

def removePathFromFileName(data):
    # Testing feedback print this function and the parent who called it.
    # print("Function " + inspect.stack()[0][3] +" was called by " + inspect.stack()[1][3] + " in " + REL_PATH ) 

    if data["fileName"]:
        fileNameWithPath = data["fileName"]
    else:
        fileNameWithPath = 'NULL-filename-in-database.jpg'
        
    fileNameWithNoPath = os.path.basename(fileNameWithPath)
    data["fileName"] = fileNameWithNoPath
    return data



