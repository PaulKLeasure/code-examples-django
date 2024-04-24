from django.shortcuts import render, redirect
from iv_user.models import IvaultUser
from core.forms import OptionForm
from core.models import Asset, Option
from rest_framework import viewsets
from iv_user.admin import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import JsonResponse
from .forms import AssetForm
from django.conf import settings

import os
from dotenv import load_dotenv
load_dotenv()

#from django.contrib.auth import get_user_model
#User = get_user_model()

static_asset_filesnames = {'javascript':'core.js', 'styles':'core.css'}
context = {'static_asset_filesnames' : static_asset_filesnames}

#from iv_user.serializers import IvaultUserSerializer
# REST_FRSMEWORK / SERIALIZERS
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from core.serializers import AssetSerializer

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

def option_create_view(request):
    form = OptionForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = OptionForm()
    
    context = {
        'form': form
    }

    return render(request, "option/option_create.html", context)


# Create your views here.
def home(request):
    count = IvaultUser.objects.count()
    containerId = '0'
    if(os.environ['HOSTNAME']):
        containerId = os.environ['HOSTNAME']
    return render(request, 'home.html', {
        'count': count, 
        'DOCKER_CONTAINER_ID' : containerId
    })

def ajax_test(request):
    optionGroupName = request.GET['optionGroupName']
    print('optionGroupName', optionGroupName)
    data =  {'optionGroupName':optionGroupName}
    return JsonResponse(data)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {
        'form': form
    })

@login_required
def secret_page(request):
    return render(request, 'secret_page.html')

class secretPage(LoginRequiredMixin, TemplateView):
    template_name = 'secret_page.html'


