from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpRequest, HttpResponse, JsonResponse
from rest_framework.authtoken.models import Token
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.views.decorators.csrf import csrf_exempt
from core.models import Asset, Option, Category, ivault_t_search, ivault_t_options, ivault_t_vals
from core.serializers import AssetSerializer
from core.functions import assetOption_stringifier, selfHealAssetOptions, update_core_ivault_t_search_and_vals, delete_core_ivault_t_search_and_vals
from core.settings import BASE_DIR
from django.db.models import Q # filter using operators '&' or '|'
from search.views import SearchAssetsOptions
from django.core.exceptions import ObjectDoesNotExist
from iv_logger.functions import commitLogEntryToDatabase, build_log_text, ensureLog
from pprint import pprint
from datetime import datetime
from django.utils import timezone
import json
import os
import inspect
from django.db import transaction

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
    """
    AUTH TOKEN RELATED
    """
    if(request.method == "GET"):
        pass
        #return fetch_assets(request)
    if(request.method == "PUT"):
        return update_assets(request)
    if(request.method == "DELETE"):
        pass
        #return delete_asset(request)

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
def update_assets(request):
    tokenKey = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
    username_authenticatedByToken = Token.objects.get(key=tokenKey).user.username
    # Testing feedback print this function and the parent who called it.
    # print("Function " + inspect.stack()[0][3] +" was called by " + inspect.stack()[1][3] + " in " + REL_PATH ) 
    context = {}  
    context["asset_id_updated"] = []
    context["asset_id_not_updated"] = []
    context["message"] = ""
    context["success"] = False
    logMode = 'default'
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    # Serializing json  
    #jsonobj = json.dumps(body, indent = 4) 
    queryString = False
    queryObj = {}
    queryObj["queryString"] = ""
    queryObj["filenameAlphaCodes"] = ""
    filenameAlphaCodes = False
    logMode = "batch"
    batch_action_data = body_unicode
    batch_action_dict = body
    context["batch_action_data"] = batch_action_dict
    if isinstance(body, dict):
        if 'logMode' in body.keys():
            logMode = body['logMode']

    if 'tags' in body:
        tags = body['tags']
        # stringafy list of tags
        #print('===TAGS===')
        #print(tags)

    if 'queryString' in body:
        queryString = body['queryString']
        queryObj["queryString"] = queryString
        #print('===queryString===')
        #print(queryString)

    if 'filenameAlphaCodes' in body:
        filenameAlphaCodes = body['filenameAlphaCodes']
        queryObj["filenameAlphaCodes"] = filenameAlphaCodes
        #print('=== filenameAlphaCodes ===')
        #print( filenameAlphaCodes )

    queryResults = SearchAssets(queryObj)
    
    # Make these queries transactional so they will roll-back if there is an error
    # Trigger atomic transaction so loop is executed in a single transaction
    with transaction.atomic():
        i = 0
        for AssetData in queryResults['searchResults']:
            #This is needed so the logger can tell the diff befor and after
            log_text_before_update = build_log_text("before update","Asset",AssetData)
            i += 1
            selfHealAssetOptions(AssetData)
            #TRANSACTION ERROR TESTING
            #if i > 10:
            #    AssetData = False
            # Ensures that a log of existing tags is created if 
            # it does not exist (for legacy migration)
            ensureLog(AssetData)
            assetOptionIds = AssetData.options.all().values_list('id', flat=True)
            # reset (disassociate) options before adding the updated options set
            assetOptions = AssetData.options.all()
            assetOptionsList = []
            assetOptionsIdList = []

            for id in assetOptionIds:
                assetOptionsIdList.append(id)
    
            for opt in assetOptions:
                assetOptionsList.append(opt)
    
            for tag in tags:               
                tagOid = tag['id']
                tagOptionObj = Option.objects.get(id=tagOid)
                
                # Check for REMOVE tag
                if tag['batchEditMode'] == 'batchAddAssetOption' and tagOid not in assetOptionIds:
                    assetOptionsList.append(tagOptionObj)
                    assetOptionsIdList.append(tagOid)

                # Check for ADD tag
                if tag['batchEditMode'] == 'batchRemoveAssetOption' and tagOid in assetOptionIds:
                    assetOptionsList.remove(tagOptionObj)
                    assetOptionsIdList.remove(tagOid)  
    
            AssetData.options.clear()

            for opt in assetOptionsList:
                AssetData.options.add(opt)
            
            AssetData.search_string = ''
            AssetData.search_string = assetOption_stringifier(assetOptionsIdList)
            AssetData.timestamp = datetime.now()
            AssetData.save()
            serializedAssetItem = AssetSerializer(AssetData, many=False)
            searialAssDat = serializedAssetItem.data
            #For backwards compatability with wellborn.com Curator
            f_name = searialAssDat['fileName'].replace("media", "").replace("/","")
            s_string = str(searialAssDat['search_string'])
            timestampIn = searialAssDat['timestamp']
            optionIds = searialAssDat['search_string'].split("--")
            print('================================')
            print('--- ivault_t_search  DATA -----')
            print('f_name = ' + f_name )
            print('s_string = ' + s_string )
            print('================================')
            # --- UPDATE core_ivault_t_search (legacy table) ----
            ivaultTSearchObject = ivault_t_search.objects.get(fileName=f_name.replace("%20", " "))
            ivaultTSearchObject.search_string = s_string
            ivaultTSearchObject.timestamp = timestampIn            
            ivaultTSearchObject.save(update_fields=['search_string','timestamp'])
            # --- UPDATE core_ivault_t_vals (legacy table) ----
            # Remove the ivault_t_vals prior to add back in the updated options
            ivaultTValsObjs = ivault_t_vals.objects.filter(fileName=f_name)
            for tValsObj in ivaultTValsObjs:
                tValsObj.delete()
            for optId in optionIds:
                if optId.strip() != "":
                    ivaultTValsObject = ivault_t_vals(fileName=f_name, optId=int(optId), selected="", option_group="", option_text="", resolution="")
                    ivaultTValsObject.save()
     
            context["asset_id_updated"].append(AssetData.id)
            #This will properly not log if transaction does not complete (tested)
            commitLogEntryToDatabase(username_authenticatedByToken, "update", "Asset", AssetData, logMode, log_text_before_update)
            commitLogEntryToDatabase(":bkwd cmpatbl updt", "bkwd cmpatbl UPDATE", "ivault_t_search", ivaultTSearchObject, "batch-edited") 
            commitLogEntryToDatabase(":bkwd cmpatbl updt", "bkwd cmpatbl UPDATE", "ivault_t_vals", ivaultTValsObject, "batch-edited")
        
        context["success"] = True
        #tokenKey = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
        
            
    

     #  Create LOG entry for the BATCH ACTION
    commitLogEntryToDatabase(username_authenticatedByToken, "BatchTagger", "BatchTagger", False, logMode, batch_action_data)           

    return JsonResponse(context, safe=False)
    #for searchResultsData in searchResults

    #if('id' in body):
    #    try:
    #        AssetData = fetch_asset(request, body["id"])
    #        log_text_before_update = build_log_text("before update","Asset",AssetData)
    #    except:
    #        context["message"] = "Error: Asset NOT FOUND for this ID!"
    #        context["success"] = "false"
    #        return JsonResponse(context, safe=False)            
    #else:
    #    context["message"] = "Error: id parameter missing!"
    #    context["success"] = "false"
    #    return JsonResponse(context, safe=False)

    #if(AssetData):
    #    serializedAssetPrev = AssetSerializer(AssetData, many=False)
    #    context["data_before_update"] = removePathFromFileName(serializedAssetPrev.data)

    #    if('fileName' in body):
    #    	AssetData.fileName = body["fileName"]
