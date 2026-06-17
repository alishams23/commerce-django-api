from django.contrib import admin

from core.admins.mixins import AllObjectsAdmin
from .models import Department, Ticket, TicketMessage


@admin.register(Department)
class DepartmentAdmin(AllObjectsAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    readonly_fields = ('created_by', 'updated_by')

@admin.register(Ticket)
class TicketAdmin(AllObjectsAdmin):
    list_display = (
        "ticket_number",
        "title",
        "created_by",
        "department",
        "priority",
        "status",
        "assigned_to",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "priority", "department")
    search_fields = ("ticket_number","title", "description", "reference_code", "created_by__username")
    autocomplete_fields = ("created_by", "assigned_to", "department")
    readonly_fields = ('created_by', 'updated_by')
