from django.urls import path

from order.views import CartAddItem, CartRemoveItem, CartView, DeliveryView


urlpatterns = [
    path("list-delivery/",DeliveryView.as_view(),name = "delivery"),
    path("cart/",CartView.as_view(),name = "cart"),
    path("cart/add/<int:pk>/",CartAddItem.as_view(),name = "cart-add"),
    path("cart/remove/<int:pk>/",CartRemoveItem.as_view(),name = "cart-remove"),
    
]