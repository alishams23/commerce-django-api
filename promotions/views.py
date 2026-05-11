from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from promotions.models import Banner, Campaign, Gallery
from promotions.serializers import (
    BannerSerializer,
    CampaignSerializer,
    GallerySerializer,
)
# Create your views here.

@extend_schema(
    summary="Banners",
    tags=["Promotions"],
)

class BannerView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BannerSerializer

    def get_queryset(self):
        return Banner.objects.filter(is_active=True)

@extend_schema(
    summary="Campaigns",
    tags=["Promotions"],
)
class CampaignView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CampaignSerializer

    def get_queryset(self):
        now = timezone.now()
        return Campaign.objects.filter(
            is_active=True,
            start_time__lte=now,
            end_time__gte=now,
        ).prefetch_related("products")


@extend_schema(
    summary="Gallery",
    description="""
        Returns list of Images.
        Used for Gallery.
    """,
    tags=["Promotions"],
)
class GalleryView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = GallerySerializer
    queryset = Gallery.objects.filter(is_published=True, is_deleted=False).only(
        "id", "image", "order"
    )
