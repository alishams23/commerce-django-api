from django.urls import path

from order.views import DeliveryView
from rest_framework.routers import DefaultRouter

from .views import CartViewSet, ProvinceListAPIView

urlpatterns = [
    path("list-delivery/", DeliveryView.as_view(), name="delivery"),
    path("provinces/", ProvinceListAPIView.as_view(),name = "provinces"),

]
router = DefaultRouter()
router.register(r"cart", CartViewSet, basename="cart")

urlpatterns += router.urls
