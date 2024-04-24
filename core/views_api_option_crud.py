from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.models import Option, Category
from iv_logger.functions import commitLogEntryToDatabase, build_log_text
from core.serializers import OptionSerializer
from core.functions import selfHealAssetOptions, update_core_ivault_t_options, delete_core_ivault_t_options, create_core_ivault_t_options
from django.core.exceptions import ObjectDoesNotExist
from pprint import pprint
import json
import os

"""
GET:
    GET OPTION BY DEFINITION:
    /?definition=<def>  

    GET OPTION BY ID:
    /?id=<id>  

    GET OPTIONS (plural) BY IDs :
    /?ids=<id, id, id, id ...>

    GET OPTIONS (plural) BY Group :
    /?groupName=<grp>

    GET OPTIONS (plural) BY multiple Groups :
    /?groupNames=<grp, grp,grp,grp,grp ...>

"""

"""
API OPTION ROUTER
NOTE: Need to add LOG entries functionality
"""
@api_view(["GET","POST","PUT","DELETE"])
@permission_classes([IsAuthenticated])
@csrf_exempt
def router(request):
    #print("ROUTER: (method)" + request.method)

    """
        AUTH TOKEN RELATED
    """
    #print('AUTH TOKEN RELATED')
    #pprint(request.META.get('HTTP_AUTHORIZATION'))
    tokenKey = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
    userAuthByToken = Token.objects.get(key=tokenKey).user

    if(request.method == "GET"):
        return fetch_options(request)
    if(request.method == "POST"):
        return create_option(request, userAuthByToken)
    if(request.method == "PUT"):
        return update_option(request, userAuthByToken)
    if(request.method == "DELETE"):
        return delete_option_definition(request, userAuthByToken)


"""
 CREATE OPTION 

"""
def create_option(request, userAuthByToken):
    context = {}
    logMode = 'default'
    print('POST BODY')
    groupName = request.POST.get("groupName")
    definition = request.POST.get("definition")

    if(not userAuthByToken.is_admin):
        context["message"] = "Error: Not permitted. "+ userAuthByToken.username +" is not an admin."
        context["success"] = "false" 
        pprint(context)
        return JsonResponse(context, safe=False) 


    if 'logMode' in request.POST:
        logMode = request.POST.get('logMode')

    if(len(groupName.strip()) > 0 and len(definition.strip()) > 0):
        # Test for existance
        if( Option.objects.filter(groupName=groupName, definition=definition).exists() ):
            context["message"] = "This option already exists!"
            context["error"] = "option already exists!"
            context["success"] = "false"
            return JsonResponse(context, safe=False)
        else:
            # Create new option definition
            optionObject = Option(groupName=groupName.title(), definition=definition.title())
            optionObject.save()

            #BUILD LOGGING TEXT
            lastOption = Option.objects.latest('id')
            commitLogEntryToDatabase("API:POST:Update Option","create","Option",lastOption, logMode)
            serializedOption = OptionSerializer(optionObject, many=False)

            """
            For backwards compatability with wellborn.com Curator
            """
            create_core_ivault_t_options(serializedOption.data)
            
            #BUILD RESPONSE TEXT            
            context["message"] = "Created Option!"
            context["success"] = "true"
            context["data"] = serializedOption.data
            return JsonResponse(context, safe=False) 
    else:
        context["message"] = "Error: parameter missing!"
        context["success"] = "false"
        return JsonResponse(context, safe=False) 


