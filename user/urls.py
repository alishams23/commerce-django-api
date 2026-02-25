from django.urls import path

from user.views import ContactUsView, LoginView, LogoutView,RegisterViewSet

from django.urls import re_path

from dj_rest_auth.jwt_auth import get_refresh_view

from rest_framework.routers import DefaultRouter

urlpatterns = [
    path("login/",LoginView.as_view(),name = 'login'),
    path("logout/",LogoutView.as_view(),name = 'logout'),
    re_path(r'token/refresh/?$', get_refresh_view().as_view(), name='token_refresh'),
    path("contact-us/",ContactUsView.as_view(),name = 'contact-us'),
]

router = DefaultRouter()

router.register("register",RegisterViewSet,basename = 'register')

urlpatterns += router.urls