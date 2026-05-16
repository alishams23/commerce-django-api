from django.db import models

from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel
from product.models import Product, ProductColor

from colorfield.fields import ColorField

from datetime import timedelta

from django.utils import timezone

from user.models import User

from .utils import generate_discount_code

from django.db import transaction

from django.utils.translation import gettext_lazy as _


# Create your models here.


class Delivery(AuditableModel, SoftDeleteModel):
    name = models.CharField(
        max_length=75,
        unique=True,
        verbose_name=_("Delivery Type Name"),
        help_text=_("For example: Post, Tipax, etc."),
    )
    cost = models.PositiveBigIntegerField(verbose_name=_("Delivery Cost (Toman)"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    def __str__(self):
        return f"{self.name} - {self.cost}"

    class Meta:
        verbose_name = _("Delivery")
        verbose_name_plural = _("Deliveries")


class Cart(AuditableModel, SoftDeleteModel):
    STATUS_CHOICE = (
        ("pending_pay", _("Pending Payment")),
        ("pay", _("Paid")),
        ("pay_error", _("Payment Error")),
    )
    created_by = models.OneToOneField(
        User,
        on_delete=models.CASCADE,  # Rewrote for this
        null=True,
        blank=True,
        related_name="created_%(class)s_set",
        verbose_name=_("User"),
    )
    discount_code = models.ForeignKey(
        "DiscountCode",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_used",
        verbose_name=_("Discount Code"),
    )
    delivery_type = models.ForeignKey(
        Delivery,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="cart_used",
        verbose_name=_("Delivery Type"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default="pending_pay",
        verbose_name=_("Cart Payment Status"),
    )

    @property
    def total_price(self):
        total_price = 0
        for item in self.items.all():
            total_price += item.total_price
        return total_price

    @property
    def discounted_price(self):
        item_discount = 0
        for item in self.items.all():
            item_discount += item.discounted_price

        if self.discount_code and self.discount_code.included_type == "cart":
            return self.discount_code.apply_discount(amount=item_discount)

        return item_discount

    @property
    def final_price(self):
        return self.discounted_price + (
            self.delivery_type.cost if self.delivery_type else 0
        )

    def __str__(self):
        return f"{self.created_by.phone_number} سبد خرید کاربر "

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")


class CartItem(AuditableModel, SoftDeleteModel):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Cart"),
    )
    product_color = models.ForeignKey(
        ProductColor,
        on_delete=models.PROTECT,
        related_name="cart_items",
        verbose_name=_("Product"),
    )
    count = models.PositiveIntegerField(default=1, verbose_name=_("Count"))

    discounted = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Discounted Price"),
    )

    @property
    def total_price(self):
        return self.count * self.product_color.price

    @property
    def discounted_price(self):
        return self.count * (
            self.product_color.discounted_price
            if self.discounted == 0
            else self.discounted
        )

    def discount_calculate(self):
        if self.cart.discount_code.included_type == "product":
            self.discounted = self.cart.discount_code.apply_discount(
                amount=self.discounted_price
            )
            self.save()
            return True

        return False

    def __str__(self):
        return f"آیتم {self.cart}"

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        unique_together = ("cart", "product_color")
        ordering = ("created_at",)


class Order(AuditableModel, SoftDeleteModel):
    STATUS_CHOICE = (
        ("pending_pay", _("Pending Payment")),
        ("doing", _("Preparing")),
        ("send", _("Sent")),
        ("completing", _("Completed")),
        ("canceled", _("Canceled")),
    )
    # user/author = created_by

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default="pending_pay",
        verbose_name=_("Order Status"),
    )

    number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Order Number"),
    )

    tracking_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Tracking Code"),
    )
    send_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Send Date"))

    transaction_code = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        verbose_name=_("Transaction Code"),
    )

    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    first_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("First Name"),
    )
    last_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Last Name"),
    )
    phone_number = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name=_("Phone Number"),
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_("Email"),
    )

    is_different_address = models.BooleanField(
        default=False,
        verbose_name=_("Different Address"),
    )
    province = models.CharField(
        blank=True,
        null=True,
        max_length=20,
        verbose_name=_("Province"),
    )
    city = models.CharField(
        blank=True,
        null=True,
        max_length=30,
        verbose_name=_("City"),
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Address"),
    )
    zip_code = models.CharField(
        blank=True,
        null=True,
        max_length=10,
        verbose_name=_("Zip Code"),
    )

    total_price = models.PositiveBigIntegerField(
        default=0,
        verbose_name=_("Total Items Price"),
    )
    discount_price = models.PositiveBigIntegerField(
        default=0,
        verbose_name=_("Discount Amount"),
    )
    delivery_price = models.PositiveBigIntegerField(
        default=0,
        verbose_name=_("Delivery Price"),
    )
    final_price = models.PositiveBigIntegerField(
        default=0,
        verbose_name=_("Final Price"),
    )

    def generate_number(self):
        with transaction.atomic():
            date_str = timezone.now().strftime("%Y%m%d")
            last_order = (
                Order.objects.select_for_update()
                .filter(number__startswith=date_str)
                .order_by("number")
                .last()
            )

            if last_order:
                last_num = int(last_order.number.split("-")[1]) + 1
            else:
                last_num = 1
            return f"{date_str}-{last_num:03d}"

    def __str__(self):
        return f"سفارش  {self.number}"

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")


