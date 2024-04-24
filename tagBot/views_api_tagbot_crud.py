from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from tagBot.models import TagBotModes, TagBotMapping
from iv_logger.functions import commitLogEntryToDatabase, build_log_text
from tagBot.serializers import TagBotMappingSerializer
from tagBot.functions import process_filename_codes

from pprint import pprint
import json
import os

"""
GET:
    GET RULE BY :
    /?=<alphacode>  

    GET RULE BY ID:
    /?id=<id>  

    GET RULESS (plural) BY IDs :
    /?ids=<id, id, id, id ...>

    GET RULES (plural) BY multiple alpha code :
    /?groupNames=<alphacode,alphacode,alphacode ...>

"""



"""
API OPTION ROUTER
NOTE: Need to add LOG entries functionality
"""
@api_view(["GET","POST","PUT","DELETE"])
@permission_classes([IsAuthenticated])
@csrf_exempt
def router(request):
    # print("ROUTER: (method)" + request.method)

    """
        AUTH TOKEN RELATED
    """
    #print('AUTH TOKEN RELATED')
    #pprint(request.META.get('HTTP_AUTHORIZATION'))
    tokenKey = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
    userByToken = Token.objects.get(key=tokenKey).user

    if(request.method == "GET"):
        return fetch_tagbot_map(request)
    if(request.method == "POST"):
        return create_tagbot_mapping(request, userByToken)
    if(request.method == "PUT"):
        return update_tagbot_map(request, userByToken)
    if(request.method == "DELETE"):
        print('INSIDE tagBOT :DELETE')
        return delete_tagBotMap(request, userByToken)


"""
 UPDATE (PUT) tagBot Map 
 params: id, nomenclature, logic, mode_id, option_ids
"""
def update_tagbot_map(request, userAuthByToken):
    context = {}  
    logMode = 'tagBot_rules'

    if(not userAuthByToken.is_admin):
        context["message"] = "Error: Not permitted. "+ userAuthByToken.username +" is not an admin."
        context["success"] = "false" 
        pprint(context)
        return JsonResponse(context, safe=False) 

    pprint(request.body)
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    print("== INSIDE:  def update_tagbot_map")

    if('id' in body):
        tmid = body["id"]
        try:
            tagBotObj  = TagBotMapping.objects.get(id=int(tmid))
            serializedTagBotMap = TagBotMappingSerializer(tagBotObj, many=False)
            log_text_before_update = build_log_text("before update","tagBot Map",tagBotObj)
        except:
            context["message"] = "Error: tagBot Map NOT FOUND for this ID!"
            context["success"] = False
            return JsonResponse(context, safe=False)            
    else:
        context["message"] = "Error: id parameter missing! or JSON may be malformed."
        context["error"] = "Error: id parameter missing! or JSON may be malformed."
        context["success"] = False
        return JsonResponse(context, safe=False)

    if(tagBotObj):
        serializedTagBotObjPrev = TagBotMappingSerializer(tagBotObj, many=False)
        context["data_before_update"] = serializedTagBotObjPrev.data

        if('nomenclature' in body):
            print("body nomenclature ...")
            pprint(type(body["nomenclature"]))
            pprint(body["nomenclature"])
            tagBotObj.nomenclature = body["nomenclature"].strip()

        if('logic' in body):
            print("body logic ...")
            pprint(type(body["logic"]))
            pprint(body["logic"])
            tagBotObj.logic = body["logic"].strip()

        if('mode' in body):
            print("body modec ...")
            pprint(type(body['mode']))
            pprint(body['mode'])
            mode_id = int(body['mode'])
            TagBotModeObj = TagBotModes.objects.get(id=mode_id)
            tagBotObj.mode = TagBotModeObj

        if('optionIds' in body):
            print("body optionIds ...")
            pprint(type(body["optionIds"]))
            tagBotObj.optionIds = body["optionIds"].strip()

        # Commit the change
        try:
            tagBotObj.full_clean()
            tagBotObj.save()

        except ValidationError as e:
            pprint(e.message_dict)

        tokenKey = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
        username_authenticatedByToken = Token.objects.get(key=tokenKey).user.username
        commitLogEntryToDatabase(username_authenticatedByToken, "update", "tagBot Map", tagBotObj, logMode, log_text_before_update)

        context["success"] = True
        context["message"] = "tagBotObj Map "+ str(body["id"])+" updated."
        serializedTagBotMap = TagBotMappingSerializer(tagBotObj, many=False)
        context["data"] = serializedTagBotMap.data

    else:
        context["message"] = "Error: unable to access this tagBot Map as queried"
        context["error"] = "Error: unable to access this tagBot Map as queried"
        context["success"] = False
        return JsonResponse(context, safe=False)

    context["api_path"] = request.META["PATH_INFO"]

    return JsonResponse(context, safe=False)


