from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import ExpressionWrapper, F, DecimalField
from order.models import Cart, CartItem, Delivery, DiscountCode
from order.serializers import (
    ApplyDiscountSerializer,
    CartSerializer,
    DeliverySerializer,
)

from product.models import ProductColor
from order.serializers import AddToCartSerializer, RemoveFromCartSerializer

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


@extend_schema(
    summary="Get user cart",
    description="""
        Returns the current user's cart.

        If the cart does not exist, it will be created automatically.
        Used to display cart details and start checkout flow.
    """,
    tags=["Order"],
)
class CartView(APIView):
    serializer_class = CartSerializer

    def get_object(self):
        return Cart.objects.get_or_create(created_by=self.request.user)[0]

    def get(self, request):
        context = {"result": "Success"}
        cart = self.get_object()

        
        if cart.discount_code is not None and not cart.discount_code.code_validation():
            cart.discount_code = None
            cart.save()
            context["warning"] = "Discounted Code Expired!"
        
        
        cart.items.update(discounted=0)
        
        if cart.discount_code is not None and cart.discount_code.included_type == "product":
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
            discounted_item.order_by("-total_price_items").first().discount_calculate()
        context["cart_detail"] = self.serializer_class(instance=cart).data

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
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="User Cart ID",
            required=True,
        ),
    ],
    tags=["Order"],
)

# ----- Item To Cart ------#
class CartAddItem(generics.UpdateAPIView):
    serializer_class = AddToCartSerializer

    def get_queryset(self):
        return Cart.objects.filter(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        data = self.request.data

        self.serializer_class(data=data).is_valid(
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
            description="User Cart ID",
            required=True,
        ),
    ],
    tags=["Order"],
)
class CartRemoveItem(CartAddItem):
    serializer_class = RemoveFromCartSerializer

    def update(self, request, *args, **kwargs):
        data = self.request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)  # For Validation Item ID

        item = get_object_or_404(
            CartItem,
            id=data["id"],
            created_by=self.request.user,
            cart=self.get_object(),
        )

        item.count -= 1
        item.save()

        if serializer.data["deleted"] or item.count == 0:
            item.delete_hard()
            return Response(
                {"result": "Item Deleted from cart"}, status=status.HTTP_200_OK
            )

        # better performance?

        # if serializer.data["deleted"]:
        #     item.delete_hard()
        #     return Response(
        #         {"result": "Item Deleted from cart"}, status=status.HTTP_200_OK
        #     )

        # item.count -= 1
        # item.save()

        # if item.count == 0:
        #     item.delete_hard()
        #     return Response({"result": "Item Deleted from cart"}, status=status.HTTP_200_OK)

        return Response(
            {"result": "Item decrease from cart"}, status=status.HTTP_200_OK
        )


class ApplyDiscount(generics.UpdateAPIView):
    serializer_class = ApplyDiscountSerializer

    def get_queryset(self):
        return Cart.objects.filter(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.get_object()
        
        if obj.discount_code:
            obj.discount_code = None
            obj.save()
            return Response({"result": "Discount UnApplied."})
        
        discount_code = get_object_or_404(DiscountCode, code=serializer.validated_data["code"])

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
