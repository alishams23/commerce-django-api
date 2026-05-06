from django.db import models
from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel
from helpdesk.utils import generate_ticket_number
from user.models import User
from django.utils.translation import gettext_lazy as _
# Create your models here.


class Department(AuditableModel, SoftDeleteModel):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Name"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))

    def __str__(self):
        return self.name


class Ticket(AuditableModel, SoftDeleteModel):
    class Priority(models.IntegerChoices):
        LOW = 1, _("Low")
        MEDIUM = 2, _("Medium")
        HIGH = 3, _("High")

    class Status(models.IntegerChoices):
        OPEN = 1, _("Open")
        CLOSED =0, _("Closed")

    # user = created_by

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="assigned_tickets",
        null=True,
        blank=True,
        verbose_name=_("Assigned to"),
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="tickets",
        verbose_name=_("Department"),
    )

    title = models.CharField(max_length=255, verbose_name=_("Title"))

    ticket_number = models.PositiveIntegerField(
        blank = True,
        null = True,
        unique=True,
        editable=False,
        db_index=True,
    )

    reference_code = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("Reference code"),
    )

    priority = models.SmallIntegerField(
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True,
        verbose_name=_("Priority"),
    )
    status = models.SmallIntegerField(
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
        verbose_name=_("Status"),
    )

    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")
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
        return f"Ticket #{self.ticket_number}" if self.ticket_number else "New Ticket"


class TicketMessage(AuditableModel, SoftDeleteModel):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("Ticket"),
    )

    message = models.TextField(verbose_name=_("Message"))

    is_admin = models.BooleanField(
        default=False, db_index=True, verbose_name=_("Is admin")
    )

    class Meta:
        verbose_name = _("Ticket message")
        verbose_name_plural = _("Ticket messages")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["ticket", "created_at"]),
            models.Index(fields=["created_by", "created_at"]),
        ]

    def __str__(self):
        return f"Message #{self.pk} for Ticket #{self.ticket_id}"