"""
 GET OPTION 
 params: tmid
"""
def fetch_tagbot_map(request):
    context = {}
    logMode = 'tagBot_rules'
    count = 0
    data = []
    if(request.GET.get('id')):
        tmid = request.GET.get('id')
        if(tmid):
            try:
                tagBotObj  = TagBotMapping.objects.get(id=int(tmid))
                TagBotModeObj = TagBotModes.objects.get(id=int(tagBotObj.mode.id))
                #print('TagBotModeObj')
                #pprint(TagBotModeObj)
                serializedTagBotMap = TagBotMappingSerializer(tagBotObj, many=False)
                tagBotMapData = serializedTagBotMap.data
                tagBotMapData['mode'] = {"id":TagBotModeObj.id, 'name': TagBotModeObj.name}
                context["data"] = tagBotMapData
                context["success"] = True
                return JsonResponse(context, safe=False) 
            except ObjectDoesNotExist:
                context["data"] = []
                context["success"] = False
                context["error"] = "Object does not exist"
                return JsonResponse(context, safe=False) 

    else:
        try:
            tagBotObjs  = TagBotMapping.objects.all()
            for tagBotObj in tagBotObjs:
                TagBotModeObj = TagBotModes.objects.get(id=int(tagBotObj.mode.id))
                #print('TagBotModeObj')
                #pprint(TagBotModeObj.name)
                serializedTagBotMap = TagBotMappingSerializer(tagBotObj, many=False)
                tagBotMapData = serializedTagBotMap.data
                tagBotMapData['mode'] = {"id":TagBotModeObj.id, 'name': TagBotModeObj.name}
                data.append(tagBotMapData)
            
            context["count"] = len(data)
            context["success"] = True
            context["data"] = data
            
            return JsonResponse(context, safe=False) 
                
        except ObjectDoesNotExist:
            context["data"] = []
            context["success"] = False
            context["error"] = "Object does not exist"
            return JsonResponse(context, safe=False) 

    context["message"] = "Error id parameter missing!"
    context["error"] = "Error id parameter missing!"
    context["success"] = False
    return JsonResponse(context, safe=False) 


