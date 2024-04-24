from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import IvaultUser, IvaultUserManager
from pprint import pprint

class RegistrationSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)

    class Meta:
        model = IvaultUser
        fields = ['email', 'username', 'password', 'password2']
        extra_kwargs = { 
            'password': {'write_only': True}
        }
    
    # Override the validation and save
    def save(self):
        ivUserObj = IvaultUser(
            email    = self.validated_data['email'], 
            username = self.validated_data['username']
            )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
    	    raise serializers.ValidationError({'password': 'Passwords must match'})

        ivUserObj.set_password(password)
        ivUserObj.save()
        return ivUserObj

class IvaultUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = IvaultUser
        fields = ['id', 'username', 'email', 'is_admin' ]