#
    #    # reset (disassociate) options before adding the updated options set
    #    AssetData.options.clear()
    #    AssetData.search_string = ''
#
    #    # Set all the new options
    #    for optId in body["options"]:
    #        if isinstance(optId, str) :
    #            optId = int(optId)
    #        print('=========PKL TEST===================')
    #        pprint(optId)
    #        print('==========PKL TEST========================')
    #        AssetData.options.add( Option.objects.get(id=optId))
#
    #    # Stringify the new options and update the s_string
    #    AssetData.search_string = assetOption_stringifier(body["options"])
#
    #    # Commit the change
    #    try:
    #        AssetData.full_clean()
    #        AssetData.save()
#
    #    except ValidationError as e:
    #        pprint(e.message_dict)
#
    #    tokenKey = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
    #    username_authenticatedByToken = Token.objects.get(key=tokenKey).user.username
    #    commitLogEntryToDatabase(username_authenticatedByToken, "update", "Asset", AssetData, logMode, log_text_before_update)
#
    #    context["success"] = "true"
    #    context["message"] = "Asset "+ str(body["id"])+" updated."
    #    serializedAsset = AssetSerializer(AssetData, many=False)
    #    context["data"] = removePathFromFileName(serializedAsset.data)
#
    #    """
    #    For backwards compatability with wellborn.com Curator
    #    """
    #    update_core_ivault_t_search_and_vals(serializedAsset.data)
#
    #else:
    #    context["message"] = "Error: unable to access this asset as queried"
    #    context["success"] = "false"
    #    return JsonResponse(context, safe=False)
#
    #context["api_path"] = request.META["PATH_INFO"]
#
    #return JsonResponse(context, safe=False)


def SearchAssets(queryObj):
    searchResults = ''
    fileNameString = ''
    queryString = ''
    queryString = queryObj['queryString']
    if( queryObj['filenameAlphaCodes'] ):
      fileNameString = queryObj['filenameAlphaCodes']

    # Turn list of values into list of Q objects
    if len(queryString) :
        if len(fileNameString) :
            fileNameParts = fileNameString.split(",")
            andedContains = Q()
            for part in fileNameParts:
                andedContains &= Q(fileName__contains=part) 
                # pprint(andedContains)
            assets = Asset.objects.filter(andedContains).order_by('fileName')
        else:
            # Initial set based on all
            assets = Asset.objects.all().order_by('fileName')
        #print('QueryString: '+ queryString)
        searchResultsData = SearchAssetsOptions(queryString, assets, 'AND')
        #serializer = AssetSerializer(searchResults, many=True)
        #print('searchResultsData')
        #pprint(searchResultsData)
        return searchResultsData