"""
 CREATE OPTION 
 params: nomenclature, logic, mode_id, option_ids
"""
def create_tagbot_mapping(request, userAuthByToken):
    context = {}
    logMode = 'tagBot_rules'
    nomenclature = ''
    logic = ''
    mode_id = ''
    option_ids = ''
    print('INSIDE tagBOT POST')
    pprint(json.loads(request.body.decode("utf-8")))
    payload = json.loads(request.body.decode("utf-8"))

    if(not userAuthByToken.is_admin):
        context["message"] = "Error: Not permitted. "+ userAuthByToken.username +" is not an admin."
        context["success"] = "false" 
        pprint(context)
        return JsonResponse(context, safe=False) 

    if(request.method == 'POST'):
        if(payload['nomenclature']):
            nomenclature = payload['nomenclature']
        if(payload['logic']):
            logic = payload['logic']
        if 'mode' in payload:
            mode_id = payload['mode']
        else:
            mode_id = 1;

        if(payload['optionIds']):
            option_ids = payload['optionIds']

    print('nomenclature: ' + nomenclature)
    print('Mode_id: ' + str(mode_id))
    print('logic: ' + logic)
    print('option_ids: ' + str(option_ids))


    # Check for nomenclature
    if(len(nomenclature.strip()) > 0):
        # Test for nomenclature existance
        if( nomenclature != '~LOGIC' and TagBotMapping.objects.filter(nomenclature=nomenclature).exists() ):
            context["message"] = "This tagBot Mapping Nomenclature already exists!"
            context["error"] = "tagBot Mapping Nomenclature already exists!"
            context["success"] = False
            return JsonResponse(context, safe=False)
        elif(len(logic.strip()) > 0 and TagBotMapping.objects.filter(logic=logic.strip()).exists()):
            context["message"] = "This tagBot Mapping LOGIC already exists!"
            context["error"] = "tagBot Mapping LOGIC already exists!"
            context["success"] = False
            return JsonResponse(context, safe=False)
        else:
            # Create new option definition
            
            TagBotModesObj = TagBotModes.objects.get(id=int(mode_id))
            TagBotMappingObj = TagBotMapping(nomenclature=nomenclature.strip(), logic=logic.strip(), mode=TagBotModesObj, optionIds=option_ids)
            TagBotMappingObj.save()

            #BUILD LOGGING TEXT
            lastTagBotMapping =TagBotMapping.objects.latest('id')
            commitLogEntryToDatabase("API:POST:Create TagBotMappingObj","create","TagBotMappingObj",lastTagBotMapping, logMode)
            serializedTagBotMapping = TagBotMappingSerializer(TagBotMappingObj, many=False)
            
            #BUILD RESPONSE TEXT            
            context["message"] = "Created TagBot Mapping!"
            context["success"] = True
            context["data"] = serializedTagBotMapping.data
            return JsonResponse(context, safe=False) 
    else:
        context["message"] = "Error: parameter missing!"
        context["error"] = "Error: parameter missing!"
        context["success"] = False
        return JsonResponse(context, safe=False) 


"""
   DELETE By ID or groupName
   curl -X "DELETE" http://ivault.mac/api/optiongroup/?groupName=<some_group>
   curl -X "DELETE" http://ivault.mac/api/optiongroup/?id=<id>&token=23hf98y98y3b2y49823hb
   NOTE: Need to programm must be authorized to delete
 
   NOTE:  At this point, this deletes from dB but not the file from S3
"""
def delete_tagBotMap(request, userAuthByToken):
    context = {}
    logMode = 'tagBot_rules'
    tmid = request.GET.get('tmid')

    if(not userAuthByToken.is_admin):
        context["message"] = "Error: Not permitted. "+ userAuthByToken.username +" is not an admin."
        context["success"] = "false" 
        pprint(context)
        return JsonResponse(context, safe=False) 

    if(tmid):
        try:
            TagBotMappingObj = TagBotMapping.objects.get(id=tmid)
        except ObjectDoesNotExist:
            context["error"] = ", TagBotMappingn " + str(tmid) + " NOT found"
            context["success"] = False       
            context["message"] = "Error: " + str(tmid) + " cannot be deleted becasue it does not exist in database!" 
            return JsonResponse(context, safe=False)
    else:
        context["message"] = "Error: id parameter missing!"
        context["success"] = False
        return JsonResponse(context, safe=False)

    if(TagBotMappingObj):
        serializedTagBotMap = TagBotMappingSerializer(TagBotMappingObj, many=False)
        commitLogEntryToDatabase("API:POST:DELETE TagBotMapping","delete","TagBotMapping",TagBotMappingObj, logMode)

        TagBotMappingObj.delete()

        context["message"] ="TagBotMapping deleted"
        context["success"] = True
        context["deleted_tagBotMap"] = serializedTagBotMap.data
        return JsonResponse(context, safe=False)
    else:
        context["message"] = "Error: unable to access this TagBotMapping as queried"
        context["success"] = False
        return JsonResponse(context, safe=False)
         
 
 
 
# """
# ////////////////////////
#    UTILITY FUNCTIONS
# ////////////////////////
# """
