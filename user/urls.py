from django.urls import path

from user.views import ContactUsView, LoginView, LogoutView


urlpatterns = [
    path("login/",LoginView.as_view(),name = 'login'),
    path("logout/",LogoutView.as_view(),name = 'logout'),
    path("contact-us/",ContactUsView.as_view(),name = 'contact-us'),
]