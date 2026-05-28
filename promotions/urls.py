from django.urls import path

from promotions.views import BannerViewSet, CampaignView, GalleryView

from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('campaign/',CampaignView.as_view(),name = "campaign"),
    path('gallery/',GalleryView.as_view(),name = "gallery"),
]

router = DefaultRouter()
router.register("banners", BannerViewSet, basename="banners")
urlpatterns += router.urls