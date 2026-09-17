from azbankgateways import (
    bankfactories,
)
from azbankgateways import (
    default_settings as settings,
)
from azbankgateways import (
    models as bank_models,
)
from azbankgateways.exceptions import AZBankGatewaysException
from azbankgateways.models.enum import PaymentStatus
from django.db import transaction
from django.db.models import F, Q
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from order.models import Order
from payments.serializers import DetailPaySerializer
from payments.tasks import create_order
from shop.models import ShopSettings


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
        shop_setting = ShopSettings.objects.order_by("created_at").first()

        if shop_setting.is_sale_active is False:
            return Response(
                {
                    "status": "error",
                    "message": shop_setting.maintenance_message,
                },
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        user = self.request.user

        # -------------------------
        # Get user's cart
        # -------------------------
        try:
            user_cart = user.created_cart_set
        except user.created_cart_set.RelatedObjectDoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Cart is empty",
                },
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
            
    

        # -------------------------
        # Lock cart and validate it
        # -------------------------
        with transaction.atomic():
            user_cart = (
                user_cart.__class__.objects.select_for_update()
                .prefetch_related("items__product_color")
                .get(pk=user_cart.pk)
            )

            # Cart is already being paid
            if user_cart.status == "pay_doing":
                return Response(
                    {
                        "status": "error",
                        "message": "Cart is currently in payment process.Please try again in 10 minutes.",
                    },
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )

            # -------------------------
            # Validate discount code
            # -------------------------
            cart_discount_code = user_cart.discount_code

            if (
                cart_discount_code is not None
                and not cart_discount_code.code_validation()
            ):
                user_cart.discount_code = None
                user_cart.save(update_fields=["discount_code"])

            # -------------------------
            # Get cart items
            # -------------------------
            cart_items = user_cart.items.select_related("product_color")

            if not cart_items.exists():
                return Response(
                    {
                        "status": "error",
                        "message": "Cart is empty",
                    },
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )

            # -------------------------
            # Check unpublished products
            # -------------------------
            unavailable_items = cart_items.filter(
                Q(product_color__product__is_published=False)
                | Q(product_color__product__is_deleted=True)
            )

            if unavailable_items.exists():
                first_bad = unavailable_items.first()

                return Response(
                    {
                        "status": "error",
                        "message": f"Item {first_bad.product_color} is no longer available",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )


            # -------------------------
            # Check stock
            # -------------------------
            out_of_stock = cart_items.filter(product_color__stock__lt=F("count"))

            if out_of_stock.exists():
                first_bad = out_of_stock.first()

                return Response(
                    {
                        "status": "error",
                        "message": f"Item {first_bad.product_color} out of stock",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # -------------------------
            # Validate payment data
            # -------------------------
            serializer = DetailPaySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user_mobile_number = getattr(
                user,
                "phone_number",
                " ",
            )

            # -------------------------
            # Mark cart as payment in progress
            # -------------------------
            user_cart.status = "pay_doing"
            user_cart.save(update_fields=["status"])

        # -------------------------------------------------
        # IMPORTANT:
        # Transaction is committed here.
        # Do NOT keep DB transaction open during bank call.
        # -------------------------------------------------

        factory = bankfactories.BankFactory()

        try:
            bank = factory.auto_create()

            order = create_order(
                serializer.validated_data,
                user.id,
            )
            bank.set_request(request)
            bank.set_amount(order.final_price)

            bank.set_client_callback_url(reverse("payments:callback-gateway"))

            bank.set_mobile_number(user_mobile_number)

            bank_record = bank.ready()

            order.transaction_code=bank_record.tracking_code
            order.save()
            return Response(
                {
                    "gateway_url": bank.get_gateway(),
                },
                status=status.HTTP_200_OK,
            )

        except AZBankGatewaysException as e:
            # Bank request failed.
            # Unlock cart so the user can try again.
            user_cart.__class__.objects.filter(
                pk=user_cart.pk,
                status="pay_doing",
            ).update(status="pending_pay")

            return Response(
                {
                    "error": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


def callback_gateway_view(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)

    if not tracking_code:
        raise Http404

    try:
        order = Order.objects.select_related("created_by").get(
            transaction_code=tracking_code
        )
    except Order.DoesNotExist:
        raise Http404

    if order.status != "pending_pay":
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
        order.status = "paid"
        order.save()
        user_cart.status = "pending_pay"
        user_cart.save(update_fields=["status"])
        return render(request, "payment/success.html", context)

    elif bank_record.status == PaymentStatus.CANCEL_BY_USER:
        order.status = "cancelled"
        order.cancel_reason = "customer_request"
        order.save()
        user_cart.status = "pending_pay"
        user_cart.save(update_fields=["status"])
        return render(request, "payment/failed.html", context)

    else:
        order.status = "cancelled"
        order.cancel_reason = "payment_error"
        order.save()
        user_cart.status = "pending_pay"
        user_cart.save(update_fields=["status"])
        return render(request, "payment/failed.html", context)
