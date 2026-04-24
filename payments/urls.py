from django.urls import path
from .views import PaymentViewSet
from rest_framework.routers import DefaultRouter

app_name = 'payments'

urlpatterns = [
    # path('go-to-gateways/', go_to_gateway_view, name='gateway-view'),
    # path('callback-gateway/', callback_gateway_view, name='callback-gateway'),
    # path('verify-gateway/', verify_payment_view, name='verify-gateway'),
]

router = DefaultRouter()

router.register("",PaymentViewSet,basename = 'payment')

urlpatterns += router.urls