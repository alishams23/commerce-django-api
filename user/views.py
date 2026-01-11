from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import AnonymousUser
from user.models import ContactUs, User
from user.serializers import ContactUsSerializer, LoginSerializer
from dj_rest_auth.views import LoginView as login_rest
from dj_rest_auth.views import LogoutView as logout_rest
from django.contrib.auth import authenticate
# Create your views here.

class LoginView(login_rest):
    serializer_class = LoginSerializer
    
    def login(self,serializer):
        self.serializer = serializer
        return super().login()
    
    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)

        user = User.objects.get(phone_number = serializer.validated_data['phone_number'])

        if not authenticate(request,username = user.username,password = serializer.validated_data['password']):
            return Response({"Error":"User Not Found!"}, status = status.HTTP_404_NOT_FOUND)

        serializer.validated_data['user'] = user
        self.login(serializer)
        return self.get_response()


class LogoutView(logout_rest):
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ContactUsView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.all()
    def perform_create(self, serializer):
        user = self.request.user
        if not isinstance(user,AnonymousUser):
            serializer.validated_data['phone_number'] = user.phone_number
            
            if user.first_name and user.last_name:
                serializer.validated_data['first_name'] = user.first_name
                serializer.validated_data['last_name'] = user.last_name
            else:
                user.first_name = serializer.validated_data['first_name']
                user.last_name = serializer.validated_data['last_name']
            
            if  (user.email == '' or user.email is None) and serializer.validated_data['email']:
                user.email = serializer.validated_data['email']
                
            else:
                serializer.validated_data['email'] = user.email
                
            user.save()
            serializer.save(created_by = user)
            
        return super().perform_create(serializer)