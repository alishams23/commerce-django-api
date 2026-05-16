from django.db import models
from django.utils.text import slugify
from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel
from colorfield.fields import ColorField
from django_ckeditor_5 import fields as ckeditor_fields

from django.utils.translation import gettext_lazy as _


from product.utils import encode_product_id
# Create your models here.


class Category(AuditableModel, SoftDeleteModel):
    name = models.CharField(
        max_length=50, unique=True, verbose_name=_("Parent Category Name")
    )
    order = models.PositiveIntegerField(
        default=0, verbose_name=_("Display Order"), db_index=True
    )
    is_active = models.BooleanField(
        default=True, verbose_name=_("Active / Inactive"), db_index=True
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Parent Category")
        verbose_name_plural = _("Parent Categories")


class CategoryChildren(AuditableModel, SoftDeleteModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="children",
        verbose_name=_("Parent Category"),
    )
    name = models.CharField(
        max_length=50, unique=True, verbose_name=_("Child Category Name")
    )
    order = models.PositiveIntegerField(
        default=0, verbose_name=_("Display Order"), db_index=True
    )

    icon = models.ImageField(
        upload_to="products/images/category-children/icon/",
        blank=True,
        null=True,
        verbose_name=_("Category Icon"),
    )

    show_in_menu = models.BooleanField(
        default=False,
        verbose_name=_("Show in Menu"),
        help_text=_(
            "Enable this option to display this category in the main website category menu."
        ),
    )

    is_active = models.BooleanField(
        default=True, verbose_name=_("Active / Inactive"), db_index=True
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Child Category")
        verbose_name_plural = _("Child Categories")
        indexes = [
            models.Index(fields=["category", "is_active", "is_deleted"]),
        ]


class Brand(AuditableModel, SoftDeleteModel):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Brand Name"))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")


class Product(AuditableModel, SoftDeleteModel):
    category = models.ForeignKey(
        CategoryChildren,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Product Category"),
        db_index=True,
    )

    name = models.CharField(max_length=100, verbose_name=_("Product Name"))

    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        blank=True,
        verbose_name=_("Product Slug"),
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="products",
        verbose_name=_("Brand"),
    )

    specifications = ckeditor_fields.CKEditor5Field(
        blank=True, null=True, verbose_name=_("Specifications")
    )

    description = ckeditor_fields.CKEditor5Field(
        blank=True, null=True, verbose_name=_("Product Description")
    )

    fixed_price = models.PositiveBigIntegerField(
        default=0,
        verbose_name=_("Base Price (Toman)"),
        help_text=_(
            "If the base price of the product or all of its colors is 0, the product will be considered free."
        ),
        db_index=True,
    )

    discount_percentage = models.PositiveIntegerField(
        default=0, verbose_name=_("Product Discount Percentage")
    )

    is_published = models.BooleanField(
        default=True, verbose_name=_("Published"), db_index=True
    )

    is_favorite = models.BooleanField(default=False, verbose_name=_("Featured Product"))

    @property
    def public_id(self):
        return encode_product_id(self.id)

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug

            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        unique_together = ("name", "category")
        indexes = [
            models.Index(fields=["category", "is_published", "is_deleted"]),
            models.Index(fields=["fixed_price"]),
        ]


class Color(AuditableModel, SoftDeleteModel):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Color Name"))

    code = ColorField(default="#ffffff", unique=True, verbose_name=_("Color HEX Code"))

    def __str__(self):
        return f"رنگ {self.name}"

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.lower()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Color")
        verbose_name_plural = _("Colors")
        unique_together = ("name", "code")


class ProductColor(AuditableModel, SoftDeleteModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="colors",
        verbose_name=_("Product"),
        db_index=True,
    )

    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Color"),
        db_index=True,
    )

    base_price = models.PositiveBigIntegerField(
        default=0,
        verbose_name=_("Color Price (Toman)"),
        help_text=_(
            "If no price is set for this color, the product base price will be used."
        ),
    )

    base_discount = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Color Discount Percentage"),
        help_text=_(
            "If no discount is set for this color, the product default discount will be applied."
        ),
    )

    stock = models.PositiveIntegerField(default=0, verbose_name=_("Stock Quantity"))

    @property
    def price(self):
        return self.base_price if self.base_price != 0 else self.product.fixed_price

    @property
    def discount_percentage(self):
        return (
            self.base_discount
            if self.base_discount != 0
            else self.product.discount_percentage
        )

    @property
    def discounted_price(self):
        return self.price - (self.price * self.discount_percentage // 100)

    def __str__(self):
        return f"{self.product} - {self.color}"

    def save(self, *args, **kwargs):
        product = self.product
        if product.fixed_price == 0 or product.fixed_price > self.price:
            product.fixed_price = self.price
            product.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Product Color")
        verbose_name_plural = _("Product Colors")
        unique_together = ("product", "color")


class ProductImage(AuditableModel, SoftDeleteModel):
    product_color = models.ForeignKey(
        ProductColor,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Product Color"),
        db_index=True,
    )

    image = models.ImageField(
        upload_to="products/images/product-color/", verbose_name=_("Product Image")
    )

    order = models.PositiveIntegerField(
        default=0, verbose_name=_("Display Order"), db_index=True
    )

    is_cover = models.BooleanField(
        default=False,
        verbose_name=_("Cover Image"),
        help_text=_(
            "Use this image as the product preview in lists such as comments, favorites, or product listings."
        ),
        db_index=True,
    )

    def __str__(self):
        return f"{self.product_color}"

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")


class ProductCommentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_approved=True)


class ProductComment(AuditableModel, SoftDeleteModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("Product"),
        db_index=True,
    )

    text = models.TextField(verbose_name=_("Comment Text"))

    reply = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="replies",
        verbose_name=_("Reply To"),
    )

    is_approved = models.BooleanField(
        default=True, verbose_name=_("Approved"), db_index=True
    )
    objects = ProductCommentManager()

    all_objects = models.Manager()

    def __str__(self):
        return f"{self.product.name} - {self.pk}"

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Product Comment")
        verbose_name_plural = _("Product Comments")
