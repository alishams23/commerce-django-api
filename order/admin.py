from django.contrib import admin
from django.db.models import Sum, F
from django.utils.html import format_html
from .models import Delivery, DifferentAddress, Cart, CartItem, Order, OrderItem



#region boof ai
# ---------------------------------------------------------------------
# Inline Classes
# ---------------------------------------------------------------------


# class CartItemInline(admin.TabularInline):
#     model = CartItem
#     extra = 0
#     readonly_fields = ("product", "count", "total_price")
#     can_delete = True

#     def product(self, obj):
#         return obj.product_color

#     product.short_description = "محصول"

#     def total_price(self, obj):
#         return f"{obj.total_price:,} تومان"

#     total_price.short_description = "جمع قیمت"


# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 0
#     readonly_fields = ("product_name", "product_count", "product_price", "total_price")
#     can_delete = False

#     def total_price(self, obj):
#         return f"{obj.total_price:,} تومان"

#     total_price.short_description = "جمع قیمت"


# # ---------------------------------------------------------------------
# # Model Admins
# # ---------------------------------------------------------------------


# @admin.register(Delivery)
# class DeliveryAdmin(admin.ModelAdmin):
#     list_display = ("name", "cost", "is_active")
#     list_filter = ("is_active",)
#     search_fields = ("name",)


# @admin.register(DifferentAddress)
# class DifferentAddressAdmin(admin.ModelAdmin):
#     list_display = ("user", "province", "city", "zip_code")
#     search_fields = ("created_by__phone_number", "created_by__username", "city")

#     def user(self, obj):
#         return obj.created_by.username

#     user.short_description = "کاربر"


# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = (
#         "id",
#         "user",
#         "status",
#         "delivery_type",
#         "total_price",
#         "created_at",
#     )
#     list_filter = ("status", "delivery_type", "created_at")
#     search_fields = ("created_by__username", "created_by__phone_number")
#     list_select_related = ("created_by", "delivery_type")
#     inlines = [CartItemInline]
#     readonly_fields = ("total_price", "created_at")

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.annotate(
#             calculated_total=Sum(F("items__count") * F("items__product_color__price"))
#         )

#     def total_price(self, obj):
#         total = getattr(obj, "calculated_total", 0)
#         return f"{total:,} تومان"

#     total_price.short_description = "مجموع سبد"
#     total_price.admin_order_field = "calculated_total"

#     def user(self, obj):
#         return obj.created_by.username

#     user.short_description = "کاربر"


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ("id", "user", "status", "final_price", "tracking_code", "send_date")
#     list_filter = ("status", "is_different_address", "created_at")
#     search_fields = (
#         "id",
#         "tracking_code",
#         "created_by__username",
#         "created_by__phone_number",
#     )

#     # فیلدهای مالی فقط خواندنی باشند تا دستکاری نشوند
#     readonly_fields = (
#         "total_price",
#         "discount_price",
#         "delivery_price",
#         "final_price",
#         "created_at",
#         "updated_at",
#     )

#     raw_id_fields = ("created_by",)
#     inlines = [OrderItemInline]

#     fieldsets = (
#         (
#             None,
#             {
#                 "fields": (
#                     "created_by",
#                     "status",
#                     "tracking_code",
#                     "send_date",
#                     "description",
#                 )
#             },
#         ),
#         (
#             "اطلاعات مالی",
#             {
#                 "fields": (
#                     "total_price",
#                     "discount_price",
#                     "delivery_price",
#                     "final_price",
#                 ),
#             },
#         ),
#         (
#             "آدرس ارسال",
#             {
#                 "fields": (
#                     "is_different_address",
#                     "province",
#                     "city",
#                     "address",
#                     "zip_code",
#                 ),
#                 "classes": ("collapse",),  # این بخش جمع شده است تا صفحه شلوغ نباشد
#             },
#         ),
#     )

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.select_related("created_by")

#     def final_price(self, obj):
#         return f"{obj.final_price:,} تومان"

#     final_price.short_description = "مبلغ نهایی"
#     final_price.admin_order_field = "final_price"

#     def user(self, obj):
#         return obj.created_by.username

#     user.short_description = "کاربر"
#endregion


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id','name','cost','is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    
@admin.register(DifferentAddress)
class DifferentAddressAdmin(admin.ModelAdmin):
    list_display = ('id','zip_code')
    list_display = ('province','city')
    search_fields = ('province','city','address','zip_code',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id','created_by__username','total_price','status')
    list_editable = ('status',)
    list_filter = ('status','discount_code','delivery_type')
    
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id','created_by__username','total_price',)
    list_filter = ('cart',)
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass