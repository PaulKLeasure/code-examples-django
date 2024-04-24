from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Cast
from django.core.exceptions import ObjectDoesNotExist
from .models import AltTextTemplate, AltTextCache
from .paging import get_page
from .functions import fetchAltText
from .serializers import AltTextTemplateSerializer, AltTextCacheSerializer
from datetime import datetime
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
@api_view(["POST","GET","PUT","DELETE"])
@permission_classes([IsAuthenticated])
@csrf_exempt
def altTextTemplate(request):
    user = get_user_from_token(request=request)
    # READ ACCESS OPEN with API Auth Token
    if(request.method == "GET"):
        return getAltTextTemplate(request)
    # "POST","PUT","DELETE" Only authorized for user is admin
    if not user.is_admin:
        context = {"response_code": 401, "message": "Not authorized! " + user.username + " is not an admin.",
                   "success": "false"}
        return JsonResponse(context, safe=False)
    if(request.method == "POST"):
        return createAltTextTemplate(request)
    if(request.method == "PUT"):
        return updateAltTextTemplate(request)
    if(request.method == "DELETE"):
        return deleteAltTextTemplate(request)

"""
CREATE  Alt Text Template
  curl -X "POST" /api/alttext/template
  body {
    path = "/..."
    requiredIds = [n,n,n,...]
    grpHeader = str
    recursive = boole
    template = str with tokens  like {{ token }}
  }
"""
def createAltTextTemplate(request):
    success = False
    error = False
    REST_VERB = request.method
    altTextData = {}
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    try:
        # Create Object
        altTextObject = AltTextTemplate()
        altTextObject.path = "none"
        altTextObject.requiredIds = []
        altTextObject.isRecursive = False
        altTextObject.grpHeader = "none"
        altTextObject.template = "none"
        

        print(" ==== PRE SAVED  BODY: ")
        pprint(body)
        
        if len(body["path"]) > 0:
             altTextObject.path = body["path"]
        if len(body["requiredIds"]) > 0:
             altTextObject.requiredIds = body["requiredIds"]
        if len(body["grpHeader"]) > 0:
             altTextObject.grpHeader = body["grpHeader"]
        if isinstance(body["isRecursive"], (bool)):
             altTextObject.isRecursive = body["isRecursive"]
        if len(body["template"]) > 0:
             altTextObject.template = body["template"]
        
        #altTextObject.timestamp = datetime.now()

        print(" ==== PRE SAVED   altTextObject: ")
        pprint(altTextObject)

        # Commit the change
        altTextObject.save()
        altTextSerialized = AltTextTemplateSerializer(altTextObject, many=False)
        altTextData = altTextSerialized.data
        success = True    
    except Exception as e: 
            message = traceback.format_exc()
            print(message)
            error = "Failed to fetch Filter Group object" + message
            print(error)
            success = False
            count = 0 

    metadata = {
        'verb': REST_VERB,
        'success': success,
        'endpoint': request.META['HTTP_HOST']+request.META['PATH_INFO']+"?"+request.META['QUERY_STRING']
        }
    if error:
        metadata["error"] = error

    return JsonResponse({'metadata': metadata, 'data':  altTextData}, safe=False)

"""
READ  Alt Text Template
  curl -X "GET" /api/alttext/template?id=<int>
  curl -X "GET" /api/alttext/template?page=<int>
"""
def getAltTextTemplate(request):
    success = False
    css_style = ""
    error = False
    isList = False
    REST_VERB = request.method
    data = {}
    thisPage = 1
    itemsCount = 0
    altText_params = ['id', 'page']

    for param in altText_params:
        if request.GET.get(param):
            valid = True
            break

    lookup_key = request.GET.get(param)
    data = {}
    
    # Returns single template by ID
    if param == 'id':
        data = get_template_item(id=lookup_key)
        itemsCount = 1
    # Return page from the Templates Index (list)
    elif param == 'page':
        thisPage = lookup_key
        data = get_page(page=thisPage)
        itemsCount = len(data)

    metadata = {
        "page": thisPage,
        "itemsCount": itemsCount,
        'verb': REST_VERB,
        'success': success,
        'endpoint': request.META['HTTP_HOST']+request.META['PATH_INFO']+"?"+request.META['QUERY_STRING']
    }

    return JsonResponse({'metadata': metadata, 'data': data}, safe=False)

def get_template_item(id):
    res = {}
    try:
        templateObj = AltTextTemplate.objects.get(id=id)
    except AltTextTemplate.DoesNotExist:
        templateObj = None
    if templateObj:
        templateSerialized = AltTextTemplateSerializer(templateObj, many=False)
        templateData = templateSerialized.data
        res["templateData"] = templateData
        
    else:
        res["templateData"] = None

    return res


"""
UPDATE  Alt Text Template
  curl -X "PUT" /api/alttext/template?id=<int>
  Any or all of the body params
  Payload (body) Needs to be valid JSON
  {
    "id":6,
    "path" : "/...",
    "requiredIds": [999,111,123,222,234],
    "grpHeader" : "Some TEST String of a Heaader",
    "recursive" : true,
    "template" : "Some string with tokens  like {{ token }}"
  }
"""
def updateAltTextTemplate(request):
    success = False
    error = False
    REST_VERB = request.method
    AltTextTemplateData = {}
    pprint(request.body)
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    print("----------")
    print("body")
    print("----------")
    pprint(body)
    int_id = int(body["id"])
    altText_update_params = ['path',"requiredIds","grpHeader","isRecursive","template"]
            
    try:
        AltTextTemplateObj = AltTextTemplate.objects.get(pk=int(body["id"]))
        for param_item in altText_update_params:
            if param_item in body:
                setattr(AltTextTemplateObj, param_item, body[param_item])         
        AltTextTemplateObj.save() 
        AltTextTemplateSerialized = AltTextTemplateSerializer( AltTextTemplateObj, many=False)
        AltTextTemplateData =  AltTextTemplateSerialized.data
        success = True    
    except: 
        error = "Failed to fetch Filter object"
        success = False
        count = 0
        print("ERROR::" + error)

    metadata = {
        'verb': REST_VERB,
        'success': success,
        'endpoint': request.META['HTTP_HOST']+request.META['PATH_INFO']+"?"+request.META['QUERY_STRING']
        }
    if error:
        metadata["error"] = error

    return JsonResponse({'metadata': metadata, 'data':  AltTextTemplateData}, safe=False)





"""
DELETE  Alt Text Template
  curl -X "DELETE" api/altText/template?id=<id>
"""
def deleteAltTextTemplate(request):
    REST_VERB = request.method
    error = False
    isDeleted = False
    id = False
    id = request.GET.get('id')
    data = None
    success = False
    mode = "DELETE"
    if(id):
        try:
            altTextTemplateObject = AltTextTemplate.objects.get(id=id)
            altTextTemplateObject.delete()
            success = True
            isDeleted = True
        except ObjectDoesNotExist:
            success = False       
            error = "Error: " + str(id) + " cannot be deleted becasue it does not exist in database!" 
    else:
        error = "Error: id parameter missing!"
        sucess = False 

    metadata = {
        'verb': REST_VERB,
        'mode': mode,
        'success': success,
        'uri': request.META['HTTP_HOST']+request.META['PATH_INFO']+request.META['QUERY_STRING'],
        'isDeleted': isDeleted
        }
    if error:
        metadata["error"] = error

    return JsonResponse({'metadata': metadata, 'data': data}, safe=False)






