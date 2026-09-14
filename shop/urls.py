from django.urls import path

from shop.views import AboutUsAPIView, ShopSettingsAPIView

urlpatterns = [
    path(
        "settings/",
        ShopSettingsAPIView.as_view(),
        name="settings",
    ),
    path(
        "about-us/",
        AboutUsAPIView.as_view(),
        name="about-us",
    ),
]