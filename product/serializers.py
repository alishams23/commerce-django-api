from rest_framework import serializers
from product.models import Category, CategoryChildren, Product, ProductColor, ProductImage


# <------------ Category List ---------------->

class CategoryChildrenListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryChildren
        fields = ['id','name','order']

class CategoryListSerializer(serializers.ModelSerializer):
    children = CategoryChildrenListSerializer(many = True)
        
    class Meta:
        model = Category
        fields = ['id','name','order','children']

# <------------ Product List ---------------->

class ProductListSerializer(serializers.ModelSerializer):
    cover_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id','name','fixed_price','cover_image']
    
    def get_cover_image(self,obj):
        img = ProductImage.objects.filter(product_color__product_id = obj.id,is_cover = True).first()
        if img:
            return self.context.get("request").build_absolute_uri(img.image.url)
        
    
# <------------ Product Detail ---------------->

class ImageProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id','image','order','is_cover']

class ColorProductSerializer(serializers.ModelSerializer):
    images  = ImageProductSerializer(many = True)
    class Meta:
        model = ProductColor
        fields = ['id','name','code','price','stock','images']

class ProductDetailSerializer(serializers.ModelSerializer):
    colors = ColorProductSerializer(many = True)
    class Meta:
        model = Product
        fields = ['id','name','brand','fixed_price','percentage','is_published','is_favorite','specifications','description','colors']
        
# <------------ Category Detail ---------------->

class CategoryChildrenDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many = True)
    class Meta:
        model = CategoryChildren
        fields = ['id','name','order','products']

class CategoryDetailSerializer(serializers.ModelSerializer):
    children = CategoryChildrenDetailSerializer(many = True)
        
    class Meta:
        model = Category
        fields = ['id','name','order','children']
        



