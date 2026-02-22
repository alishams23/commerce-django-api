from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import ExpressionWrapper, F, DecimalField
from order.models import Cart, CartItem, Delivery, DiscountCode
from order.serializers import (
    ApplyDiscountSerializer,
    CartSerializer,
    DeliverySerializer,
)

from product.models import ProductColor
from order.serializers import AddToCartSerializer

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
# Create your views here.


@extend_schema(
    summary="List delivery methods",
    description="""
        Returns all active delivery methods.

        Used in checkout to let the user choose a delivery option.
    """,
    tags=["Order"],
)
class DeliveryView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = DeliverySerializer
    queryset = Delivery.objects.filter(is_active=True)


class CartViewSet(viewsets.ViewSet):
    def get_object(self):
        return Cart.objects.get_or_create(created_by=self.request.user)[0]

    @extend_schema(
        summary="Get user cart",
        description="""
            Returns the current user's cart.

            If the cart does not exist, it will be created automatically.
            Used to display cart details and start checkout flow.
        """,
        responses={200: CartSerializer},
        tags=["Order"],
    )
    @action(detail=False, methods=["GET"])
    def view(self, request):
        context = {"result": "Success"}
        cart = self.get_object()

        for item in cart.items.select_related("product_color"):
            current_stock = item.product_color.stock

            if current_stock == 0:
                context.setdefault("warnings", []).append(
                    {"reason": "OUT_OF_STOCK", "item_id": item.id}
                )  # .{item.product_color.product.name}
                item.delete_hard()

            elif item.count > current_stock:
                item.count = current_stock
                item.save()
                context.setdefault("warnings", []).append(
                    {"reason": "QUANTITY_ADJUSTED", "item_id": item.id}
                )  # .{item.product_color.product.name}

        if cart.discount_code is not None and not cart.discount_code.code_validation():
            cart.discount_code = None
            cart.save()
            context.setdefault("warnings", []).append(
                {"reason": "DISCOUNTED_CODE_EXPIRED"}
            )

        cart.items.update(discounted=0)

        if (
            cart.discount_code is not None
            and cart.discount_code.included_type == "product"
        ):
            discounted_item = cart.items.filter(
                product_color__product_id__in=cart.discount_code.products.values_list(
                    "id", flat=True
                )
            ).annotate(
                total_price_items=ExpressionWrapper(
                    F("count") * F("product_color__base_price"),
                    output_field=DecimalField(),
                )
            )

            if discounted_item:
                discounted_item.order_by(
                    "-total_price_items"
                ).first().discount_calculate()
            else:
                context["Error"] = "Discount Code Is Not Included This Cart!"
                cart.discount_code = None
                cart.save()

        context["cart_detail"] = CartSerializer(instance=cart).data

        return Response(
            context,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Add item to cart",
        description="""
            Adds a product color to the user's cart or increases its quantity by one.

            Used when the user clicks the "Add to cart" button.
        """,
        request=AddToCartSerializer,
        tags=["Order"],
    )
    @action(detail=False, methods=["POST"], url_path="items/add")
    def add(self, request):
        data = self.request.data

        AddToCartSerializer(data=data).is_valid(
            raise_exception=True
        )  # For Validation ProductColor ID

        product_color = get_object_or_404(ProductColor, id=data["id"])

        if product_color.stock == 0:
            return Response(
                {"Error": "Stock This Color From Product is 0"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item, created = CartItem.objects.get_or_create(
            created_by=self.request.user,
            cart=self.get_object(),
            product_color=product_color,
        )

        if not created and item.count >= product_color.stock:
            return Response(
                {"Error": "Stock This Color From Product is 0"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not created:  # default Count = 1
            item.count += 1

        item.save()
        return Response(
            {
                "result": "Item increase from cart",
                "item_id": item.id,
                "remaining_stock": product_color.stock - item.count,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Remove item from cart",
        description="""
            Decreases the quantity of a cart item by one.

            If the quantity reaches zero, the item will be removed from the cart.
            Used when the user clicks the decrease or remove button.
        """,
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="CartItem ID",
                required=True,
            ),
        ],
        tags=["Order"],
    )
    @action(detail=True, methods=["PATCH"], url_path="items/remove")
    def remove(self, request, pk=None):

        item = get_object_or_404(
            CartItem,
            id=pk,
            created_by=self.request.user,
            cart=self.get_object(),
        )

        item.count -= 1
        item.save()

        if item.count == 0:
            item.delete_hard()
            return Response(
                {"result": "Item Deleted from cart"}, status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            {"result": "Item decrease from cart"}, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Delete item from cart",
        description="""
            Deletes a cart item completely from the user's cart.

            Use this endpoint when the user wants to remove the item entirely.
            If you only want to decrease the quantity, use the remove endpoint instead.
        """,
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="CartItem ID",
                required=True,
            ),
        ],
        tags=["Order"],
    )
    @action(detail=True, methods=["DELETE"], url_path="items/delete")
    def delete(self, request, pk=None):
        get_object_or_404(
            CartItem, id=pk, created_by=self.request.user, cart=self.get_object()
        ).delete_hard()
        return Response(
            {"result": "Item Deleted from cart"}, status=status.HTTP_204_NO_CONTENT
        )

    @extend_schema(
        summary="Apply discount code to cart",
        description="""
            Applies a discount code to the current user's cart.

            Validates the discount code and checks if it applies to any items in the cart.
            Returns an error if the code is invalid or not applicable.
        """,
        request=ApplyDiscountSerializer,
        tags=["Order"],
    )
    @action(detail=False, methods=["PATCH"], url_path="discount/apply")
    def apply(self, request):
        serializer = ApplyDiscountSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.get_object()

        discount_code = get_object_or_404(
            DiscountCode, code=serializer.validated_data["code"]
        )

        if discount_code.code_validation():
            if discount_code.included_type == "product":
                qs = obj.items.filter(
                    product_color__product_id__in=discount_code.products.values_list(
                        "id", flat=True
                    )
                )

                if not qs.exists():
                    return Response(
                        {"Error": "Discount Code Is Not Included This Cart!"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            obj.discount_code = discount_code
            obj.save()

            # discount_code.increment_usage() # while buy finish

            return Response({"result": "Discount Applied."})

        return Response(
            {"Error": "Discount Code is Invalid!"}, status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Remove discount code from cart",
        description="""
            Removes the currently applied discount code from the user's cart.
            If no discount code is applied, this endpoint does nothing.
        """,
        tags=["Order"],
    )
    @action(detail=False, methods=["PATCH"], url_path="discount/unapply")
    def unapply(self, request):
        cart = self.get_object()
        if cart.discount_code is not None:
            cart.discount_code = None
            cart.save()
        return Response({"result": "Discount Code UnApply Successfully"})
