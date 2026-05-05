from django.urls import path
from .views import PaymentViewSet, callback_gateway_view
from rest_framework.routers import DefaultRouter

app_name = 'payments'

urlpatterns = [
    path('callback-gateway/', callback_gateway_view, name='callback-gateway'),
]

router = DefaultRouter()

router.register("",PaymentViewSet,basename = 'payment')

urlpatterns += router.urls