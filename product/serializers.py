from rest_framework import serializers
from product.models import (
    Brand,
    Category,
    CategoryChildren,
    Color,
    Gallery,
    Product,
    ProductColor,
    ProductComment,
    ProductImage,
)
from user.serializers import UserCommentsSerializer

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
        fields = ["id", "name", "order"]


class CategoryListSerializer(serializers.ModelSerializer):
    children = CategoryChildrenListSerializer(many=True)

    class Meta:
        model = Category
        fields = ["id", "name", "order", "children"]




# <------------ Comment ---------------->

class CommentSerializer(serializers.ModelSerializer):
    created_by = UserCommentsSerializer()
    replies = serializers.SerializerMethodField("get_replies")

    class Meta:
        model = ProductComment
        fields = ["id", "created_by", "text", "is_approved", "replies"]

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return None


# class CommentReplySerializer(serializers.ModelSerializer):
#     user = UserCommentsSerializer()
#     class Meta:
#         model = ProductComment
#         fields = ['id','user','text','is_approved','replies']

# class CommentSerializer(serializers.ModelSerializer):
#     user = UserCommentsSerializer()
#     replies = CommentReplySerializer(many = True)
#     class Meta:
#         model = ProductComment
#         fields = ['id','user','text','is_approved','replies']


class ImageProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "order", "is_cover"]


# <------------ ProductColors ---------------->
class ProductColorSerializer(serializers.ModelSerializer):
    images = ImageProductSerializer(many=True)
    color = ColorSerializer()
    class Meta:
        model = ProductColor
        fields = ["id", "color", "price","discounted_price", "stock", "images"]

# <------------ Product List ---------------->

class ProductListSerializer(serializers.ModelSerializer):
    colors = ProductColorSerializer(many = True)
    class Meta:
        model = Product
        fields = ["id", "name", "fixed_price","discount_percentage","discounted_price","colors"]

# <------------ Product Detail ---------------->
class ProductDetailSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    colors = ProductColorSerializer(many=True)
    comments = CommentSerializer(many=True)
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "brand",
            "fixed_price",
            "discount_percentage ",
            "is_published",
            "is_favorite",
            "specifications",
            "description",
            "colors",
            "comments",
        ]


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

# <------------ Gallery ---------------->

class GallerySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Gallery
        fields = ['id','order','image']