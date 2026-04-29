from django.contrib import admin
from .models import Delivery, DiscountCode, Order, OrderItem
from django import forms


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "cost", "is_active")
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
    )
    ordering = ("-created_at",)

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
        "color_code",
        "product_price",
        "product_count",
        "total_price",
    )
    readonly_fields = (
        "total_price",
        "product_name",
        "color_name",
        "color_code",
        "product_price",
        "product_count",
    )
    can_delete = True

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
        (None, {"fields": ("number", "status", "created_at", "updated_at")}),
        (
            "اطلاعات مشتری",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "email",
                    "created_by",
                    "updated_by",
                )
            },
        ),
        (
            "اطلاعات آدرس ارسال",
            {
                "fields": (
                    "is_different_address",
                    "province",
                    "city",
                    "address",
                    "zip_code",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "اطلاعات مالی",
            {
                "fields": (
                    "total_price",
                    "discount_price",
                    "delivery_price",
                    "final_price",
                ),
            },
        ),
        (
            "اطلاعات حمل و نقل",
            {
                "fields": ("send_date", "tracking_code"),
                "classes": ("collapse",),
            },
        ),
        (
            "تراکنش و توضیحات",
            {
                "fields": ("transaction_code", "description"),
            },
        ),
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
        "id",
        "name",
        "code",
        "amount",
        "is_percentage",
        "max_usage",
        "current_usage",
        "expired_at",
        "included_type",
        "is_deleted",
    )
    list_editable = ("is_percentage", "included_type", "is_deleted")
    filter_horizontal = ("products",)
    list_filter = ("is_percentage", "included_type", "expired_at")
    search_fields = ("name", "code", "products__name")
    ordering = ("-created_at",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
        "created_by",
        "updated_by",
    )

    def clean_amount(self, cleaned_data):
        if cleaned_data["is_percentage"] and cleaned_data["amount"] > 100:
            raise forms.ValidationError("مقدار تخفیف نمی تواند بیشتر از 100 درصد باشد")
        return cleaned_data["amount"]
