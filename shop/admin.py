from django.contrib import admin
from django.contrib import messages

from .models import ShopSettings


@admin.register(ShopSettings)
class ShopSettingsAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "province",
        "is_sale_active",
        "updated_at",
    )

    list_filter = (
        "province",
        "is_sale_active",
    )

    search_fields = (
        "name",
    )

    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": ("name", "province")
        }),
        ("وضعیت فروش", {
            "fields": ("is_sale_active", "maintenance_message")
        }),
    )

    def has_add_permission(self, request):
        """
        جلوگیری از ساخت بیش از یک تنظیمات
        """
        if ShopSettings.objects.exists():
            return False
        return True

    def changelist_view(self, request, extra_context=None):
        """
        اگر هنوز تنظیمات ساخته نشده، پیام راهنما بده
        """
        if not ShopSettings.objects.exists():
            self.message_user(
                request,
                "هنوز تنظیمات فروشگاه ساخته نشده است. لطفاً یک مورد ایجاد کنید.",
                level=messages.WARNING
            )
        return super().changelist_view(request, extra_context=extra_context)