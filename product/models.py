from datetime import timedelta
from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel
from .utils import generate_discount_code
from colorfield.fields import ColorField
# Create your models here.


class Category(AuditableModel, SoftDeleteModel):
    name = models.CharField(max_length=50, unique = True ,verbose_name="نام دسته بندی والد")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش دسته بندی",db_index=True)
    is_active = models.BooleanField(default=True, verbose_name="فعال/غیرفعال",db_index=True)

    def __str__(self):
        return f"دسته بندی والد - {self.name}"

    class Meta:
        verbose_name = "دسته بندی والد"
        verbose_name_plural = "دسته بندی های والد"


class CategoryChildren(AuditableModel, SoftDeleteModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="childrens",
        verbose_name="دسته بندی والد",
    )
    name = models.CharField(max_length=50,unique = True,verbose_name="نام دسته بندی فرزند")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش دسته بندی",db_index=True)
    icon = models.ImageField(
        upload_to="products/image/category-children/icon/",
        blank=True,
        null=True,
        verbose_name="کاور دسته بندی فرزند",
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال/غیرفعال",db_index=True)

    def __str__(self):
        return f"دسته بندی فرزند - {self.name}"

    class Meta:
        verbose_name = "دسته بندی فرزند"
        verbose_name_plural = "دسته بندی های فرزند"
        indexes = [
            models.Index(fields=["category", "is_active", "is_deleted"]),
        ]


class Brand(AuditableModel, SoftDeleteModel):
    name = models.CharField(max_length=50,unique = True,verbose_name="نام برند")

    def __str__(self):
        return f"برند {self.id} - {self.name}"

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها "

class Product(AuditableModel, SoftDeleteModel):
    category = models.ForeignKey(
        CategoryChildren,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="دسته بندی محصول",db_index=True
    )
    name = models.CharField(max_length=100, verbose_name="نام محصول")
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="products",
        verbose_name="برند محصول",
    )
    specifications = models.TextField(
        blank=True, null=True, verbose_name="مشخصات محصول"
    )
    description = models.TextField(
        blank=True, null=True, verbose_name="توضیحات/معرفی محصول"
    )
    fixed_price = models.PositiveBigIntegerField(
        default = 0,
        verbose_name="قیمت ثابت",
        help_text="!اگر قیمت ثابت محصول و یا تمام رنگ های آن 0 باشد محصول رایگان در نظر گرفته میشود",db_index=True
    )
    percentage = models.PositiveIntegerField(
        default=0, verbose_name="درصد تخفیف ویژه این محصول"
    )
    is_published = models.BooleanField(default=True, verbose_name="وضعیت انتشار محصول",db_index=True)
    is_favorite = models.BooleanField(default=False, verbose_name="وضعیت محبوبیت")

    def __str__(self):
        return f"محصول {self.id} - {self.name}"

    # TODO: Validation Save Similar ProductColor In Django Panel!

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات "
        unique_together = ('name','category')
        indexes = [
            models.Index(fields=["category", "is_published", "is_deleted"]),
            models.Index(fields=["fixed_price"]),
        ]

class Color(AuditableModel,SoftDeleteModel):
    name = models.CharField(max_length=50,unique = True,verbose_name="اسم رنگ")
    code = ColorField(default = '#ffffff',unique = True,verbose_name="کد رنگ (HEX)")

    def __str__(self):
        return f"رنگ  {self.id} - {self.name}"

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.lower()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "رنگ"
        verbose_name_plural = "رنگ ها "
        unique_together = ('name','code')

class ProductColor(AuditableModel, SoftDeleteModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="colors",verbose_name = "محصول",db_index=True)
    color = models.ForeignKey(Color,on_delete = models.PROTECT,related_name = "products",verbose_name = "رنگ",db_index=True)
    price = models.PositiveBigIntegerField(blank=True, null=True, verbose_name="قیمت این رنگ از محصول",help_text = ".اگر قیمتی برای این رنگ در نظر گرفته نشود، پیش فرض قیمت پایه محصول روی این رنگ اعمال می شود")
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی این رنگ از محصول")

    
    
    
    def __str__(self):
        return f"رنگ محصول {self.product} - {self.color}"

    def save(self, *args, **kwargs):
        if self.price is None:
            self.price = self.product.fixed_price
        super().save(*args, **kwargs)
    # def save(self, *args, **kwargs):
    #     # TODO: Validation In Django Panel!
    #     if self.price:
    #         if not self.product.fixed_price or self.price < self.product.fixed_price:
    #             self.product.fixed_price = self.price
    #             self.product.save()

    #     if (
    #         self.product.is_published
    #         and not self.product.fixed_price
    #         and not self.product.colors.exclude(price__isnull=True).exists()
    #     ):
    #         raise ValidationError(
    #             "محصول منتشر شده باید قیمت ثابتی داشته باشد یا حداقل یک رنگ دارای قیمت باشد."
    #         )

    #     super().save(*args, **kwargs)

    class Meta:
        verbose_name = "رنگ محصول"
        verbose_name_plural = "رنگ بندی محصولات"
        unique_together = ('product','color')

