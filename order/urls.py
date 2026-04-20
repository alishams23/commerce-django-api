from django.urls import path

from order.views import DeliveryView
from rest_framework.routers import DefaultRouter

from .views import CartViewSet, DetailPayView

urlpatterns = [
    path("list-delivery/", DeliveryView.as_view(), name="delivery"),
    path("detail-pay/", DetailPayView.as_view(), name="detail-pay"),
]
router = DefaultRouter()
router.register(r"cart", CartViewSet, basename="cart")

urlpatterns += router.urls
