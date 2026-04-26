import re
from rest_framework import serializers
from order.models import DiscountCode
from product.models import Product, ProductComment, ProductImage
from user.models import ContactUs, Notification, User
from rest_framework.validators import UniqueValidator

class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length = 11)

    def validate_phone_number(self,value):
        if not re.match(r'^09[0-9]{9}$',value):
            raise serializers.ValidationError("Phone Number Started '09' and must 11 character")
        return value


class UserCommentsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['get_full_name','profile_image']
    
class LoginSerializer(PhoneNumberSerializer):
    password = serializers.CharField()
    
    def validate_password(self,value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must gte 8 character")
        return value


class RegistrationSerializer(PhoneNumberSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    birthdate = serializers.DateField(required=False, allow_null=True)
    # email = serializers.EmailField(required=False, allow_blank=True)
    email = serializers.EmailField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

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
    
class VerifyOTPCodeSerializer(PhoneNumberSerializer):
    otp_code = serializers.CharField(max_length = 6,required = True)

class ResetPasswordSerializer(VerifyOTPCodeSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
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

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['id','created_by','first_name','last_name','phone_number','email','description']
    
    def validate_phone_number(self,value):
        if not re.match(r'^09[0-9]{9}$', value):
            raise serializers.ValidationError("Phone Number started '09' and must 11 character")
        return value
    
class IdentitySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['profile_image','username']
    
class DashboardSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(read_only = True)
    email = serializers.EmailField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    date_joined = serializers.DateTimeField(read_only = True)
    
    class Meta:
        model = User
        fields = ['get_full_name','fist_name','last_name','phone_number','email','date_joined','birthdate','province',
                  'city','address','zip_code','receiver_phone_number']
    
    def validate_zip_code(self, value):
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Zip Code must 10 character")
        return value
    
    def validate_receiver_phone_number(self,value):
        if not re.match(r'^09[0-9]{9}$',value):
            raise serializers.ValidationError("Receiver Phone Number Started '09' and must 11 character")
        return value
    
class PersonalInfoSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(read_only = True)
    email = serializers.EmailField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(required = False,max_length=128,write_only = True)
    class Meta:
        model = User
        fields = ['profile_image','get_full_name','username','phone_number','email','province',
                  'city','address','zip_code','password']
        
    def validate_zip_code(self, value):
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Zip Code must 10 character")
        return value

class DiscountCodeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = ['id','code','amount','is_percentage','expired_at']

class NotificationSerializer(serializers.ModelSerializer):
    discount_code = DiscountCodeUserSerializer()    
    class Meta:
        model = Notification
        fields = ['id','title','text','subject','discount_code']

class ProductUserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id','name','slug','image']

    def get_image(self,obj):
        product_image = ProductImage.objects.filter(product_color__product = obj,is_cover = True,order = 0).first()
        if not product_image:
            return None
        return self.context.get("request").build_absolute_uri(product_image.image.url)
    
class ProductCommentUserSerializer(serializers.ModelSerializer):
    product = ProductUserSerializer()
    class Meta:
        model = ProductComment
        fields = ['product','text','created_at','is_approved']
