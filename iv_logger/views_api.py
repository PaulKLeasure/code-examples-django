from . import functions

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
#from core.models import Option, Category
#from iv_logger.functions import commitLogEntryToDatabase, build_log_text
#from core.serializers import OptionSerializer
from django.core.exceptions import ObjectDoesNotExist
from pprint import pprint
import json
import os


#@permission_classes([IsAuthenticated])
#@csrf_exempt
def getAssetLogs(request, mode=None):
    context = {}
    context["success"] = False
    context["count"] = 0  
    context["logs"] = ""  

    fileName = request.GET.get('filename')
    #print('getAssetLogs: fileName')
    #pprint(fileName)
    logs = functions.getHumanReadableLogsByAssetFilename(fileName)
    context["logs"] = logs
    if len(logs) > 0:
        context["success"] = True
        context["count"] = len(logs)

    return JsonResponse(context, safe=False)


