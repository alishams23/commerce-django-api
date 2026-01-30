from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from order.models import Cart, CartItem, Delivery, DiscountCode
from order.serializers import CartSerializer, DeliverySerializer

from product.models import ProductColor
from order.serializers import AddToCartSerializer,RemoveFromCartSerializer

from drf_spectacular.utils import extend_schema
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
    def get(self, request):
        return Response(
            {
                "result": "Success",
                "cart_detail": self.serializer_class(
                    instance=Cart.objects.get_or_create(created_by=self.request.user)[0]
                ).data,
            },
            status=status.HTTP_200_OK,
        )

@extend_schema(
    summary="Add item to cart",
    description="""
        Adds a product color to the user's cart or increases its quantity by one.

        Used when the user clicks the "Add to cart" button.
    """,
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
    tags=["Order"],
)

class CartRemoveItem(CartAddItem):
    serializer_class = RemoveFromCartSerializer
    def update(self, request, *args, **kwargs):
        data = self.request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)  # For Validation Item ID

        # region comment
        # product_color = get_object_or_404(ProductColor, id = data["product_color_id"])

        # if product_color.stock == 0:
        #     return Response(
        #         {"Error": "Stock This Color From Product is 0"},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        # endregion

        item = get_object_or_404(
            CartItem,
            id=data["id"],
            created_by=self.request.user,
            cart=self.get_object(),
        )  # product_color=product_color

        item.count -= 1
        item.save()

        if serializer.data["deleted"] or item.count == 0:
            item.delete_hard()
            return Response(
                {"result": "Item Deleted from cart"}, status=status.HTTP_200_OK
            )

        # better performance?
        # item.count -= 1
        # item.save()

        # if item.count == 0:
        #     item.delete_hard()
        #     return Response({"result": "Item Deleted from cart"}, status=status.HTTP_200_OK)

        return Response(
            {"result": "Item decrease from cart"}, status=status.HTTP_200_OK
        )


class ApplyDiscount(generics.UpdateAPIView):
    def get_queryset(self):
        return Cart.objects.filter(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        data = self.request.data
        discount_code = get_object_or_404(DiscountCode, code=data["code"])
        obj = self.get_object()

        if discount_code.included_type == "cart":
            discount_result = discount_code.apply_discount(amount=obj.total_price)

        elif discount_code.included_type == "product":
            qs = obj.items.filter(product_color__product_id__in = discount_code.products.values_list("id",flat = True))
            if qs.exists():
                product = qs.first().product_color.product
                discount_result = discount_code.apply_discount(product = product if product else None)

        if type(discount_result) is not float:
            return Response(discount_result, status=status.HTTP_400_BAD_REQUEST)
        
        obj.discount_code = discount_code
        
        obj.save()
        
        return Response({"result": discount_result})