"""
PUT  (with params as JSON in body)
curl -X PUT -H "Content-Type: application/json" 
     -d '{ <req'd>  "id":20, 
           <optn> "groupName" :"Some_group_name", 
           <optn> "definition": "some_definition",
           <req'd>  "token": "23hf98y98y3b2y49823hb" }' 
     "http://ivault.mac/api/optiongroup/?id=20"

NOTE: This will auto stringinfy the options s_string) from the array of option IDs

"""
def update_option(request, userAuthByToken):
    context = {}
    logMode = 'default'
    print('request.META')
    pprint(request.META)   
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    print('PUT BODY')
    pprint(body)

    if(not userAuthByToken.is_admin):
        context["message"] = "Error: Not permitted. "+ userAuthByToken.username +" is not an admin."
        context["success"] = "false" 
        pprint(context)
        return JsonResponse(context, safe=False) 

    if('logMode' in body):
        logMode = body['logMode']

    if('id' in body):
    	OptionData = Option.objects.get(id=body["id"])
    	log_text_before_update = build_log_text("before update","Option",OptionData)
    else:
        context["message"] = "Error: id parameter missing!"
        context["success"] = "false"
        return JsonResponse(context, safe=False)


    if(OptionData):
        serializedOption = OptionSerializer(OptionData, many=False)
        context["data_before_update"] = serializedOption.data

        if('groupName' in body):
            OptionData.groupName = body["groupName"]

        if('definition' in body):
            OptionData.definition = body["definition"]

        # Commit the change
        OptionData.save()
        print("/////////////// USER =================")

        # Create new option definition
        commitLogEntryToDatabase("API:POST:Update Option", "update","Option", OptionData, logMode, log_text_before_update)

        """
        For backwards compatability with wellborn.com Curator
        """
        update_core_ivault_t_options(serializedOption.data)

        context["success"] = "true"
        context["message"] = "Option "+ str(body["id"])+" updated."
        serializedOption = OptionSerializer(OptionData, many=False)
        context["data"] = serializedOption.data

    else:
        context["message"] = "Error: unable to access this option as queried"
        context["success"] = "false"
        return JsonResponse(context, safe=False)

    context["api_path"] = request.META["PATH_INFO"]

    return JsonResponse(context, safe=False)


"""
DELETE By ID or groupName
  curl -X "DELETE" http://ivault.mac/api/optiongroup/?groupName=<some_group>
  curl -X "DELETE" http://ivault.mac/api/optiongroup/?id=<id>&token=23hf98y98y3b2y49823hb
  NOTE: Need to programm must be authorized to delete

  NOTE:  At this point, this deletes from dB but not the file from S3
"""
def delete_option_definition(request, userAuthByToken):
    context = {}
    oid = request.GET.get('id')

    if(not userAuthByToken.is_admin):
        context["message"] = "Error: Not permitted. "+ userAuthByToken.username +" is not an admin."
        context["success"] = "false" 
        pprint(context)
        return JsonResponse(context, safe=False) 

    if(oid):
        try:
            OptionData = Option.objects.get(id=oid)
        except ObjectDoesNotExist:
            context["error"] = ", Option " + str(oid) + " NOT found"
            context["success"] = " False "       
            context["message"] = "Error: " + str(oid) + " cannot be deleted becasue it does not exist in database!" 
            return JsonResponse(context, safe=False)
    else:
        context["message"] = "Error: id parameter missing!"
        context["success"] = "false"
        return JsonResponse(context, safe=False)

    if(OptionData):
        serializedOption = OptionSerializer(OptionData, many=False)
        commitLogEntryToDatabase("API:POST:Update Option","delete","Option",OptionData)

        OptionData.delete()

        """
        For backwards compatability with wellborn.com Curator
        """
        delete_core_ivault_t_options(serializedOption.data)

        context["message"] ="Option definition deleted"
        context["success"] = "true"
        context["deleted_group_data"] = serializedOption.data
        return JsonResponse(context, safe=False)
    else:
    	context["message"] = "Error: unable to access this option as queried"
    	context["success"] = "false"
    	return JsonResponse(context, safe=False)
        



"""
////////////////////////
   UTILITY FUNCTIONS
////////////////////////
"""

def fetch_options(request):
    context = {}
    if(request.GET.get('id')):
        ogid = request.GET.get('id')
        return get_single_option_grouping_by_param(ogid, grpName=None)
    elif(request.GET.get('definition')):
        optdef = request.GET.get('definition')
        return get_single_option_by_definition(optdef)
    elif(request.GET.get('ids')):
        stringOfIds = request.GET.get('ids')
        return fetch_options_by_ids_string(stringOfIds)
    elif(request.GET.get('groupName')):
        grpName = request.GET.get('groupName')
        ogid = None
        return get_single_option_grouping_by_param(ogid, grpName)
    elif(request.GET.get('groupNames')):
        stringOfGroupNames = request.GET.get('groupNames')
        return fetch_options_by_groupnames_string(stringOfGroupNames)
    context["message"] = "Error: unable to access this option as queried"
    context["success"] = "false"
    return JsonResponse(context, safe=False)

"""
GET SINGLE FILE Option
eg. api call
    curl -X "GET" http://ivault.mac/api/optiongroup/?definition=oak
"""
def get_single_option_by_definition(optionDef):
    context = {}
    print("====>  get_single_option_by_definition(optDef)" + optionDef)
    OptionData = Option.objects.get(definition=optionDef)

    if(OptionData):
        serializedOption = OptionSerializer(OptionData, many=False)
        context["data"] = serializedOption.data
        context["success"] = "true"
        return JsonResponse(context, safe=False)
    else:
        context["message"] = "Error: unable to access this option as queried"
        context["success"] = "false"
        return JsonResponse(context, safe=False)


