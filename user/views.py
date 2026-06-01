from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.utils import timezone
from product.models import Product
from product.serializers import ProductListInterestsSerializer
from user.models import ContactUs, Notification, NotificationRead, User
from user.pagination import Pagination10
from user.serializers import (
    ContactUsSerializer,
    DashboardSerializer,
    IdentitySerializer,
    LoginSerializer,
    NotificationSerializer,
    OrderListUserSerializer,
    PersonalInfoSerializer,
    PhoneNumberSerializer,
    ProductCommentUserSerializer,
    RegistrationSerializer,
    ResetPasswordSerializer,
    VerifyOTPCodeSerializer,
)
from dj_rest_auth.views import LoginView as login_rest
from dj_rest_auth.views import LogoutView as logout_rest
from rest_framework import serializers


# from dj_rest_auth.registration.views
from user.models import RegistrationSession
from django.contrib.auth import authenticate
from user.service.otp import OTPService
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, OpenApiResponse, inline_serializer, extend_schema
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
    tags=["User"],
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
        register_info.first_name = serializer.validated_data["first_name"]
        register_info.last_name = serializer.validated_data["last_name"]
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

        register_info = get_object_or_404(
            RegistrationSession, phone_number=phone_number
        )

        user = User.objects.create(
            username=register_info.phone_number,
            phone_number=register_info.phone_number,
            first_name = register_info.first_name,
            last_name = register_info.last_name,
            password=register_info.password_hash,
            birthdate=register_info.birthdate,
            email=register_info.email,
            receiver_phone_number=register_info.phone_number,
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


class ResetPasswordViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Request Password Reset OTP",
        description="Sends a one-time password (OTP) to the user's phone number for password reset verification.",
        request=PhoneNumberSerializer,
        tags=["User"],
    )
    def create(self, request):
        serializer = PhoneNumberSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]

        if not User.objects.filter(phone_number=phone_number).exists():
            return Response(
                {"status": "error", "message": "User Not Register"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_service = OTPService(
            serializer.validated_data["phone_number"], "reset_password"
        )

        success, message = otp_service.generate_code()

        if success is False:
            return Response(
                {"status": "error", "message": message},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        print(message)  # Send Code

        return Response({"status": "success", "message": "OTP Send Success"})

    @extend_schema(
        summary="Verify Password Reset",
        request=ResetPasswordSerializer,
        tags=["User"],
    )
    @action(detail=False, methods=["POST"], url_path="verify")
    def verify(self, request):

        serializer = ResetPasswordSerializer(data=self.request.data)

        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        OTP_service = OTPService(phone_number, "reset_password")

        success, message = OTP_service.verify_code(
            serializer.validated_data["otp_code"]
        )

        if success is False:
            return Response(
                {"status": "error", "message": message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.get(phone_number=phone_number)
        user.set_password(serializer.validated_data["password"])
        user.save()

        return Response(
            {"status": "success", "message": "Password has been reset successfully."}
        )


class ProfileViewSet(viewsets.ViewSet):
    
    @extend_schema(
        summary="Retrieve User Identity",
        description="""
            Returns the profile information of the current user.
        """,
        responses = IdentitySerializer,
        tags=["User"],
    )
    @action(detail=False, methods=["GET"])
    def identity(self, request):
        return Response(
            IdentitySerializer(
                instance=self.request.user, context={"request": request}
            ).data
        )

    @extend_schema(
        summary="Retrieve and Update Dashboard Data",
        description="""
            Retrieves or updates the user's dashboard data.

            - GET: Fetch current dashboard info.
            - PATCH: Update dashboard info.
        """,
        request = DashboardSerializer,
        responses = DashboardSerializer,
        tags=["User"],
    )
    
    @action(detail=False, methods=["GET", "PATCH"])
    def dashboard(self, request):
        if self.request.method == "GET":
            return Response(DashboardSerializer(instance=self.request.user).data)

        serializer = DashboardSerializer(
            data=self.request.data, instance=self.request.user
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        summary="Retrieve and Update Personal Info",
        description="""
            Gets or updates the user's personal information.

            - GET: Fetch personal info.
            - PATCH: Update personal info.
        """,
        request = PersonalInfoSerializer,
        responses = PersonalInfoSerializer,
        tags=["User"],
    )
    
    @action(detail=False, methods=["GET", "PATCH"], url_path="personal-info")
    def personal_info(self, request):

        if self.request.method == "GET":
            return Response(
                PersonalInfoSerializer(
                    instance=self.request.user, context={"request": request}
                ).data
            )

        serializer = PersonalInfoSerializer(
            data=self.request.data,
            instance=self.request.user,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        summary="Get User Interests",
        description="""
            Retrieves a paginated list of the user's interests.
        """,
        responses = ProductListInterestsSerializer,
        tags=["User"],
    )
    
    @action(detail=False, methods=["GET"])
    def interests(self, request):
        return Response(
            ProductListInterestsSerializer(
                Pagination10().paginate_queryset(
                    self.request.user.interests.order_by('-created_at'), request
                ),
                many=True,
                context={"request": request},
            ).data
        )

    @extend_schema(
        summary="Get user notifications",
        description="""
            Returns a paginated list of published notifications.

            Marks unread notifications in the current page as read.
        """,

        responses = NotificationSerializer,
        tags=["User"],
    )
    
    @action(detail=False, methods=["GET"])
    def notifications(self, request):

        user_notifications = (
            Notification.objects.filter(is_published=True)
            .select_related("discount_code")
            .prefetch_related("user_statuses")
        )

        page = Pagination10().paginate_queryset(user_notifications, request)

        unread = user_notifications.exclude(
            user_statuses__user=self.request.user
        )
        unread_in_page = unread.filter(id__in = [notification.id for notification in page])

        if unread_in_page.exists():
            NotificationRead.objects.bulk_create(
                [
                    NotificationRead(
                        user=self.request.user,
                        notification=notification,
                        read_at=timezone.now(),
                    )
                    for notification in unread_in_page
                ]
            )

        return Response(NotificationSerializer(page, many=True).data)

    @extend_schema(
        summary="Retrieve User Comments",
        description="""
            Returns a paginated list of comments made by the user on products.
        """,


        responses = ProductCommentUserSerializer,
        tags=["User"],
    )
    
    @action(detail=False, methods=["GET"])
    def comments(self, request):
        return Response(
            ProductCommentUserSerializer(
                Pagination10().paginate_queryset(
                    self.request.user.created_productcomment_set.order_by('-created_at').select_related(
                        "product"
                    ),
                    request,
                ),
                many=True,
                context={"request": request},
            ).data
        )

    @extend_schema(
        summary="Retrieve User Orders",
        description="""
            Returns a paginated list of orders created by the user.
        """,



        responses = OrderListUserSerializer,
        tags=["User"],
    )
    
    @action(detail=False, methods=["GET"])
    def orders(self, request):
        return Response(
            OrderListUserSerializer(
                Pagination10().paginate_queryset(
                    self.request.user.created_order_set.order_by('-created_at'), request
                ),
                many=True,
            ).data
        )

@extend_schema(
    summary="Manage User Interests",
    description="""
        Authenticated users to add or remove products from their interests list.
    """,
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Product ID",
            required=True,
        ),
    ],
    tags=["User"],
)

class InterestsViewSet(viewsets.ViewSet):
    lookup_field = "id"

    @action(detail=True, methods=["POST"])
    def add(self, request, id):
        self.request.user.interests.add(get_object_or_404(Product, id = id))
        return Response({"status": "Success", "Message": "Product Add To Interests."})

    @action(detail=True, methods=["Delete"])
    def remove(self, request, id):
        self.request.user.interests.remove(get_object_or_404(Product, id = id))
        return Response(
            {"status": "Success", "Message": "Product Removed To Interests."}
        )

@extend_schema(
    summary="Contact Us Request",
    description="""
        Creates a new contact-us request.

        - Allows anonymous users (AllowAny) can request.
    """,
    tags=["User"],
)


class ContactUsView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated:
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
