from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status,viewsets
from rest_framework.decorators import action, api_view
# Create your views here.



from azbankgateways.exceptions import AZBankGatewaysException
from azbankgateways import (
    bankfactories,
    models as bank_models,
    default_settings as settings,
    )
from django.urls import reverse

from order.models import Order


class PaymentViewSet(viewsets.ViewSet):
    
    @action(detail = False,methods = ["POST"],url_path = "go-to-gateways")
    def go_to_gateway_view(self,request):
        user_cart = self.request.user.created_cart_set
        
        for item in user_cart.items.all().select_related("product_color"):
            if item.count > item.product_color.stock:
                return Response({"status":"error", "message":f"Item {item.product_color} Not Mojoud"}, status=status.HTTP_400_BAD_REQUEST)        

        amount = self.request.user.created_cart_set.total_price
    
        user_mobile_number = getattr(self.request.user, "phone_number", " ")

        factory = bankfactories.BankFactory()
        try:
            bank = (
                factory.auto_create()
            )
            bank.set_request(request)
            bank.set_amount(amount)

            bank.set_client_callback_url(reverse("payments:payment-callback-gateway-view"))
            bank.set_mobile_number(user_mobile_number)  # اختیاری
            
            bank_record = bank.ready()
            
            return Response({"gateway_url": bank.get_gateway()}, status=status.HTTP_200_OK)
        
        except AZBankGatewaysException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail = False,methods = ["GET"],url_path = "callback-gateway")
    def callback_gateway_view(self,request):
        tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
        
        if not tracking_code:
            return Response({"status":"error", "message":"tracking code is invalid."}, status=status.HTTP_404_NOT_FOUND)
        try:
            bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)

        except bank_models.Bank.DoesNotExist:
            return Response({"status":"error", "message": "tracking code is incorrect."}, status=status.HTTP_404_NOT_FOUND)

        if bank_record.is_success:
            
            #Celery Task For Create Order
            
            return Response("Ok")
            
        else:
            return Response("no ")
