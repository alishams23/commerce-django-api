from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel


class User(AbstractUser,AuditableModel, SoftDeleteModel):
    phone_number = models.CharField(max_length=11, unique=True, verbose_name=_("Phone Number"))
    verify_phone_number = models.BooleanField(default=False, verbose_name=_("Phone Verified"))
    verify_phone_code = models.CharField(max_length=6, blank=True, null=True, verbose_name=_("Verification Code"))
    count_sms = models.IntegerField(default=0, verbose_name=_("SMS Count"))
    profile_image = models.ImageField(blank=True, null=True, upload_to="user/image_profile/", verbose_name=_("Profile Image"))
    province = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Province"))
    city = models.CharField(max_length=30, blank=True, null=True, verbose_name=_("City"))
    address = models.TextField(blank=True, null=True, verbose_name=_("Address"))
    zip_code = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("ZIP Code"))
    receiver_phone_number = models.CharField(max_length=11, unique=True, verbose_name=_("Receiver Phone Number"))

    def __str__(self):
        return f"کاربر {self.username} --- {self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class SignUpVerifyCode(AuditableModel, SoftDeleteModel):
    phone_number = models.CharField(max_length=11, unique=True, verbose_name=_("Phone Number"))
    verify_phone_number = models.BooleanField(default=False, verbose_name=_("Phone Verified"))
    verify_phone_code = models.CharField(max_length=6, blank=True, null=True, verbose_name=_("Verification Code"))
    count_sms = models.IntegerField(default=0, verbose_name=_("SMS Count"))

    def __str__(self):
        return f"تایید ثبت نام {self.phone_number}"

    class Meta:
        verbose_name = _("Sign Up Verification")
        verbose_name_plural = _("Sign Up Verification Queue")


class ContactUs(AuditableModel, SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="contact_us_requests", verbose_name=_("User"))
    first_name = models.CharField(max_length=50, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=50, verbose_name=_("Last Name"))
    phone_number = models.CharField(max_length=11, verbose_name=_("Phone Number"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email"))
    description = models.TextField(verbose_name=_("Description"))
    is_called = models.BooleanField(default=False, verbose_name=_("Called"))

    def __str__(self):
        return f"درخواست تماس با ما {self.first_name} -- {self.last_name} -- {self.phone_number}"

    class Meta:
        verbose_name = _("Contact Us Request")
        verbose_name_plural = _("Contact Us Requests")


class Notification(AuditableModel, SoftDeleteModel):
    title = models.CharField(max_length=75, verbose_name=_("Title"))
    text = models.TextField(verbose_name=_("Text"))
    users = models.ManyToManyField(User, through="NotificationRead",through_fields=("notification", "user"),related_name="notifications", verbose_name=_("Users"))
    is_published = models.BooleanField(default=False, verbose_name=_("Published"))
    published_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Published At"))

    def save(self, *args, **kwargs):
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")


class NotificationRead(AuditableModel, SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_reads", verbose_name=_("User"))
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="user_statuses", verbose_name=_("Notification"))
    read_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Read At"))


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
        verbose_name = _("User Notification Status")
        verbose_name_plural = _("User Notification Statuses")
        unique_together = ("user", "notification")
