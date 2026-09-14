from django.contrib import admin
from django.contrib import messages

from .models import AboutUs, ShopSettings


@admin.register(ShopSettings)
class ShopSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "اطلاعات عمومی فروشگاه",
            {
                "fields": (
                    "name",
                    "logo",
                    "province",
                )
            },
        ),
        (
            "وضعیت فروش",
            {
                "fields": (
                    "is_sale_active",
                    "maintenance_message",
                )
            },
        ),
        (
            "اطلاعات پشتیبانی",
            {
                "fields": (
                    "support_phone",
                    "support_mobile",
                )
            },
        ),
        (
            "شبکه‌های اجتماعی",
            {
                "fields": (
                    "instagram_url",
                    "telegram_url",
                )
            },
        ),
        (
            "اطلاعات فوتر",
            {
                "fields": (
                    "shop_address",
                    "factory_address",
                    "footer_text",
                )
            },
        ),
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
    
    
@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "محتوای درباره ما",
            {
                "fields": (
                    "title",
                    "text",
                )
            },
        ),
        (
            "رسانه",
            {
                "description": (
                    "رسانه را فقط به یکی از دو روش زیر وارد کنید: "
                    "یا لینک رسانه را وارد کنید یا فایل رسانه را آپلود کنید. "
                    "هر دو روش را همزمان استفاده نکنید."
                ),
                "fields": (
                    "media_type",
                    "media_url",
                    "media_file",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return not AboutUs.objects.exists()