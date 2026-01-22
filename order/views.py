from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from order.models import Cart, CartItem, Delivery
from order.serializers import CartSerializer, DeliverySerializer

from product.models import  ProductColor
from order.serializers import IDSerializer
# Create your views here.


class DeliveryView(generics.ListAPIView):
    permission_classes = AllowAny
    serializer_class = DeliverySerializer
    queryset = Delivery.objects.filter(is_active=True)


class CartView(APIView):
    def get(self, request):
        return Response(
            {
                "result": "Success",
                "cart_detail": CartSerializer(
                    instance = Cart.objects.get_or_create(created_by=self.request.user)[0]
                ).data,
            },
            status=status.HTTP_200_OK,
        )


# ----- Item To Cart ------#
class CartAddItem(generics.UpdateAPIView):
    serializer_class = IDSerializer 

    def get_queryset(self):
        return Cart.objects.filter(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        data = self.request.data
        
        self.serializer_class(data = data).is_valid(raise_exception = True)#For Validation ProductColor ID
        
        product_color = get_object_or_404(ProductColor, id = data["id"])

        if product_color.stock == 0:
            return Response(
                {"Error": "Stock This Color From Product is 0"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item, created = CartItem.objects.get_or_create(created_by = self.request.user,
            cart=self.get_object(), product_color=product_color
        ) 
        
        if not created and item.count >= product_color.stock:
            return Response(
                {"Error": "Stock This Color From Product is 0"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        
        if not created:   # default Count = 1
            item.count += 1
        item.save()
        return Response(
            {"result": "Add Item To Cart Success"}, status=status.HTTP_200_OK
        )
        
class CartRemoveItem(CartAddItem):

    def update(self, request, *args, **kwargs):
        
        data = self.request.data
        
        self.serializer_class(data = data).is_valid(raise_exception = True)#For Validation Item ID

        # product_color = get_object_or_404(ProductColor, id = data["product_color_id"])

        # if product_color.stock == 0:
        #     return Response(
        #         {"Error": "Stock This Color From Product is 0"},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        item = get_object_or_404(CartItem,id = data["id"] ,created_by = self.request.user,cart=self.get_object())  #product_color=product_color
        
        item.count -= 1
        item.save()
    
        if item.count == 0:
            item.delete_hard()
            
        return Response(
            {"result": " Item To Cart Removed"}, status=status.HTTP_200_OK
        )


