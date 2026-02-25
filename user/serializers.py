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


class RegistrationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    password = serializers.CharField(write_only=True, min_length=8)
    birthdate = serializers.DateField(required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate_phone_number(self, value):
        if not re.match(r'^09[0-9]{9}$', value):
            raise serializers.ValidationError("Phone Number must start with '09' and be 11 digits")
        return value
    

    def validate_password(self, value):
        
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("Password must contain at least one letter.")

        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit.")

        # if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', value):
        #     raise serializers.ValidationError("Password must contain at least one special character.")

        phone = self.initial_data.get("phone_number")
        if phone and phone in value:
            raise serializers.ValidationError("Password cannot contain your phone number.")

        return value
    
class VerifyOTPCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length = 11)
    otp_code = serializers.CharField(max_length = 6,required = True)
    
    def validate_phone_number(self,value):
        if not re.match(r'^09[0-9]{9}$',value):
            raise serializers.ValidationError("Phone Number Started '09' and must 11 character")
        return value

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['id','created_by','first_name','last_name','phone_number','email','description']
    
    def validate_phone_number(self,value):
        if not re.match(r'^09[0-9]{9}$', value):
            raise serializers.ValidationError("Phone Number started '09' and must 11 character")
        return value