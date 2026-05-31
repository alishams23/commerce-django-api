from django.db import models
from django.utils import timezone
from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel
from django.core.exceptions import ValidationError

from product.models import Product


class Banner(AuditableModel, SoftDeleteModel):
    POSITION_CHOICES = (
        ("wide_single", "بنر عریض میانی (حداکثر ۱ عدد)"),
        ("middle_half", "بنرهای وسط صفحه (حداکثر ۲ عدد)"),
        ("side_grid_four", "بنر ستون کناری (حداکثر ۴ عدد)"),
    )

    MAX_ACTIVE_LIMITS = {
        "wide_single": 1,
        "middle_half": 2,
        "side_grid_four": 4,
    }
    title = models.CharField(max_length=100, verbose_name="عنوان بنر")
    text = models.CharField(
        max_length=150, blank=True, null=True, verbose_name="متن کوتاه"
    )
    image = models.ImageField(upload_to="banners/%Y/%m/", verbose_name="تصویر بنر")
    url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="لینک مقصد"
    )
    position = models.CharField(
        max_length=50, choices=POSITION_CHOICES, verbose_name="جایگاه نمایش"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش ",db_index=True)
    is_active = models.BooleanField(default=True, verbose_name="فعال/غیرفعال")

    def clean(self):
        super().clean()

        if self.is_active:
            limit = self.MAX_ACTIVE_LIMITS.get(self.position)

            if limit is not None:
                active_count = (
                    Banner.objects.filter(position=self.position, is_active=True)
                    .exclude(pk=self.pk)
                    .count()
                )

                if active_count >= limit:
                    raise ValidationError(
                        {
                            "is_active": f'ظرفیت پر است! شما نمی‌توانید بیشتر از {limit} بنر فعال برای جایگاه "{self.get_position_display()}" داشته باشید. لطفاً ابتدا یکی از بنرهای قبلی را غیرفعال کنید.'
                        }
                    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "بنر"
        verbose_name_plural = "بنرها"
        ordering = ["order","-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"


class Campaign(AuditableModel, SoftDeleteModel):
    title = models.CharField(
        max_length=200, verbose_name="عنوان کمپین",help_text = "(مثل پیشنهاد شگفت‌انگیز)"
    )
    start_time = models.DateTimeField(verbose_name="زمان شروع")
    end_time = models.DateTimeField(verbose_name="زمان پایان")
    is_active = models.BooleanField(default=True, verbose_name="فعال/غیرفعال")

    products = models.ManyToManyField(
        Product, related_name="campaigns", verbose_name="محصولات کمپین"
    )

    class Meta:
        verbose_name = "کمپین فروش ویژه"
        verbose_name_plural = "کمپین‌های فروش ویژه"

    def __str__(self):
        return self.title
    
    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("زمان پایان کمپین باید بعد از زمان شروع آن باشد.")
            
    @property
    def is_valid(self):
        return self.is_active and self.start_time <= timezone.now() <= self.end_time


class Gallery(AuditableModel, SoftDeleteModel):
    image = models.ImageField(upload_to="home/images/gallery/", verbose_name="عکس")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش عکس")
    is_published = models.BooleanField(
        default=True, verbose_name="وضعیت انتشار عکس", db_index=True
    )

    def __str__(self):
        return f"عکس گالری {self.id} - {self.image}"

    class Meta:
        verbose_name = "عکس گالری"
        verbose_name_plural = "گالری / عکس های گالری"
        ordering = ("order", "-created_at")
