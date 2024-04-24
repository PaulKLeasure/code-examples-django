# NOTE: This code has a whole lot already encapsulated
#       by dJango. See: https://www.django-rest-framework.org/ (tutorials)
#from django.contrib.auth.models import User, Group 

from core.models import Asset, Option, Category
from core.serializers import AssetSerializer, OptionSerializer, CategorySerializer
# REST Framework Mixin and Generics (saves a ton of code)
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions

'''
    NOTE:  Using generic class-based views
           https://www.django-rest-framework.org/tutorial/3-class-based-views/#using-generic-class-based-views

'''
class AssetList(generics.ListCreateAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    #permission_classes = [permissions.IsAuthenticated]


class AssetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    #permission_classes = [permissions.IsAuthenticated]

class OptionList(generics.ListCreateAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    #permission_classes = [permissions.IsAuthenticated]


class OptionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    #permission_classes = [permissions.IsAuthenticated]

class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    #permission_classes = [permissions.IsAuthenticated]


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    #permission_classes = [permissions.IsAuthenticated]




