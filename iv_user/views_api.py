from django.conf import settings
#from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from iv_user.models import IvaultUser
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from iv_user.serializers import RegistrationSerializer, IvaultUserSerializer
from django.core.exceptions import ObjectDoesNotExist
from pprint import pprint
import json

@api_view(['POST',])
def registration_view(request):
	if request.method == 'POST':
		serializer = RegistrationSerializer(data=request.data)
		data = {}
		if serializer.is_valid():
			IvaultUser = serializer.save()
			data['response'] = 'Sucessfully registered a new user.'
			data['email']    = IvaultUser.email
			data['username'] = IvaultUser.username
			token = Token.objects.get(user=IvaultUser).key
			data['token'] = token

		else:
			data = serializer.errors
		return Response(data)



@api_view(["GET","PUT","DELETE"])
@csrf_exempt
def router(request):
    print("ROUTER: (method)" + request.method)
    pprint(request.method)
    if(request.method == "GET"):
        return fetch_user(request)
    #if(request.method == "PUT"):
    #    return update_user(request)
    #if(request.method == "DELETE"):
    #    return delete_user(request)


def fetch_user(request):
    print("///// ///////   fetch_user")
    context = {}
    if(request.GET.get('id')):
        try:
            userObj = IvaultUser.objects.get(id=request.GET.get('id'))
            serializedUserObj = IvaultUserSerializer(userObj, many=False)
            context['userData'] = serializedUserObj.data
            context["message"] = ""
            context["success"] = "true"
            return JsonResponse(context, safe=False)
        except ObjectDoesNotExist:
            return False
    
    if(request.GET.get('email')):
        try:
            userObj =  IvaultUser.objects.get(email=request.GET.get('email'))
            serializedUserObj = IvaultUserSerializer(userObj, many=False)
            context['userData'] = serializedUserObj.data
            context["message"] = ""
            context["success"] = "true"
            return JsonResponse(context, safe=False)
        except ObjectDoesNotExist:
            return False

    context["message"] = "Error: unable to access this user as queried"
    context["success"] = "false"
    return JsonResponse(context, safe=False)






