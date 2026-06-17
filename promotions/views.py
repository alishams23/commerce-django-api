from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from product.models import Product
from promotions.models import Banner, Campaign, Gallery
from promotions.serializers import (
    BannerSerializer,
    CampaignSerializer,
    GallerySerializer,
)
# Create your views here.


class BannerViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = BannerSerializer
    queryset = Banner.objects.filter(is_active=True)

    def _get_by_position(self, position):
        queryset = self.get_queryset().filter(position=position)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get wide banner (1)",
        description="Returns the active wide banner displayed in the middle section of the homepage.",
        responses=BannerSerializer(many=True),
        tags=["Promotions"],
    )
    @action(detail=False, methods=["get"])
    def wide_single(self, request):
        return self._get_by_position("wide_single")

    @extend_schema(
        summary="Get middle banners (2)",
        description="Returns the active half-width banners displayed in the middle section of the homepage.",
        responses=BannerSerializer(many=True),
        tags=["Promotions"],
    )
    @action(detail=False, methods=["get"])
    def middle_half(self, request):
        return self._get_by_position("middle_half")

    @extend_schema(
        summary="Get side banners (4)",
        description="Returns the active sidebar banners displayed in the homepage side grid.",
        responses=BannerSerializer(many=True),
        tags=["Promotions"],
    )
    @action(detail=False, methods=["get"])
    def side_grid_four(self, request):
        return self._get_by_position("side_grid_four")

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
