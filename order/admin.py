from django.contrib import admin
from django.utils.html import format_html
from core.admins.auditable import AuditableExcludeAdmin
from .models import Cart, CartItem, Delivery, DiscountCode, Order, OrderItem
from django import forms

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    pass
@admin.register(Delivery)
class DeliveryAdmin(AuditableExcludeAdmin):
    list_display = ("name", "cost", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order_display",
        "product_name",
        "color_name",
        "product_price",
        "product_count",
        "total_price",
        "created_at",
    )
    list_filter = ("order", "created_at", "updated_at")
    search_fields = ("order__number", "product_name")
    readonly_fields = (
        "order",
        "product_name",
        "color_code",
        "color_name",
        "product_price",
        "product_count",
        "total_price",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "color_display",
    )
    ordering = ("-created_at",)
    fieldsets = (
        ("اطلاعات سفارش مادر", {
            "fields": (
                "order",
            )
        }),
        ("مشخصات محصول انتخاب شده", {
            "fields": (
                "product_name", 
                "product_count",
                "product_price", 
                "total_price",
                "color_name",
                "color_display",
                
            )
        }),
        ("اطلاعات سیستمی", {
            "classes": ("collapse",),
            "fields": (
                "created_at",
                "updated_at",
                "created_by",
                "updated_by",
            )
        }),
    )
    def color_display(self, obj):
        if not obj.color_code:
            return "-"
        return format_html(
            '<div style="display:flex;align-items:center;gap:8px;">'
            '<span style="width:18px;height:18px;border-radius:4px;display:inline-block;background:{};border:1px solid #ccc;"></span>'
            '<code>{}</code>'
            '</div>',
            obj.color_code,
            obj.color_code
        )

    color_display.short_description = "رنگ"
    
    def order_display(self, obj):

        return obj.order.number if obj.order else "بدون سفارش"

    order_display.short_description = "شماره سفارش"

    def total_price(self, obj):

        return obj.calculate_total_price()

    total_price.short_description = "جمع جزء (تومان)"

    def __str__(self):
        return f"آیتم سفارش {self.order_display}"

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم های سفارشات"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = (
        "product_name",
        "color_name",
        "color_display",
        "product_price",
        "product_count",
        "total_price",
    )
    readonly_fields = (
        "total_price",
        "product_name",
        "color_name",
        "product_price",
        "product_count",
        "color_display",
    )
    can_delete = True
    
    def color_display(self, obj):
        if not obj.color_code:
            return "-"
        return format_html(
            '<div style="display:flex;align-items:center;gap:8px;">'
            '<span style="width:18px;height:18px;border-radius:4px;display:inline-block;background:{};border:1px solid #ccc;"></span>'
            '<code>{}</code>'
            '</div>',
            obj.color_code,
            obj.color_code
        )

    color_display.short_description = "رنگ"
    def total_price(self, obj):
        return obj.calculate_total_price()

    total_price.short_description = "جمع جزء"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "user_display",
        "status",
        "transaction_code",
        "total_price",
        "discount_price",
        "delivery_price",
        "final_price",
    )

    list_filter = ("status", "send_date", "created_at")
    search_fields = (
        "number",
        "transaction_code",
        "phone_number",
        "email",
        "first_name",
        "last_name",
    )
    readonly_fields = (
        "number",
        "created_by",
        "updated_by",
        "transaction_code",
        "description",
        "first_name",
        "last_name",
        "phone_number",
        "email",
        "is_different_address",
        "province",
        "city",
        "address",
        "zip_code",
        "total_price",
        "discount_price",
        "delivery_price",
        "final_price",
        "created_at",
        "updated_at",
    )
    inlines = [OrderItemInline]
    ordering = ("-created_at",)

    fieldsets = (
        ("اطلاعات اصلی سفارش", {
            "fields": (
                "transaction_code",
                "send_date",
                "tracking_code",
            )
        }),
        
        ("مشخصات خریدار", {
            "fields": (
                "created_by", 
                "first_name", 
                "last_name",
                "phone_number", 
                "email",
            )
        }),
        
        ("جزئیات ارسال و آدرس", {
            "classes": ("collapse",),
            "fields": (
                "is_different_address",
                "province", 
                "city",
                "address",
                "zip_code",
                "description",
            )
        }),
        
        ("مبالغ و صورت‌حساب (تومان)", {
            "fields": (
                "total_price",
                "discount_price",
                "delivery_price",
                "final_price",
            ),
            "description": "تمامی مبالغ به واحد تومان می‌باشد."
        }),
                
        ("اطلاعات سیستمی", {
            "classes": ("collapse",),
            "fields": (
                "created_at",
                "updated_at",
                "updated_by",
            )
        }),
    )

    def user_display(self, obj):
        if obj.created_by:
            return obj.created_by.phone_number
        return "کاربر نامشخص"

    user_display.short_description = "کاربر"

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"


# ------------------- DiscountCode -------------------
@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "amount",
        "is_percentage",
        "max_usage",
        "current_usage",
        "expired_at",
        "included_type",
    )
    list_editable = ("is_percentage", "included_type")
    exclude = ('is_deleted',)

    filter_horizontal = ("products",)
    list_filter = ("is_percentage", "included_type", "expired_at")
    search_fields = ("name", "code", "products__name")
    ordering = ("-created_at",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    
    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": (
                "name",
                "code",
                "included_type",
            )
        }),

        ("مشخصات تخفیف", {
            "fields": (
                ("amount", "is_percentage"),
            ),
            "description": "اگر درصدی است، مقدار باید بین 0 تا 100 باشد."
        }),

        ("محدودیت و استفاده", {
            "fields": (
                "max_usage",
                "current_usage",
                "expired_at",
            ),
        }),

        ("محصولات شامل تخفیف", {
            "classes": ("collapse",),
            "fields": ("products",),
            "description": "این بخش برای زمانی هست که کدتخفیف شامل محصول/محصولات باشه."
        }),

        ("اطلاعات سیستمی", {
            "classes": ("collapse",),
            "fields": (
                "created_at",
                "updated_at",
                "created_by",
                "updated_by",
            ),
        }),
    )

    def clean_amount(self, cleaned_data):
        if cleaned_data["is_percentage"] and cleaned_data["amount"] > 100:
            raise forms.ValidationError("مقدار تخفیف نمی تواند بیشتر از 100 درصد باشد")
        return cleaned_data["amount"]
