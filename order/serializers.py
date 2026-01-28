from rest_framework import serializers

from order.models import Cart, CartItem, Delivery
from product.models import Color, Product, ProductColor

class IDSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    deleted = serializers.BooleanField(required = False)

class DeliverySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Delivery
        fields = ['id','name','price','is_active']

class ColorOrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Color
        fields = ['name','code']

class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = ['name']

class ProductColorSerializer(serializers.ModelSerializer):
    product = ProductSerializer() 
    color = ColorOrderSerializer()
    class Meta:
        model = ProductColor
        fields = ['id','product','color','price']

class CartItemSerializer(serializers.ModelSerializer):
    product_color = ProductColorSerializer()
    class Meta:
        model = CartItem
        fields = ['id','product_color','count','total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many = True)
    item_count = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id','status','discount_code','delivery_type','total_price','item_count','items']
        
    def get_item_count(self,obj):
        return obj.items.count()