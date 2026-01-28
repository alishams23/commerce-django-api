from django.db import models

from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel
from product.models import Product, ProductColor

from colorfield.fields import ColorField

from datetime import timedelta

from django.utils import timezone

from .utils import generate_discount_code


# Create your models here.


class Delivery(AuditableModel, SoftDeleteModel):
    name = models.CharField(
        max_length=75,
        unique=True,
        verbose_name="نوع ارسال",
        help_text="...به عنوان مثال: پست ، تیپاکس و",
    )
    cost = models.PositiveBigIntegerField(verbose_name="هزینه ارسال(تومان)")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    def __str__(self):
        return f"نوع حمل و نقل {self.name} - {self.cost}"

    class Meta:
        verbose_name = "نوع حمل و نقل"
        verbose_name_plural = "انواع حمل و نقل"


class Cart(AuditableModel, SoftDeleteModel):
    STATUS_CHOICE = (
        ("pending_pay", "در انتظار پرداخت"),
        ("pay", "پرداخت شده"),
        ("pay_error", "خطا در حین پرداخت"),
    )
    # user/author = created_by
    discount_code = models.ForeignKey(
        "DiscountCode",
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
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default="pending_pay",
        verbose_name="وضعیت پرداخت سبد خرید",
    )

    @property
    def total_price(self,discount_price:int = 0):
        total_price = 0
        for item in self.items.all():
            total_price += item.total_price
        return total_price - discount_price

    def __str__(self):
        return (
            f"{self.created_by.phone_number} سبد خرید کاربر "
        )

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
    count = models.PositiveIntegerField(default = 1, verbose_name="تعداد")

    @property
    def total_price(self):
        return self.count * self.product_color.price

    def __str__(self):
        return f"آیتم {self.cart}"

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم های سبد های خرید"
        unique_together = ("cart", "product_color")


class Order(AuditableModel, SoftDeleteModel):
    STATUS_CHOICE = (
        ("doing", "در حال آماده سازی"),
        ("send", "ارسال شده"),
        ("canceled", "لغو شده"),
    )
    # user/author = created_by

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default="doing",
        verbose_name="وضعیت سفارش",
    )
    tracking_code = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="کد رهیگیری ارسال"
    )
    send_date = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ ارسال")

    description = models.TextField(blank=True, null=True, verbose_name="توضیحات سفارش")

    is_different_address = models.BooleanField(
        default=False, verbose_name="آدرس متفاوت"
    )
    province = models.CharField(blank = True,null = True,max_length=20, verbose_name="استان")
    city = models.CharField(blank = True,null = True,max_length=30, verbose_name="شهر")
    address = models.TextField(blank = True,null = True,verbose_name="آدرس")
    zip_code = models.CharField(blank = True,null = True,max_length=10, verbose_name="کدپستی")

    total_price = models.PositiveBigIntegerField(default = 0,verbose_name="جمع مبلغ آیتم ها(تومان)")
    discount_price = models.PositiveBigIntegerField(
        default=0, verbose_name="مبلغ تخفیف(تومان)"
    )
    delivery_price = models.PositiveBigIntegerField(
        default=0, verbose_name="هزینه ارسال/حمل و نقل(تومان)"
    )
    final_price = models.PositiveBigIntegerField(default = 0,verbose_name="مبلغ نهایی(تومان)")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.total_price == 0:
            for item in self.items.all():
                self.total_price += item.total_price

    def __str__(self):
        return f"سفارش  {self.id}"

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"


class OrderItem(AuditableModel, SoftDeleteModel):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="سفارش"
    )
    product_name = models.CharField(max_length=100, verbose_name="نام محصول")
    color_code = ColorField(default = "#ffffff" ,verbose_name="کد رنگ (HEX)")
    product_price = models.PositiveBigIntegerField(default = 0,
        verbose_name="قیمت پایه محصول", db_index=True
    )
    product_count = models.PositiveIntegerField(default = 0,verbose_name="تعداد محصول")
    total_price = models.PositiveBigIntegerField(default = 0,verbose_name="جمع جزء(تومان)")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.total_price = self.product_count * self.product_price
        super().save(*args, **kwargs)

    def calculate_total_price(self):
        return self.product_count * self.product_price

    def __str__(self):
        return f"آیتم سفارش  {self.order.id}"

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم های سفارشات"


class DiscountCode(AuditableModel, SoftDeleteModel):
    
    TYPE_CHOICE = (("cart","سبدخرید"),("product","محصول/محصولات"))
    
    name = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="نام کدتخفیف"
    )
    code = models.CharField(max_length=20, unique=True,blank = True,db_index=True)
    
    included_type = models.CharField(max_length = 10,choices = TYPE_CHOICE,default = 'cart',verbose_name = "تخفیف شامل")
    
    amount = models.PositiveIntegerField(default = 0,verbose_name="مقدار تخفیف")
    is_percentage = models.BooleanField(
        default=True,
        verbose_name="درصد",
        help_text="!با غیرفعال کردن این گزینه مقدار تخفیف به تومان محاسبه میشود",
    )
    max_usage = models.PositiveIntegerField(
        default=0,
        verbose_name="حداکثر تعداد استفاده ",
        help_text="اگر تعداد حداکثر استفاده 0 باشد ،کد تا پایان زمان انقضاء حداکثر 1 بار برای تمامی کاربران قابل استفاده است! ولی اگر تعداد حداکثر بیشتر از 0 باشد تا پایان زمان انقضا کد وقتی تعداد دفعات استفاده برابر با تعداد حداکثر شداعتبار کد به پایان می رسد",
    )
    current_usage = models.PositiveIntegerField(
        default=0, verbose_name="تعداد دفعات استفاده شده"
    )
    expired_at = models.DateTimeField(
        default=timezone.now() + timedelta(days=2),
        verbose_name="زمان انقضا",
        help_text="!زمان انقضا به صورت پیش فرض دو روز بعد از زمان سیستم است",
    )
    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="discount_codes",
        verbose_name="محصولات شامل این کد تخفیف",
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
        if (self.max_usage != 0 and (self.current_usage == self.max_usage)) or timezone.now() > self.expired_at:
            return False
        return True
    
    def increment_usage(self):
        self.current_usage += 1
        self.save()


    def apply_discount(self, product:Product = None, amount:float = None):
        """_summary_
        args:
            amount: For Product With diffrent Color if color price diffrent fixed_price # checkd
        """
    
        if not self.code_validation():
            return {"Error": "Discount Code is invalid! "}
        
        if amount is None and product is None:
            return {"Error": "Amount Or Product Requirement!"}
        
        if self.included_type == 'product':
            if not self.products.filter(id=product.id).exists():
                return {"Error": "This Product not included this Discount Code!"}
            
        if amount is None and product is not None:
            print("amount  = fixed price")
            amount = product.fixed_price
        

        if self.is_percentage:
            self.increment_usage()
            return amount - amount * (self.amount / 100)
            
        self.increment_usage()
        return amount - self.amount

    
    def __str__(self):
        return f"Code: {self.code}"
    
    class Meta:
        verbose_name = "کدتخفیف"
        verbose_name_plural = "کدهای تخفیف"
