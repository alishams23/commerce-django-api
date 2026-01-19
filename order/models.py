from django.db import models

from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel
from product.models import DiscountCode, ProductColor

# Create your models here.


class Delivery(AuditableModel, SoftDeleteModel):
    name = models.CharField(
        max_length=75,
        unique = True,
        verbose_name="نوع ارسال",
        help_text="...به عنوان مثال: پست ، تیپاکس و",
    )
    price = models.PositiveBigIntegerField(verbose_name="هزینه ارسال(تومان)")
    is_active = models.BooleanField(default = True,verbose_name = "فعال")
    def __str__(self):
        return f"نوع حمل نقل {self.name} - {self.price}"
    
    class Meta:
        verbose_name = "نوع حمل و نقل"
        verbose_name_plural = "انوع حمل و نقل"

class Cart(AuditableModel, SoftDeleteModel):
    STATUS_CHOICE = (
        ("pending_pay", "در انتظار پرداخت"),
        ("pay", "پرداخت شده"),
        ("pay", "ارور خورده پرداخت نشده"),
    )
    # user/author = created_by
    discount_code = models.ForeignKey(
        DiscountCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_used",
        verbose_name="کد تخفیف",
    )
    delivery_type = models.ForeignKey(
        Delivery,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="cart_used",
        verbose_name="نوع حمل و نقل",
    )
    total_price = models.PositiveBigIntegerField(verbose_name="جمع کل(تومان)")
    
    def __str__(self):
        return f'سبد خرید کاربر {self.created_by.username} (:وضعیت پرداخت {"پرداخت شده" if self.is_pay else "پرداخت نشده"})'
    
    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبد های خرید"

class CartItem(AuditableModel, SoftDeleteModel):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items", verbose_name="سبد خرید"
    )
    product_color = models.ForeignKey(
        ProductColor,
        on_delete=models.PROTECT,
        related_name="cart_items",
        verbose_name="محصول",
    )
    count = models.PositiveBigIntegerField(verbose_name="تعداد")
    total_price = models.PositiveBigIntegerField(verbose_name="جمع جزء(تومان)")
    
    def __str__(self):
        return f"آیتم {self.cart}"
    
    class Meta:
        verbose_name  =  "آیتم سبد خرید"
        verbose_name_plural  =  "آیتم های سبد های خرید"
        unique_together = ("cart", "product_color")


class CartDetail(AuditableModel, SoftDeleteModel):
    cart = models.OneToOneField(
        Cart, on_delete=models.CASCADE, related_name="detail", verbose_name="سبد خرید"
    )
    first_name = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="نام"
    )
    last_name = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="نام خانوادگی"
    )
    province = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="استان"
    )
    city = models.CharField(max_length=30, blank=True, null=True, verbose_name="شهر")
    address = models.TextField(blank=True, null=True, verbose_name="آدرس")
    zip_code = models.CharField(
        max_length=10, blank=True, null=True, verbose_name="کدپستی"
    )
    phone_number = models.CharField(max_length=11, verbose_name="شماره تلفن")
    email = models.EmailField(blank=True, null=True, verbose_name="ایمیل")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات سفارش")
    deferent_address = models.BooleanField(default=False, verbose_name="آدرس متفاوت")
    
    def __str__(self):
        return f"اطلاعات {self.cart}"
    
    class Meta:
        verbose_name = "اطلاعات سبد خرید"
        verbose_name_plural = "اطلاعات سبد های خرید"

class Order(AuditableModel, SoftDeleteModel):
    STATUS_CHOICE = (
        ("pending_send", "آماده سازی جهت ارسال"),
        ("send", "ارسال شده"),
        ("done", "تحویل داده شده"),
        ("canceled", "لغو شده"),
    )
    # user/author = created_by
    cart = models.OneToOneField(
        Cart, on_delete=models.PROTECT, related_name="order", verbose_name="سبد خرید"
    )
    buy_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت سفارش")
    status = models.CharField(max_length = 20,choices = STATUS_CHOICE,default = "pending_send",verbose_name = 'وضعیت سفارش')
    send_date = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ ارسال")
    id_send = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="کد رهیگیری ارسال"
    )
        
    def __str__(self):
        return f"سفارش  {self.id}"
    
    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"
