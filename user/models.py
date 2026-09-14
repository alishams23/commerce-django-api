from datetime import timedelta

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser

from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel

# from order.models import DiscountCode
from product.models import Product

class User(AbstractUser,AuditableModel, SoftDeleteModel):
    phone_number = models.CharField(max_length=11, unique=True, verbose_name=("شماره تلفن"))
    verify_phone_number = models.BooleanField(default=False, verbose_name=("تایید شماره تلفن"))
    birthdate = models.DateField(null=True,blank=True,verbose_name=("تاریخ تولد"))
    profile_image = models.ImageField(blank=True, null=True, upload_to="user/image_profiles/", verbose_name=("عکس پروفایل"))
    province = models.CharField(max_length=20, blank=True, null=True, verbose_name=("استان"))
    city = models.CharField(max_length=30, blank=True, null=True, verbose_name=("شهر"))
    address = models.TextField(blank=True, null=True, verbose_name=("آدرس"))
    zip_code = models.CharField(max_length=10, blank=True, null=True, verbose_name=("کدپستی"))
    receiver_phone_number = models.CharField(max_length=11,verbose_name=("شماره تلفن دریافت"))
    interests = models.ManyToManyField(Product,blank = True,related_name = 'interested_users',verbose_name=("علاقه مندی ها"))

    def __str__(self):
        return f"کاربر {self.username} --- {self.first_name} {self.last_name}"

    class Meta:
        verbose_name = ("کاربر")
        verbose_name_plural = ("کاربران")


class RegistrationSession(AuditableModel, SoftDeleteModel):
    first_name = models.CharField(max_length=150, blank=True,verbose_name = ("نام"))
    last_name = models.CharField(max_length=150, blank=True,verbose_name = ("نام خانوادگی"))
    phone_number = models.CharField(max_length=11,unique = True,verbose_name=("شماره تلفن"))
    password_hash = models.CharField(verbose_name = ("رمز عبور"), max_length=128)
    birthdate = models.DateField(null=True,blank=True,verbose_name=("تاریخ تولد"))
    email = models.EmailField(verbose_name = ("ایمیل"), blank=True)

    def __str__(self):
        return f"تایید ثبت نام {self.phone_number}"

    class Meta:
        verbose_name = ("تایید ثبت نام")
        verbose_name_plural = ("صف تایید ثبت نام")

class OTPCodeModel(AuditableModel, SoftDeleteModel):
    PURPOSE_CHOICE = (("register","ثبت نام"),("reset_password","بازیابی رمز عبور"))

    phone_number = models.CharField(max_length=11, verbose_name=("شماره تلفن"))

    purpose = models.CharField(max_length=20,choices=PURPOSE_CHOICE,default = 'register',verbose_name = ("دلیل درخواست کد"))

    code_hash = models.CharField(max_length=128,verbose_name = ("کد ارسال شده"))

    attempts = models.PositiveSmallIntegerField(default=0,verbose_name = ("تعداد دفعات درخواست ارسال کد"))

    last_sent_at = models.DateTimeField(null=True, blank=True,verbose_name = ("تایم آخرین کد ارسال شده"))

    is_used = models.BooleanField(default=False,verbose_name = ("استفاده شده"))


    def otp_validation(self):
        
        if not self.last_sent_at:
            return False
        
        if self.is_used or self.attempts >= 5 or (timezone.now() > (self.last_sent_at + timedelta(minutes = 3))):
            return False
        
        return True

    class Meta:
        indexes = [
            models.Index(fields=["phone_number", "purpose","is_used"])
        ]
        constraints = [
            models.UniqueConstraint(fields = ['phone_number','purpose'],name = 'unique_phone_purpose')
        ]
        verbose_name = ("کد ارسال شده")
        verbose_name_plural = ("کد های ارسال شده")
        ordering = ("-last_sent_at",)


class ContactUs(AuditableModel, SoftDeleteModel):
    first_name = models.CharField(max_length=50, verbose_name=("نام"))
    last_name = models.CharField(max_length=50, verbose_name=("نام خانوادگی"))
    phone_number = models.CharField(max_length=11,unique = True,verbose_name=("شماره تلفن"))
    email = models.EmailField(blank=True, null=True,unique = True,verbose_name=("ایمیل"))
    description = models.TextField(verbose_name=("توضیحات"))
    is_called = models.BooleanField(default=False, verbose_name=("تماس گرفته شده"))

    def __str__(self):
        return f"درخواست تماس با ما {self.first_name} -- {self.last_name} -- {self.phone_number}"

    class Meta:
        verbose_name = ("درخواست تماس با ما")
        verbose_name_plural = ("درخواست های تماس با ما")


class Notification(AuditableModel, SoftDeleteModel):
    STATUS_CHOICE = (("discount_code","کدتخفیف"),)
    subject = models.CharField(choices = STATUS_CHOICE,max_length = 30,blank = True,null = True,verbose_name = "موضوع اعلان")
    title = models.CharField(max_length=75, verbose_name=("عنوان"))
    text = models.TextField(verbose_name=("متن"))
    discount_code = models.ForeignKey("order.DiscountCode",on_delete = models.SET_NULL,null = True,blank = True,verbose_name = "کد تخفیف",related_name = "+")
    is_published = models.BooleanField(default=False, verbose_name=("منتشر شده"))
    published_at = models.DateTimeField(blank=True, null=True, verbose_name=("تاریخ انتشار"))

    def save(self, *args, **kwargs):
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = ("اعلان")
        verbose_name_plural = ("اعلان ها")
        ordering = ("-created_at",)


class NotificationRead(AuditableModel, SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_reads", verbose_name=("کاربر"))
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="user_statuses", verbose_name=("اعلان"))
    read_at = models.DateTimeField(blank=True, null=True, verbose_name=("تایم خواندن اعلان"))


    def save(self, *args, **kwargs):
        if self.read_at is None and getattr(self, "is_read", False):
            self.read_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_read(self):
        return self.read_at is not None

    def __str__(self):
        return f"{self.user} - {self.notification}"

    class Meta:
        verbose_name = ("وضعیت دیدن اعلان توسط کاربر")
        verbose_name_plural = ("وضعیت خوانده شدن اعلان ها توسط کاربران")
        unique_together = ("user", "notification")
