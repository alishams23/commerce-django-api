from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from core.constants.provinces import ProvinceChoices
from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel


class ShopSettings(AuditableModel,SoftDeleteModel):
    name = models.CharField(max_length=150, verbose_name="نام فروشگاه")

    logo = models.ImageField(null = True,upload_to = "shop/images/logo/",verbose_name = "لوگوی فروشگاه")
    
    province = models.CharField(
        max_length=50,
        choices=ProvinceChoices.choices,
        verbose_name="استان فروشگاه"
    )

    is_sale_active = models.BooleanField(
        default=True,
        verbose_name="وضعیت فروش",
        help_text="اگر غیرفعال شود، امکان ثبت سفارش وجود ندارد"
    )

    maintenance_message = models.CharField(
        max_length=255,
        default="در حال حاضر فروش موقتاً غیرفعال است",
        verbose_name="پیام وضعیت غیرفعال"
    )
    support_phone = models.CharField(
        max_length=20,
        blank = True,
        null = True,
        verbose_name="شماره تلفن ثابت پشتیبانی"
    )

    support_mobile = models.CharField(
        max_length=20,
        null = True,
        verbose_name="شماره موبایل پشتیبانی"
    )

    instagram_url = models.URLField(
        null = True,
        verbose_name="لینک اینستاگرام"
    )

    telegram_url = models.URLField(
        null = True,
        verbose_name="لینک تلگرام"
    )
    shop_address = models.TextField(
        null = True,
        verbose_name="آدرس فروشگاه"
    )

    factory_address = models.TextField(
        null = True,
        verbose_name="آدرس کارخانه"
    )
    footer_text = models.TextField(
        null = True,
        verbose_name="متن فوتر"
    )
    def __str__(self):
        return f"{self.name} - {self.province}"

    class Meta:
        verbose_name = "تنظیمات فروشگاه"
        verbose_name_plural = "تنظیمات فروشگاه"

    def clean(self):
        if not self.pk and ShopSettings.objects.exists():
            raise ValidationError("Only one ShopSettings instance is allowed")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class MediaTypeChoices(models.TextChoices):
    IMAGE = "image", "تصویر"
    VIDEO = "video", "ویدئو"

class AboutUs(AuditableModel, SoftDeleteModel):
    
    title = models.CharField(
        max_length=150,
        verbose_name="عنوان"
    )

    text = models.TextField(
        verbose_name="متن"
    )

    media_url = models.URLField(
        blank=True,
        verbose_name="لینک رسانه",
    )

    media_file = models.FileField(
        upload_to="shop/about/",
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png','webp','mov','avi','mp4','webm','mkv'])],
        verbose_name="فایل رسانه",
    )

    media_type = models.CharField(
        max_length=10,
        choices=MediaTypeChoices.choices,
        verbose_name="نوع رسانه",
        help_text=(
            "نوع رسانه را مطابق با فایل یا لینک انتخاب کنید. "
            "عدم تطابق نوع رسانه با فایل یا لینک باعث نمایش اشتباه آن در وب‌سایت خواهد شد."
        )
    )
    
    def __str__(self):
        return "درباره ما"
    class Meta:
        verbose_name = "درباره ما"
        verbose_name_plural = "درباره ما"

    def clean(self):
        if self.media_url and self.media_file:
            raise ValidationError(
                "فقط یکی از دو نوع لینک یا فایل را وارد کنید."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)