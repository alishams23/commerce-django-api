from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Category, CategoryChildren, Brand, Product, ProductColor, ProductImage, ProductComment, DiscountCode

# ------------------- Inlines -------------------
class CategoryChildrenInline(admin.TabularInline):
    model = CategoryChildren
    extra = 1
    fields = ('name', 'order')
    ordering = ('order',)
    verbose_name = "دسته بندی فرزند"
    verbose_name_plural = "دسته بندی‌های فرزند"

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1
    fields = ('name', 'code', 'price', 'stock')
    ordering = ('name',)
    verbose_name = "رنگ محصول"
    verbose_name_plural = "رنگ بندی محصولات"

# ------------------- Category -------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order', 'created_at', 'updated_at')
    list_editable = ('order',)
    search_fields = ('name',)
    ordering = ('order',)
    inlines = [CategoryChildrenInline]

# ------------------- CategoryChildren -------------------
@admin.register(CategoryChildren)
class CategoryChildrenAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'order', 'created_at', 'updated_at')
    list_editable = ('order',)
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    ordering = ('category', 'order')

# ------------------- Brand -------------------
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)

# ------------------- Product -------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'brand', 'fixed_price', 'is_published', 'is_favorite', 'created_at', 'updated_at')
    list_editable = ('is_published', 'is_favorite')
    list_filter = ('category', 'brand', 'is_published', 'is_favorite')
    search_fields = ('name', 'category__name', 'brand__name')
    ordering = ('category', 'name')
    inlines = [ProductColorInline]

# ------------------- ProductColor -------------------
@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'name', 'code', 'price', 'stock')
    list_editable = ('price', 'stock')
    list_filter = ('product',)
    search_fields = ('name', 'product__name')
    ordering = ('product', 'name')

# ------------------- ProductImage -------------------
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_color', 'image', 'order', 'is_cover', 'created_at', 'updated_at')
    list_editable = ('order', 'is_cover')
    list_filter = ('product_color',)
    search_fields = ('product_color__name',)
    ordering = ('product_color', 'order')

# ------------------- ProductComment -------------------
@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'text', 'is_approved', 'created_at', 'updated_at')
    list_editable = ('is_approved',)
    list_filter = ('product', 'user', 'is_approved')
    search_fields = ('user__username', 'product__name', 'text')
    ordering = ('-created_at',)

# ------------------- DiscountCode -------------------
@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'amount', 'is_percentage', 'max_usage', 'current_usage', 'expired_at', 'is_all_products', 'created_at', 'updated_at')
    list_editable = ('is_percentage', 'is_all_products')
    filter_horizontal = ('products',)
    list_filter = ('is_percentage', 'is_all_products', 'expired_at')
    search_fields = ('name', 'code', 'products__name')
    ordering = ('-created_at',)