class OrderItem(AuditableModel, SoftDeleteModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Order"),
    )

    product_name = models.CharField(
        max_length=100,
        verbose_name=_("Product Name"),
    )

    color_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Color Name"),
    )

    color_code = ColorField(
        default="#ffffff",
        verbose_name=_("Color Code"),
    )

    product_price = models.PositiveBigIntegerField(
        default=0,
        db_index=True,
        verbose_name=_("Product Price"),
    )

    product_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Product Count"),
    )

    total_price = models.PositiveBigIntegerField(
        default=0,
        verbose_name=_("Total Price"),
    )

    def calculate_total_price(self):
        return self.product_count * self.product_price

    def __str__(self):
        return f"آیتم سفارش  {self.order.number}"

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")


def default_expired_at():
    return timezone.now() + timedelta(days=2)


class DiscountCode(AuditableModel, SoftDeleteModel):
    TYPE_CHOICE = (("cart", _("Cart")), ("product", _("Product")))

    name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Discount Name"),
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        db_index=True,
        verbose_name=_("Discount Code"),
    )

    included_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICE,
        default="cart",
        verbose_name=_("Discount Type"),
    )

    amount = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Discount Amount"),
    )
    is_percentage = models.BooleanField(
        default=True,
        verbose_name=_("Percentage"),
        help_text=_(
            "If disabled, the discount amount will be calculated as a fixed Toman value."
        ),
    )
    max_usage = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Maximum Usage"),
        help_text=_(
            "If this value is 0, the code can only be used once by all users until expiration. "
            "If greater than 0, the code will remain valid until the expiration time or until "
            "the usage count reaches this limit."
        ),
    )
    current_usage = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Current Usage"),
    )
    expired_at = models.DateTimeField(
        default=default_expired_at,
        verbose_name=_("Expiration Time"),
        help_text=_(
            "By default, the expiration time is set to two days after the current system time."
        ),
    )
    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="discount_codes",
        verbose_name=_("Included Products"),
    )

    def save(self, *args, **kwargs):
        if self.code == "":
            while True:
                code = generate_discount_code()
                if not self.__class__.objects.filter(code=code).exists():
                    self.code = code
                    break
        super().save(*args, **kwargs)

    def code_validation(self):
        if (
            self.max_usage != 0 and (self.current_usage == self.max_usage)
        ) or timezone.now() > self.expired_at:
            return False
        return True

    def apply_discount(self, amount: float):
        if self.is_percentage:
            return amount - (amount * self.amount) // 100
        elif amount > self.amount:
            return amount - self.amount
        return 0

    def increment_usage(self):
        self.current_usage += 1
        self.save()

    def __str__(self):
        return f"Code: {self.code}"

    class Meta:
        verbose_name = _("Discount Code")
        verbose_name_plural = _("Discount Codes")


# class DiscountUsedModel():
#     user = ""
#     disocunt = DiscountCode
#     used_time = ""
