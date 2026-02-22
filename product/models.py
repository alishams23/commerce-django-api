from django.db import models
from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel
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
        related_name="children",
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
    show_in_menu = models.BooleanField(default = False,verbose_name = "نمایش در منو",help_text = ".با فعال کردن این گزینه دسته بندی در منوی دسته بندی صفحه اصلی سایت نمایش داده میشود")
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
        verbose_name="قیمت ثابت(تومان)",
        help_text="!اگر قیمت ثابت محصول و یا تمام رنگ های آن 0 باشد محصول رایگان در نظر گرفته میشود",db_index=True
    )

    discount_percentage  = models.PositiveIntegerField(
        default=0, verbose_name="درصد تخفیف ویژه این محصول"
    )
    is_published = models.BooleanField(default=True, verbose_name="وضعیت انتشار محصول",db_index=True)
    is_favorite = models.BooleanField(default=False, verbose_name="وضعیت محبوبیت")

    def __str__(self):
        return f"محصول {self.id} - {self.name}"


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
        return f"رنگ {self.name}"

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
    base_price = models.PositiveBigIntegerField(default = 0, verbose_name="(تومان)قیمت این رنگ از محصول",help_text = ".اگر قیمتی برای این رنگ در نظر گرفته نشود، پیش فرض قیمت پایه محصول روی این رنگ اعمال می شود")
    base_discount  = models.PositiveIntegerField(default = 0, verbose_name="درصد تخفیف ویژه این رنگ از محصول",help_text = ".اگر تخفیف ویژه برای این رنگ از محصول در نظر گرفته نشود، پیش فرض تخفیف ویژه پایه محصول روی این رنگ اعمال می شود")
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی این رنگ از محصول")


    @property
    def price(self):
        return self.base_price if self.base_price != 0 else self.product.fixed_price

    @property
    def discount_percentage(self):
        return self.base_discount if self.base_discount != 0 else self.product.discount_percentage
    
    @property
    def discounted_price(self):
        return self.price - (self.price * self.discount_percentage // 100)
    
    def __str__(self):
        return f"{self.product} - {self.color}"


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
        