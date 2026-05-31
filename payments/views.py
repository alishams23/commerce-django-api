from django.http import Http404
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.db.models import F
# Create your views here.


from azbankgateways.exceptions import AZBankGatewaysException
from azbankgateways import (
    bankfactories,
    models as bank_models,
    default_settings as settings,
)
from django.urls import reverse

from drf_spectacular.utils import extend_schema, OpenApiResponse

from order.models import Order
from payments.serializers import DetailPaySerializer

from payments.tasks import create_order, completing_order, delete_order


class PaymentViewSet(viewsets.ViewSet):
    @extend_schema(
        summary="Redirect to Payment Gateway",
        tags=["Payment"],
        request=DetailPaySerializer,
        responses={
            200: OpenApiResponse(
                description="Payment gateway URL",
                examples=[{"gateway_url": "https://bank.example.com/pay/123"}],
            ),
            400: OpenApiResponse(description="Bank error or out of stock"),
            401: OpenApiResponse(description="Unauthorized"),
            406: OpenApiResponse(description="Cart is empty"),
        },
    )
    @action(detail=False, methods=["POST"], url_path="go-to-gateways")
    def go_to_gateway_view(self, request):

        user = self.request.user

        try:
            user_cart = user.created_cart_set
            
        except:
            return Response(
                {
                    "status": "error",
                    "message": "Cart is empty",
                },
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        
        cart_discount_code = user_cart.discount_code
        if cart_discount_code is not None and not cart_discount_code.code_validation():
            cart_discount_code = None
            user_cart.save()

        cart_items = user_cart.items.all().select_related("product_color")

        if not cart_items:
            return Response(
                {
                    "status": "error",
                    "message": "Cart is empty",
                },
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        out_of_stock = cart_items.filter(product_color__stock__lt=F("count"))

        if out_of_stock.exists():
            first_bad = out_of_stock.select_related("product_color").first()
            return Response(
                {
                    "status": "error",
                    "message": f"Item {first_bad.product_color} out of stock",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DetailPaySerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        amount = user_cart.final_price

        user_mobile_number = getattr(user, "phone_number", " ")

        factory = bankfactories.BankFactory()
        try:
            bank = factory.auto_create()
            bank.set_request(request)
            bank.set_amount(amount)

            bank.set_client_callback_url(reverse("payments:callback-gateway"))
            bank.set_mobile_number(user_mobile_number)

            bank_record = bank.ready()

            create_order(
                serializer.validated_data,
                self.request.user.id,
                bank_record.tracking_code,
            )

            return Response(
                {"gateway_url": bank.get_gateway()}, status=status.HTTP_200_OK
            )

        except AZBankGatewaysException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def callback_gateway_view(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)

    try:
        order = Order.objects.select_related("created_by").get(
            transaction_code=tracking_code
        )
    except Order.DoesNotExist:
        raise Http404

    if order.status != "pending_pay":
        raise Http404

    if not tracking_code:
        raise Http404
    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)

    except bank_models.Bank.DoesNotExist:
        raise Http404

    context = {
        "tracking_code": tracking_code,
        "frontend_return_url": "https://faratabesh.co/dashboard/orders",
    }

    user_cart = order.created_by.created_cart_set

    if bank_record.is_success and (int(bank_record.amount) >= user_cart.final_price):
        completing_order(user_cart.id, tracking_code)
        return render(request, "payment/success.html", context)

    else:
        delete_order(tracking_code)
        return render(request, "payment/failed.html", context)
