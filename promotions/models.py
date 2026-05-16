from django.db import models
from django.utils import timezone
from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from product.models import Product


class Banner(AuditableModel, SoftDeleteModel):
    POSITION_CHOICES = (
        ("wide_single", _("Middle Wide Banner (max 1)")),
        ("middle_half", _("Middle Half Banners (max 2)")),
        ("side_grid_four", _("Side Column Banners (max 4)")),
    )

    MAX_ACTIVE_LIMITS = {
        "wide_single": 1,
        "middle_half": 2,
        "side_grid_four": 4,
    }

    title = models.CharField(
        max_length=100,
        verbose_name=_("Banner Title")
    )

    text = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name=_("Short Text")
    )

    image = models.ImageField(
        upload_to="banners/%Y/%m/",
        verbose_name=_("Banner Image")
    )

    url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_("Target URL")
    )

    position = models.CharField(
        max_length=50,
        choices=POSITION_CHOICES,
        verbose_name=_("Display Position")
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active / Inactive")
    )
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
                            "is_active": _(
                                'Capacity is full. You cannot have more than %(limit)s active banners for "%(position)s". Please deactivate one of the existing banners first.'
                            ) % {
                                "limit": limit,
                                "position": self.get_position_display(),
                            }
                        }
                    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Banner")
        verbose_name_plural = _("Banners")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"


class Campaign(AuditableModel, SoftDeleteModel):
    title = models.CharField(
        max_length=200,
        verbose_name=_("Campaign Title"),
        help_text=_("Example: Amazing Offer")
    )

    start_time = models.DateTimeField(
        verbose_name=_("Start Time")
    )

    end_time = models.DateTimeField(
        verbose_name=_("End Time")
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active / Inactive")
    )

    products = models.ManyToManyField(
        Product,
        related_name="campaigns",
        verbose_name=_("Campaign Products")
    )

    class Meta:
        verbose_name = _("Sales Campaign")
        verbose_name_plural = _("Sales Campaigns")

    def __str__(self):
        return self.title

    @property
    def is_valid(self):
        return self.is_active and self.start_time <= timezone.now() <= self.end_time


class Gallery(AuditableModel, SoftDeleteModel):
    image = models.ImageField(
        upload_to="home/images/gallery/",
        verbose_name=_("Image")
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order")
    )

    is_published = models.BooleanField(
        default=True,
        verbose_name=_("Published"),
        db_index=True
    )

    def __str__(self):
        return f"Gallery Image {self.id}"

    class Meta:
        verbose_name = _("Gallery Image")
        verbose_name_plural = _("Gallery Images")
        ordering = ("order", "-created_at")
