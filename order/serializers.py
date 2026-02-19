from rest_framework import serializers

from order.models import Cart, CartItem, Delivery, DiscountCode
from product.models import Color, Product, ProductColor


class DiscountCodeOrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DiscountCode
        fields = ['id','name','code']

class AddToCartSerializer(serializers.Serializer):
        
    id = serializers.IntegerField(
        help_text="ProductColor ID of the selected product variant"
    )
    
class RemoveFromCartSerializer(serializers.Serializer):
    
    id = serializers.IntegerField(
        help_text="CartItem ID to decrease or remove from the cart"
    )
    deleted = serializers.BooleanField(required = False,help_text="Force remove item from cart instead of decreasing quantity")

class DeliverySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Delivery
        fields = ['id','name','cost','is_active']

class ColorOrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Color
        fields = ['name','code']

class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = ['name']

class ProductColorCartSerializer(serializers.ModelSerializer):
    product = ProductSerializer() 
    color = ColorOrderSerializer()
    class Meta:
        model = ProductColor
        fields = ['id','product','color','price','discounted_price']

class CartItemSerializer(serializers.ModelSerializer):
    product_color = ProductColorCartSerializer()
    class Meta:
        model = CartItem
        fields = ['id','product_color','count','total_price','discounted_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many = True)
    discount_code = DiscountCodeOrderSerializer()
    item_count = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id','status','discount_code','delivery_type','total_price','discounted_price','item_count','items']
        
    def get_item_count(self,obj):
        return obj.items.count()
    
class ApplyDiscountSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required = True)
    class Meta:
        model = DiscountCode
        fields = ['code']