from drf_spectacular.utils import extend_schema
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny

from shop.models import AboutUs, ShopSettings
from shop.serializers import AboutUsSerializer, ShopSettingsSerializer


@extend_schema(
    summary="Get Shop Information",
    description="""
        Returns the shop information.
    """,
    tags=["Shop Settings"],
)
class ShopSettingsAPIView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ShopSettingsSerializer

    def get_object(self):
        return ShopSettings.objects.first()


@extend_schema(
    summary="Get About Us",
    description="""
        Returns the shop's about us information.
    """,
    tags=["Shop Settings"],
)
class AboutUsAPIView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = AboutUsSerializer

    def get_object(self):
        return AboutUs.objects.first()