def fetch_options_by_ids_string(gnString, sep=","):
    optionObjects = []
    optionIds = []
    context = {}
    context["success"] = ""
    context["message"] = ""
    context["count"] = ""
    context["error"] = ""
    count = 0
    optionGroupNames = []
    optionGroupIdsArray = gnString.split(sep)
    for ogid in optionGroupIdsArray:
        try:
            optionGrouping = fetch_option_grouping(ogid, optionGroupName=None)
            if(optionGrouping):
                for optDat in optionGrouping:
                    serializedOption = OptionSerializer(optDat, many=False)
                    serializedOptionData = serializedOption.data
                    optionObjects.append(serializedOptionData) 
                    optionIds.append(serializedOptionData['id'])
                    if serializedOptionData["groupName"] not in optionGroupNames:
                        optionGroupNames.append(serializedOptionData["groupName"])
                    count = count + 1
                context["success"] += " True "
                context["message"] += ", Option " + str(serializedOptionData["id"]) + " found"
            #else:
            #	context["message"] += ", Option, " + str(ogid) + " NOT found"
            #	context["success"] += " False "

        except ObjectDoesNotExist:
            context["error"] += ", Option " + str(ogid) + " NOT found"
            context["success"] += " False "

    context["data"] = optionObjects
    context["ids"] = optionIds
    context["optionGroupNames"] = optionGroupNames
    context["count"] = count
    context["success"] = "true"
    return JsonResponse(context, safe=False)   

def fetch_options_by_groupnames_string(gnString, sep=",", asJsonResponse=True):
    optionObjects = []
    optionIds = []
    context = {}
    context["success"] = ""
    context["message"] = ""
    context["count"] = ""
    context["error"] = ""
    count = 0
    optionGroupNames = []
    optionFnamesArray = []
    if isinstance(gnString ,str):
        optionFnamesArray = str(gnString).split(sep)
    for optionGroupName in optionFnamesArray:
        optionGroupName.replace("_"," ")
        optionGroupName.replace("%20"," ")
        try:
            grpId=None
            optionGrouping = fetch_option_grouping(grpId, optionGroupName)
            if(optionGrouping):
                for optDat in optionGrouping:
                    serializedOption = OptionSerializer(optDat, many=False)
                    serializedOptionData = serializedOption.data
                    optionObjects.append(serializedOptionData) 
                    optionIds.append(serializedOptionData['id'])
                    if serializedOptionData["groupName"] not in optionGroupNames:
                        optionGroupNames.append(serializedOptionData["groupName"])
                    count = count + 1

            context["success"] += "indeterminate"
            context["message"] += ", Option object, " + optionGroupName + " found"
        except ObjectDoesNotExist:
            context["error"] += ", Option object, " + optionGroupName + " NOT found"

    context["data"] = optionObjects
    context["ids"] = optionIds
    context["optionGroupNames"] = optionGroupNames
    context["count"] = count
    context["success"] = "true"
    if asJsonResponse:
        return JsonResponse(context, safe=False) 
    else:
        return context

"""
GET SINGLE FILE Option
eg. api call
    curl -X "GET" http://ivault.mac/api/optiongroup/?id=17
"""
def get_single_option_grouping_by_param(grpId, grpName):
    context = {}
    serializedOptionData = []
    OptionData = fetch_option_grouping(grpId, grpName)

    if(OptionData):
        for optDat in OptionData:
            serializedOption = OptionSerializer(optDat, many=False)
            serializedOptionData.append(serializedOption.data)
        context["data"] = serializedOptionData
        context["success"] = "true"
        return JsonResponse(context, safe=False)
    else:
        context["message"] = "Error: unable to access this option as queried"
        context["success"] = "false"
        return JsonResponse(context, safe=False)




def fetch_option_grouping(optionId=None, optionGroupName=None):

    if(optionId):
        try:
            options  = Option.objects.filter(id=optionId)
            return options
        except ObjectDoesNotExist:
            return False

    if(optionGroupName):
        try:
            optionGroupName = optionGroupName.replace("_"," ")
            optionGroupName = optionGroupName.replace("%20"," ")
            options  = Option.objects.filter(groupName=optionGroupName).order_by('definition')
            return options
        except ObjectDoesNotExist:
            return False
    
    return False




