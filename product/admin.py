from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.admins.auditable import AuditableExcludeAdmin
from .models import Category, CategoryChildren, Brand, Color, Product, ProductColor, ProductImage, ProductComment
# ------------------- Inlines -------------------
class CategoryChildrenInline(admin.TabularInline):
    model = CategoryChildren
    extra = 1
    fields = ('name', 'order','is_active','show_in_menu','icon')
    ordering = ('order',)
    verbose_name = "دسته بندی فرزند"
    verbose_name_plural = "دسته بندی‌های فرزند"

class ProductColorImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'order', 'is_cover')
    ordering = ('-created_at',)
    verbose_name = "عکس محصول"
    verbose_name_plural = "عکس های این رنگ از محصول"
    
class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1
    fields = ('product', 'color', 'stock','base_price','base_discount')
    ordering = ('-created_at',)
    autocomplete_fields = ['color']
    verbose_name = "رنگ محصول"
    verbose_name_plural = "رنگ بندی محصولات"
    

# ------------------- Category -------------------
@admin.register(Category)
class CategoryAdmin(AuditableExcludeAdmin):
    list_display = ('name', 'order', 'created_at', 'updated_at','is_active','is_deleted')
    list_editable = ('order','is_active','is_deleted')
    search_fields = ('name',)
    ordering = ('order',)
    inlines = [CategoryChildrenInline]

# ------------------- CategoryChildren -------------------
@admin.register(CategoryChildren)
class CategoryChildrenAdmin(AuditableExcludeAdmin):
    list_display = ('name', 'category', 'order', 'created_at', 'updated_at','is_active','is_deleted')
    list_editable = ('order','is_active','is_deleted')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    ordering = ('category', 'order')

# ------------------- Brand -------------------
@admin.register(Brand)
class BrandAdmin(AuditableExcludeAdmin):
    list_display = ('name', 'created_at', 'updated_at','is_deleted')
    search_fields = ('name',)
    ordering = ('name',)

# ------------------- Product -------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_code', 'category', 'brand', 'fixed_price', 'is_published', 'is_favorite')
    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": (
                "name", 
                "product_code",
                "slug", 
                "category", 
                "product_type", 
                "brand", 
                "is_published", 
                "is_favorite"
            )
        }),
        ("قیمت‌گذاری و تخفیف", {
            "fields": (
                "fixed_price", 
                "discount_percentage"
            ),
            "classes": ("wide",)
        }),
        ("محتوا و توضیحات", {
            "fields": (
                "specifications", 
                "description"
            )
        }),
        ("اطلاعات سیستمی", {
            "classes": ("collapse",),
            "fields": (
                "created_at",
                "updated_at",
                "deleted_at",
                "created_by",
                "updated_by",
            )
        }),
    )
    list_display_links = ('name',)
    prepopulated_fields = {"slug":("name",)}
    list_editable = ('is_published', 'is_favorite')
    list_filter = ('category', 'brand', 'is_published', 'is_favorite')
    search_fields = ('name', 'product_code' ,'category__name', 'brand__name')
    ordering = ('category', 'name')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')
    inlines = [ProductColorInline]

# ------------------- Color -------------------
@admin.register(Color)
class ColorAdmin(AuditableExcludeAdmin):
    list_display = ('name','code','created_at', 'updated_at','is_deleted')
    search_fields = ('name','code')
    ordering = ('name',)



# ------------------- ProductColor -------------------
@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('product', 'color','price','discount_percentage','discounted_price','order','stock','is_deleted')
    list_editable = ('stock','order','is_deleted')
    list_filter = ('product','color')
    search_fields = ('product__name','color__name')
    ordering = ('product','color')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')

    autocomplete_fields = ['product','color']
    inlines = [ProductColorImageInline]
    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": (
                "product",
                "color",
            )
        }),

        ("قیمت و تخفیف", {
            "fields": (
                "base_price",
                "base_discount",
            )
        }),

        ("موجودی و ترتیب", {
            "fields": (
                "stock",
                "order",
                "is_deleted",
            ),
            "classes": ("wide",)
        }),

        ("اطلاعات سیستمی", {
            "classes": ("collapse",),
            "fields": (
                "created_at",
                "updated_at",
                "deleted_at",
                "created_by",
                "updated_by",
            )
        }),
    )
# ------------------- ProductImage -------------------
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product_color', 'image', 'order', 'is_cover', 'created_at', 'updated_at','is_deleted')
    list_editable = ('order', 'is_cover','is_deleted')
    list_filter = ('product_color',)
    search_fields = ('product_color__name',)
    ordering = ('product_color', 'order')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')

# ------------------- ProductComment -------------------
@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ('created_by', 'product', 'text', 'is_approved', 'created_at', 'updated_at','is_deleted')
    list_editable = ('is_approved','is_deleted')
    list_filter = ('product', 'created_by', 'is_approved')
    search_fields = ('user__username', 'product__name', 'text')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'updated_by')
    
    def get_queryset(self, request):
        return ProductComment.all_objects.all()
