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
    created_by = models.OneToOneField(
        User,
        on_delete=models.CASCADE,#Rewrote for this
        null=True,
        blank=True,
        related_name="created_%(class)s_set"
    )
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
            
        if self.discount_code and self.discount_code.included_type == 'cart':
            return self.discount_code.apply_discount(amount = item_discount)    
        
            
        return item_discount

    @property
    def final_price(self):
        return self.discounted_price + (self.delivery_type.cost if self.delivery_type else 0)
    
    
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
    
    discounted =  models.PositiveIntegerField(default = 0)
    
    @property
    def total_price(self):
        return self.count * self.product_color.price


    @property
    def discounted_price(self):
        return self.count * self.product_color.discounted_price if self.discounted == 0 else self.discounted

    def discount_calculate(self):
        if self.cart.discount_code.included_type == 'product':
            self.discounted = self.cart.discount_code.apply_discount(amount = self.discounted_price)
            self.save()
            return True

        return False
    
    
    def __str__(self):
        return f"آیتم {self.cart}"

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم های سبد های خرید"
        unique_together = ("cart", "product_color")
        ordering = ("created_at",)


class Order(AuditableModel, SoftDeleteModel):
    STATUS_CHOICE = (
        ("pending_pay", "در انتظار پرداخت"),
        ("doing", "در حال آماده سازی"),# Paid!
        ("send", "ارسال شده"),
        ("completing", "تکمیل شده"),
        ("canceled", "لغو شده"),
    )
    # user/author = created_by

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default="pending_pay",
        verbose_name="وضعیت سفارش",
    )
    
    number = models.CharField(max_length=20,unique=True, verbose_name='شماره سفارش')
    
    tracking_code = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="کد رهیگیری ارسال"
    )
    send_date = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ ارسال")
    
    transaction_code = models.CharField(max_length=255, null=False, blank=False,verbose_name='کد تراكنش')

    description = models.TextField(blank=True, null=True, verbose_name="توضیحات سفارش")

    first_name = models.CharField(max_length=50,blank=True, null=True, verbose_name = "نام")
    last_name = models.CharField(max_length=50,blank=True, null=True, verbose_name = "نام خانوادگی")
    phone_number = models.CharField(max_length=11,blank=True, null=True,verbose_name= "شماره تلفن")
    email = models.EmailField(blank=True, null=True,verbose_name= "ایمیل")
    
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

    def generate_number(self):
        with transaction.atomic():
            date_str = timezone.now().strftime('%Y%m%d')
            last_order = Order.objects.select_for_update().filter(number__startswith=date_str).order_by('number').last()
            
            if last_order:
                last_num = int(last_order.number.split('-')[1]) + 1
            else:
                last_num = 1
            return f"{date_str}-{last_num:03d}"

    def __str__(self):
        return f"سفارش  {self.number}"

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"


class OrderItem(AuditableModel, SoftDeleteModel):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="سفارش"
    )
    product_name = models.CharField(max_length=100, verbose_name="نام محصول")
    color_name = models.CharField(max_length=50,blank = True,null = True,verbose_name="نام رنگ")
    color_code = ColorField(default = "#ffffff" ,verbose_name="کد رنگ (HEX)")
    product_price = models.PositiveBigIntegerField(default = 0,
        verbose_name="قیمت پایه محصول", db_index=True
    )
    product_count = models.PositiveIntegerField(default = 0,verbose_name="تعداد محصول")
    total_price = models.PositiveBigIntegerField(default = 0,verbose_name="جمع جزء(تومان)")


    def calculate_total_price(self):
        return self.product_count * self.product_price

    def __str__(self):
        return f"آیتم سفارش  {self.order.number}"

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم های سفارشات"


def default_expired_at():
    return timezone.now() + timedelta(days=2)

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
        default = default_expired_at,
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
    

    def apply_discount(self,amount:float):        
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
        verbose_name = "کدتخفیف"
        verbose_name_plural = "کدهای تخفیف"


# class DiscountUsedModel():
#     user = ""
#     disocunt = DiscountCode
#     used_time = ""