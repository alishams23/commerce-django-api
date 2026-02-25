from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from user.models import ContactUs,User
from user.serializers import (
    ContactUsSerializer,
    LoginSerializer,
    RegistrationSerializer,
    VerifyOTPCodeSerializer,
)
from dj_rest_auth.views import LoginView as login_rest
from dj_rest_auth.views import LogoutView as logout_rest
from rest_framework import serializers


# from dj_rest_auth.registration.views
from user.models import RegistrationSession
from django.contrib.auth import authenticate
from user.service.otp import OTPService
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
# Create your views here.

@extend_schema(
    summary="User login",
    description="""
    Authenticates user using phone number and password.

    Requirements:
    - Phone number must be verified
    - Credentials must be valid

    Returns JWT access and refresh tokens on success.
    """,
    responses={
        200: OpenApiResponse(
            description="User created successfully",
            response={
                "type": "object",
                "properties": {
                    "access": {"type": "string"},
                    "refresh": {"type": "string"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "pk": {"type": "integer"},
                            "username": {"type": "string"},
                            "email": {"type": "string"},
                            "first_name": {"type": "string"},
                            "last_name": {"type": "string"},
                        },
                    },
                },
            },
        ),
    },
    tags = ["User"]
    )

class LoginView(login_rest):
    serializer_class = LoginSerializer

    def login(self, serializer):
        self.serializer = serializer
        return super().login()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(
            User,
            phone_number=serializer.validated_data["phone_number"],
            verify_phone_number=True,
        )

        if not authenticate(
            request,
            username=user.username,
            password=serializer.validated_data["password"],
        ):
            return Response(
                {"Error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer.validated_data["user"] = user
        self.login(serializer)
        return self.get_response()



class LogoutView(logout_rest):
    @extend_schema(
        summary="User logout",
        description="""
        Logs out the authenticated user.

        If using JWT with blacklist:
        - Requires refresh token
        - Refresh token will be blacklisted

        User must be authenticated.
        """,
        request=inline_serializer(
            name="LogoutRequest",
            fields={
                "refresh": serializers.CharField(
                    help_text="Refresh token to be blacklisted"
                )
            },
        ),
        tags=["User"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RegisterViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    @extend_schema(
        summary="User registration - Send OTP",
        description="""
        Starts the user registration process.

        - Validates phone number and password
        - Stores temporary registration session
        - Sends OTP code to user's phone number

        If the phone number is already registered, an error will be returned.
        """,
        request=RegistrationSerializer,
        responses={
            200: OpenApiResponse(
                description="OTP sent successfully",
                response={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "success"},
                        "message": {"type": "string", "example": "OTP Send Success"},
                    },
                },
            ),
            400: OpenApiResponse(
                description="Phone number already registered",
            ),
            429: OpenApiResponse(
                description="Too many OTP requests",
            ),
        },
        tags=["User"],
    )
    def create(self, request):
        serializer = RegistrationSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        if User.objects.filter(phone_number=phone_number).exists():
            return Response(
                {
                    "status": "error",
                    "message": "This phone number is already registered",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        register_info, _ = RegistrationSession.objects.get_or_create(
            phone_number=phone_number
        )
        register_info.password_hash = make_password(
            serializer.validated_data["password"]
        )
        register_info.email = serializer.validated_data.get("email", "")
        register_info.birthdate = serializer.validated_data.get("birthdate", None)

        register_info.save()

        OTP_service = OTPService(phone_number, "register")

        success, message = OTP_service.generate_code()

        if success is False:
            return Response(
                {"status": "error", "message": message},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        print(message)  # Send Code

        return Response({"status": "success", "message": "OTP Send Success"})
    @extend_schema(
        summary="Verify OTP and create user",
        description="""
        Verifies the OTP code sent to the user's phone.

        If OTP is valid:
        - Creates the user
        - Marks phone number as verified
        - Returns JWT access and refresh tokens
        """,
        request=VerifyOTPCodeSerializer,
        responses={
            200: OpenApiResponse(
                description="User created successfully",
                response={
                    "type": "object",
                    "properties": {
                        "access": {"type": "string"},
                        "refresh": {"type": "string"},
                        "user": {
                            "type": "object",
                            "properties": {
                                "pk": {"type": "integer"},
                                "username": {"type": "string"},
                                "email": {"type": "string"},
                                "first_name": {"type": "string"},
                                "last_name": {"type": "string"},
                            },
                        },
                    },
                },
            ),
            400: OpenApiResponse(
                description="Invalid or expired OTP",
            ),
        },
        tags=["User"],
    )
    @action(detail=False, methods=["POST"], url_path="verify")
    def verify(self, request):

        serializer = VerifyOTPCodeSerializer(data=self.request.data)

        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        OTP_service = OTPService(phone_number, "register")

        success, message = OTP_service.verify_code(
            serializer.validated_data["otp_code"]
        )

        if success is False:
            return Response(
                {"status": "error", "message": message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        register_info = get_object_or_404(RegistrationSession,phone_number=phone_number)
        
        user = User.objects.create(
            username=register_info.phone_number,
            phone_number=register_info.phone_number,
            password=register_info.password_hash,
            birthdate=register_info.birthdate,
            email=register_info.email,
            verify_phone_number=True,
        )
        register_info.delete_hard()
        refresh_token = RefreshToken.for_user(user)
        context = {
            "access": str(refresh_token.access_token),
            "refresh": str(refresh_token),
            "user": {
                "pk": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        }
        return Response(context, status=status.HTTP_200_OK)


class ContactUsView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if not isinstance(user, AnonymousUser):
            serializer.validated_data["phone_number"] = user.phone_number

            if user.first_name and user.last_name:
                serializer.validated_data["first_name"] = user.first_name
                serializer.validated_data["last_name"] = user.last_name
            else:
                user.first_name = serializer.validated_data["first_name"]
                user.last_name = serializer.validated_data["last_name"]

            if (user.email == "" or user.email is None) and serializer.validated_data[
                "email"
            ]:
                user.email = serializer.validated_data["email"]

            else:
                serializer.validated_data["email"] = user.email

            user.save()
            serializer.save(created_by=user)

        return super().perform_create(serializer)
