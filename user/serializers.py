import re
from rest_framework import serializers

from user.models import ContactUs, User

class UserCommentsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['get_full_name','profile_image']
    
class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length = 11)
    password = serializers.CharField()
    
    def validate_phone_number(self,value):
        if not re.match(r'^09[0-9]{9}$',value):
            raise serializers.ValidationError("Phone Number Started '09' and must 11 character")
        return value
    
    def validate_password(self,value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must gte 8 character")
        return value


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['id','created_by','first_name','last_name','phone_number','email','description']
    
    def validate_phone_number(self,value):
        if not re.match(r'^09[0-9]{9}$', value):
            raise serializers.ValidationError("Phone Number started '09' and must 11 character")
        return value