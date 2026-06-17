from django.db import models
from django.core.exceptions import ValidationError

from core.constants.provinces import ProvinceChoices
from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel


class ShopSettings(AuditableModel,SoftDeleteModel):
    name = models.CharField(max_length=150, verbose_name="نام فروشگاه")

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
        blank=True,
        null=True,
        default="در حال حاضر فروش موقتاً غیرفعال است",
        verbose_name="پیام وضعیت غیرفعال"
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
    