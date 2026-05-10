from django.urls import path

from promotions.views import BannerView, CampaignView, GalleryView
urlpatterns = [
    path('banner/',BannerView.as_view(),name = "banner"),
    path('campaign/',CampaignView.as_view(),name = "campaign"),
    path('gallery/',GalleryView.as_view(),name = "gallery"),
]