from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from searchTemplates.models import SearchTemplate
from searchTemplates.serializers import SearchTemplateSerializer
from pprint import pprint
import json
#from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

'''
REMINDER: API AUTHORIZATION TOKEN
          NEEDS TO BE iN THE HEADER
'''

'''
 Endpoint:   /api/search/template
             /api/search/template?tid=<template id>

 Results:    /api/search/template  resturns list of all
             search template objects from dB limited by `limit`
             
             /api/search/template?tid=<template id>  returns
             single search template object
'''
@api_view(['GET','POST','DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def GetSearchTemplates(request, format=None):
    if request.method =='GET':
        print('REQUEST OPBJECT')
        pprint(request)
        context = {}
        
        quanPerPage = 30

        if(request.GET.get('limit')):
            quanPerPage = request.GET.get('limit')

        tid = False;

        if(request.GET.get('tid')):
        	tid = request.GET.get('tid')
        	templates = SearchTemplate.objects.filter(id__exact=tid)
        	print('SINGLE TEMPLATE')
        	pprint(templates)

        else:
            templates = SearchTemplate.objects.all()
            print('TEMPLATE')
            pprint(templates)

        template_serializer = SearchTemplateSerializer(templates, many=True)
        print("template_serializer.data")
        pprint(template_serializer.data)
        context['templateData'] = template_serializer.data
        context['objectsCount'] = templates.count()
        context['endpoint'] = request.get_full_path()
        context['limit'] = quanPerPage
        return JsonResponse(context, safe=False)


    elif request.method =='POST':
        '''
           RESTfully CREATE search template
           The body include a data key which holds
           a valis JSON template used in VUE JS Front end
           
           eg.  
             Method:    POST
             Endpoint:  /api/search/template
             Body:      {
                         "name": "Template Name Here",
                         "descr": "Some descriptions here (options)",
                         "data": {"def": {"and": [], "andOr": [], "exclude": [], "excludeOr": []}, "group": {"and": [], "andOr": [], "exclude": [], "excludeOr": []}}
                        }    
        '''
        new_template_data = JSONParser().parse(request)
        template_serializer = SearchTemplateSerializer(data=new_template_data)
        if template_serializer.is_valid():
            template_serializer.save()
            return JsonResponse(template_serializer.data, status=status.HTTP_201_CREATED) 

        return JsonResponse(template_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    elif request.method =='DELETE':
        '''
           RESTfully Delete search template
           eg.  
             Method:    DELETE
             Endpoint:  /api/search/template
             Body:      {"tid": [<int>] } ~or~ {"tid": [5,6,7] }     
        '''
        print('======== DELETE ===========')
        pprint(request.data)    	
        if(request.data):
            dataDict = request.data
            outStr = " "
            err = ''
            print('======== REQUEST.DATA ===========')
            print(dataDict['tid'])
            tids = dataDict['tid']
            for tid in tids:
                try:
                    print(tid)
                    ST = SearchTemplate.objects.get(id__exact=tid)
                    ST.delete()
                    outStr += 'ID:' + str(tid) + " deleted successfully!, "
                except:
                	outStr += str(tid) + " does not exist, "
            outStr = outStr.rstrip()[:-1]+"."
            return JsonResponse({'message': outStr }, status=status.HTTP_204_NO_CONTENT)
        
        





