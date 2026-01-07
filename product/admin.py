from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Category, CategoryChildren, Brand, Color, Product, ProductColor, ProductImage, ProductComment, DiscountCode

# ------------------- Inlines -------------------
class CategoryChildrenInline(admin.TabularInline):
    model = CategoryChildren
    extra = 1
    fields = ('name', 'order','is_active','icon')
    ordering = ('order',)
    verbose_name = "دسته بندی فرزند"
    verbose_name_plural = "دسته بندی‌های فرزند"

# class ProductColorInline(admin.TabularInline):
#     model = ProductColor
#     extra = 1
#     fields = ('name', 'code', 'price', 'stock')
#     ordering = ('name',)
#     verbose_name = "رنگ محصول"
#     verbose_name_plural = "رنگ بندی محصولات"

# ------------------- Category -------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order', 'created_at', 'updated_at','is_active','is_deleted')
    list_editable = ('order','is_active','is_deleted')
    search_fields = ('name',)
    ordering = ('order',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')
    inlines = [CategoryChildrenInline]

# ------------------- CategoryChildren -------------------
@admin.register(CategoryChildren)
class CategoryChildrenAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'order', 'created_at', 'updated_at','is_active','is_deleted')
    list_editable = ('order','is_active','is_deleted')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    ordering = ('category', 'order')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')

# ------------------- Brand -------------------
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at','is_deleted')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')

# ------------------- Product -------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'brand', 'fixed_price', 'is_published', 'is_favorite', 'created_at', 'updated_at','is_deleted')
    list_editable = ('is_published', 'is_favorite','is_deleted')
    list_filter = ('category', 'brand', 'is_published', 'is_favorite')
    search_fields = ('name', 'category__name', 'brand__name')
    ordering = ('category', 'name')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')
    # inlines = [ProductColorInline]


# ------------------- Color -------------------
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','code','created_at', 'updated_at','is_deleted')
    search_fields = ('name','code')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')



# ------------------- ProductColor -------------------
@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'color','price', 'stock','is_deleted')
    list_editable = ('price', 'stock','is_deleted')
    list_filter = ('product','color')
    search_fields = ('product__name','color__name')
    ordering = ('product','color')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')

# ------------------- ProductImage -------------------
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_color', 'image', 'order', 'is_cover', 'created_at', 'updated_at','is_deleted')
    list_editable = ('order', 'is_cover','is_deleted')
    list_filter = ('product_color',)
    search_fields = ('product_color__name',)
    ordering = ('product_color', 'order')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')

# ------------------- ProductComment -------------------
@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by', 'product', 'text', 'is_approved', 'created_at', 'updated_at','is_deleted')
    list_editable = ('is_approved','is_deleted')
    list_filter = ('product', 'created_by', 'is_approved')
    search_fields = ('user__username', 'product__name', 'text')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')

# ------------------- DiscountCode -------------------
@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'amount', 'is_percentage', 'max_usage', 'current_usage', 'expired_at', 'is_all_products', 'created_at', 'updated_at','is_deleted')
    list_editable = ('is_percentage', 'is_all_products','is_deleted')
    filter_horizontal = ('products',)
    list_filter = ('is_percentage', 'is_all_products', 'expired_at')
    search_fields = ('name', 'code', 'products__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')
