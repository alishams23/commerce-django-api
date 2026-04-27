from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.db import transaction
# Create your views here.


from azbankgateways.exceptions import AZBankGatewaysException
from azbankgateways import (
    bankfactories,
    models as bank_models,
    default_settings as settings,
)
from django.urls import reverse

from drf_spectacular.utils import extend_schema, OpenApiResponse

from order.models import Order, OrderItem
from payments.serializers import DetailPaySerializer


class PaymentViewSet(viewsets.ViewSet):
    

    @extend_schema(
        summary="Redirect to Payment Gateway",
        tags=["Payment"],
        request=DetailPaySerializer,
        responses={
            200: OpenApiResponse(description="Payment gateway URL", 
                examples=[{"gateway_url": "https://bank.example.com/pay/123"}]),
            400: OpenApiResponse(description="Bank error or out of stock"),
            401: OpenApiResponse(description="Unauthorized"),
            406: OpenApiResponse(description="Cart is empty"),
        }
    )
    
    @action(detail=False, methods=["POST"], url_path="go-to-gateways")
    def go_to_gateway_view(self, request):
        user_cart = self.request.user.created_cart_set
        if not user_cart.items.all():
              return Response(
                    {
                        "status": "error",
                        "message": "Cart is empty",
                    },
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )
              
        serializer = DetailPaySerializer(data = self.request.data)
        serializer.is_valid(raise_exception = True)
        order = Order.objects.create(
            created_by=self.request.user,
            phone_number = self.request.user.phone_number,
            first_name = serializer.validated_data['first_name'] ,
            last_name = serializer.validated_data['last_name'] ,
            email = serializer.validated_data['email'] ,
            is_different_address = serializer.validated_data['is_different_address'] ,
            province = serializer.validated_data['province'] ,
            city = serializer.validated_data['city'] ,
            address = serializer.validated_data['address'] ,
            zip_code = serializer.validated_data['zip_code'],
            description = serializer.validated_data.get('description'))

        for item in user_cart.items.all().select_related("product_color"):
            if item.count > item.product_color.stock:
                return Response(
                    {
                        "status": "error",
                        "message": f"Item {item.product_color} out of stock",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        amount = self.request.user.created_cart_set.total_price

        user_mobile_number = getattr(self.request.user, "phone_number", " ")
        
        factory = bankfactories.BankFactory()
        try:
            bank = factory.auto_create()
            bank.set_request(request)
            bank.set_amount(amount)

            bank.set_client_callback_url(
                reverse("payments:payment-callback-gateway-view")
            )
            bank.set_mobile_number(user_mobile_number)  # اختیاری

            bank_record = bank.ready()
            
            order.transaction_code = bank_record.tracking_code
            order.save()

            return Response(
                {"gateway_url": bank.get_gateway()}, status=status.HTTP_200_OK
            )

        except AZBankGatewaysException as e:
            order.delete_hard()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Callback Gateway",
        tags=["Payment"],
        )

    @action(detail=False, methods=["GET"], url_path="callback-gateway")
    def callback_gateway_view(self, request):
        tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)

        if not tracking_code:
            return Response(
                {"status": "error", "message": "tracking code is invalid."},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)

        except bank_models.Bank.DoesNotExist:
            return Response(
                {"status": "error", "message": "tracking code is incorrect."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_cart = self.request.user.created_cart_set
        if bank_record.is_success:
            with transaction.atomic():
                order = Order.objects.get(transaction_code = tracking_code)
                
                order.total_price = user_cart.total_price
                order.discount_price = (user_cart.total_price - user_cart.discounted_price)
                order.delivery_price = user_cart.delivery_type.cost if user_cart.delivery_type else 0
                
                order.final_price = (order.total_price - order.discount_price + order.delivery_price)

                for cart_item in self.request.user.created_cart_set.items.all().select_related("product_color"):
                    product_color = cart_item.product_color
                    order_item = OrderItem.objects.create(
                        order=order,
                        product_name=product_color.product.name,
                        color_code=product_color.color.code,
                        product_price=product_color.price,
                        product_count=cart_item.count,
                    )
                    product_color.stock -= cart_item.count
                    product_color.save()
                    order_item.total_price = order_item.calculate_total_price()
                    order_item.save()
                    cart_item.delete_hard()

                order.save()
            # Celery Task For Create Order

            return Response("Ok")

        else:
            return Response("no ")
