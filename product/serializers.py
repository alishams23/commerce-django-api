from rest_framework import serializers
from order.models import CartItem
from product.models import (
    Brand,
    Category,
    CategoryChildren,
    Color,
    Product,
    ProductColor,
    ProductComment,
    ProductImage,
)
from user.serializers import UserCommentsSerializer
from django.db.models import Sum

# <------------ Brand and Color List ---------------->


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name"]


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["id", "name", "code"]

# <------------ Category List ---------------->


class CategoryChildrenListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryChildren
        fields = ["id", "name", "order","show_in_menu","icon"]


class CategoryListSerializer(serializers.ModelSerializer):
    children = CategoryChildrenListSerializer(many=True)

    class Meta:
        model = Category
        fields = ["id", "name", "order", "children"]




# <------------ Comment ---------------->

class ProductCommentSerializer(serializers.ModelSerializer):
    created_by = UserCommentsSerializer()
    replies = serializers.SerializerMethodField("get_replies")

    class Meta:
        model = ProductComment
        fields = ["id", "created_by","created_at","text", "replies"]

    def get_replies(self, obj):
        if obj.replies.exists():
            return ProductCommentSerializer(obj.replies.all(), many=True).data
        return None

class ProductAddCommentSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required = True)
    comment_id = serializers.IntegerField(required = False,help_text = "The ID of the parent comment if this comment is a reply")
    text = serializers.CharField(max_length=700)


class ImageProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "order", "is_cover"]


# <------------ ProductColors ---------------->
class ProductColorSerializer(serializers.ModelSerializer):
    images = ImageProductSerializer(many=True)
    color = ColorSerializer()
    cart_details = serializers.SerializerMethodField()

    class Meta:
        model = ProductColor
        fields = ["id", "color", "price","discounted_price", "stock", "cart_details", "images"]

    def get_cart_details(self,obj):
        user = self.context.get("request").user
        
        if user.is_authenticated:

            item = CartItem.objects.filter(
                cart = user.created_cart_set,
                created_by=user,
                product_color=obj
            ).first()

            if item:
                return {
                    "item_id": item.id, 
                    "count": item.count 
                }
                  
        return None
        
    
# <------------ Product List ---------------->

class ProductListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source = "public_id")
    colors = ProductColorSerializer(many = True)
    class Meta:
        model = Product
        fields = ["id", "name","slug","fixed_price","discount_percentage","colors"]
        
# <------------ Product List Interests ---------------->
class ProductListInterestsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source = "public_id")
    stock = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ["id", "name","slug","fixed_price","discount_percentage","stock",'image']
    
    def get_image(self,obj):
        product_image = ProductImage.objects.filter(product_color__product = obj,is_cover = True,order = 0).first()
        if product_image is None:
            return None
        return self.context.get("request").build_absolute_uri(product_image.image.url)
    
    def get_stock(self,obj):
        aggregate = obj.colors.aggregate(total_stock = Sum('stock'))
        return aggregate['total_stock'] or 0

# <------------ Product Detail ---------------->
class ProductDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source = "public_id")
    brand = BrandSerializer()
    colors = ProductColorSerializer(many=True)
    user_interest = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "brand",
            "fixed_price",
            "discount_percentage",
            "is_published",
            "is_favorite",
            "user_interest",
            "specifications",
            "description",
            "colors",
        ]
    
    def get_user_interest(self,obj):
        user = self.context.get("request").user 
        if user.is_authenticated:
            return(user.interests.filter(id = obj.id).exists())
        return False

# <------------ Category Detail ---------------->


class CategoryChildrenDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True)

    class Meta:
        model = CategoryChildren
        fields = ["id", "name", "order", "products"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    children = CategoryChildrenDetailSerializer(many=True)

    class Meta:
        model = Category
        fields = ["id", "name", "order", "children"]