class ProductImage(AuditableModel, SoftDeleteModel):
    product_color = models.ForeignKey(
        ProductColor,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="عکس مختص رنگ محصول",db_index=True
    )
    image = models.ImageField(upload_to="products/image/product-color/")  # def upload
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش عکس",db_index=True)
    is_cover = models.BooleanField(
        default=False,
        verbose_name="عکس کاور",
        help_text="انتخاب این عکس به عنوان عکس پیش نمایش محصول داخل لیست محصولات",db_index=True
    )

    def __str__(self):
        return f"عکس محصول {self.product_color}"

    class Meta:
        verbose_name = "عکس محصول"
        verbose_name_plural = "عکس های محصولات"


class ProductComment(AuditableModel, SoftDeleteModel):
    # User = created_by
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="comments", verbose_name="محصول",db_index=True
    )
    text = models.TextField(verbose_name="متن نظر")
    reply = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="replies",
        verbose_name="در جواب نظر",
    )
    is_approved = models.BooleanField(default=True, verbose_name="وضعیت تایید نظر",db_index=True)

    def __str__(self):
        return f"نظر محصول {self.created_by.username} - {self.product.name}"

    class Meta:
        verbose_name = "نظر محصول"
        verbose_name_plural = "نظرات محصولات"


class DiscountCode(AuditableModel, SoftDeleteModel):
    name = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="نام کدتخفیف"
    )
    code = models.CharField(max_length=20, unique=True, db_index=True)
    amount = models.PositiveIntegerField(verbose_name="مقدار تخفیف")
    is_percentage = models.BooleanField(
        default=True,
        verbose_name="درصد",
        help_text="با غیرفعال کردن این گزینه مقدار تخفیف به تومان/ریال محاسبه میشود!",
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
        help_text="زمان انقضا به صورت پیش فرض دو روز بعد از زمان سیستم است!",
    )
    is_all_products = models.BooleanField(
        default=False,
        verbose_name="تمام محصولات",
        help_text="با فعال کردن این گزینه، کدتخفیف شامل تمامی محصولات سایت میشود!",
    )
    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="discount_codes",
        verbose_name="محصولات شامل این کد تخفیف",
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            while True:
                code = generate_discount_code()
                if not self.__class__.objects.filter(code=code).exists():
                    self.code = code
                    break
        super().save(*args, **kwargs)

    def discount_validation(self):
        if (
            self.max_usage != 0 and (self.current_usage == self.max_usage)
        ) or timezone.now() > self.expired_at:
            return False

    def apply_dicount(self, product: Product, amount=None):
        """_summary_
        args:
            amount: For Product With diffrent Color if color price diffrent fixed_price # checkd
        """

        if amount is None:
            amount = product.fixed_price

        if not self.discount_validation():
            return {"Error": "Discount Code! is invalid! "}
        if (
            not self.is_all_products
            and not self.products.filter(id=product.id).exists()
        ):
            return {"Error": "This Product not included this Discount Code!"}

        if self.is_percentage:
            return amount - (amount * self.amount / 100)

        return amount - self.amount

    def increment_usage(self):
        self.current_usage += 1
        self.save()

    class Meta:
        verbose_name = "کدتخفیف"
        verbose_name_plural = "کدهای تخفیف"



class Gallery(AuditableModel,SoftDeleteModel):
    image = models.ImageField(upload_to = "home/gallery/",verbose_name = "عکس")
    order = models.PositiveIntegerField(default = 0,verbose_name = "ترتیب نمایش عکس")
    is_published = models.BooleanField(default=True, verbose_name="وضعیت انتشار عکس",db_index=True)
    
    def __str__(self):
        return f"عکس گالری {self.id} - {self.image}"
    
    class Meta:
        verbose_name = "عکس گالری"
        verbose_name_plural = "گالری / عکس های گالری"
        ordering = ("order","-created_at")
        