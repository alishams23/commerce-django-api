from django.db import models
from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel
from helpdesk.utils import generate_ticket_number
from user.models import User
# Create your models here.


class Department(AuditableModel, SoftDeleteModel):
    name = models.CharField(max_length=100, unique=True, verbose_name=("نام دپارتمان"))
    is_active = models.BooleanField(default=True, verbose_name=("فعال/غیرفعال"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = ("دپارتمان")
        verbose_name_plural = ("دپارتمان ها")


class Ticket(AuditableModel, SoftDeleteModel):
    class Priority(models.IntegerChoices):
        LOW = 1, ("کم")
        MEDIUM = 2, ("متوسط")
        HIGH = 3, ("زیاد")

    class Status(models.IntegerChoices):
        OPEN = 1, ("باز")
        CLOSED =0, ("بسته")

    # user = created_by

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="assigned_tickets",
        null=True,
        blank=True,
        verbose_name=("ارجاع داده شده به"),
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="tickets",
        verbose_name=("دپارتمان"),
    )

    title = models.CharField(max_length=255, verbose_name=("عنوان"))

    ticket_number = models.PositiveIntegerField(
        blank = True,
        null = True,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name=("شماره تیکت"),
    )

    reference_code = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=("رفرنس کد"),
    )

    priority = models.SmallIntegerField(
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True,
        verbose_name=("اولویت"),
    )
    status = models.SmallIntegerField(
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
        verbose_name=("وضعیت"),
    )

    class Meta:
        verbose_name = ("تیکت")
        verbose_name_plural = ("تیکت ها")
        ordering = ["-status","priority","-created_at"]
        indexes = [
            models.Index(fields=["created_by", "status"]),
            models.Index(fields=["department", "status"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["-created_at"]),
        ]

    def save(self, *args, **kwargs):
        creating = self.pk is None
            
        super().save(*args, **kwargs)

        if creating and not self.ticket_number:
            self.ticket_number = generate_ticket_number(self.pk, self.created_at)
            return super().save(update_fields=["ticket_number"])

        

    def __str__(self):
        return f"تیکت #{self.ticket_number}" if self.ticket_number else "تیکت جدید"


class TicketMessage(AuditableModel, SoftDeleteModel):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=("تیکت"),
    )

    message = models.TextField(verbose_name=("پیام"))

    is_admin = models.BooleanField(
        default=False, db_index=True, verbose_name=("ارسال شده توسط ادمین")
    )

    class Meta:
        verbose_name = "پیام تیکت"
        verbose_name_plural = "پیام‌های تیکت"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["ticket", "created_at"]),
            models.Index(fields=["created_by", "created_at"]),
        ]

    def __str__(self):
        return f"پیام #{self.pk} برای تیکت #{self.ticket_id}"
