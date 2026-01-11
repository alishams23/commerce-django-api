from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import User, SignUpVerifyCode, ContactUs, Notification, NotificationRead

from django.contrib.auth.admin import UserAdmin

# ============================
# User Admin
# ============================
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username", "first_name", "last_name", "phone_number",
        "verify_phone_number", "count_sms", "province", "city"
    )
    search_fields = ("username", "first_name", "last_name", "phone_number")
    list_filter = ("verify_phone_number", "province", "city", "is_staff", "is_superuser")
    readonly_fields = ("count_sms",)
    fieldsets = (
        (_("اطلاعات کاربری"), {
            "fields": ("username", "first_name", "last_name", "email", "password")
        }),
        (_("اطلاعات تماس"), {
            "fields": ("phone_number", "verify_phone_number", "verify_phone_code", "receiver_phone_number")
        }),
        (_("آدرس"), {
            "fields": ("province", "city", "address", "zip_code")
        }),
        (_("تصویر پروفایل"), {
            "fields": ("profile_image",)
        }),
        (_("دسترسی‌ها"), {
            "fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")
        }),
    )


# ============================
# SignUpVerifyCode Admin
# ============================
@admin.register(SignUpVerifyCode)
class SignUpVerifyCodeAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "verify_phone_number", "count_sms", "created_at", "updated_at")
    search_fields = ("phone_number",)
    list_filter = ("verify_phone_number", "created_at")
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')


# ============================
# ContactUs Admin
# ============================
@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone_number", "email", "is_called", "created_at")
    search_fields = ("first_name", "last_name", "phone_number", "email")
    list_editable = ("is_called",)
    list_filter = ("is_called", "created_at")
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')
    fieldsets = (
        (_("اطلاعات کاربر"), {"fields": ("created_by", "first_name", "last_name", "phone_number", "email")}),
        (_("توضیحات"), {"fields": ("description",)}),
        (_("وضعیت تماس"), {"fields": ("is_called",)}),
        (_("تاریخ‌ها"), {"fields": ("created_at", "updated_at")}),
        (("Deleted"),{"fields":("is_deleted","deleted_at")})
    )


# ============================
# NotificationRead Inline
# ============================
class NotificationReadInline(admin.TabularInline):
    model = NotificationRead
    extra = 1
    readonly_fields = ('is_read',"read_at",'created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')
    fields = ("user", "is_read", "read_at", "created_at", "updated_at")
    can_delete = True

    def is_read(self, obj):
        return obj.is_read
    is_read.boolean = True
    is_read.short_description = _("خوانده شده")


# ============================
# Notification Admin
# ============================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_at", "created_at")
    search_fields = ("title", "text")
    list_filter = ("is_published", "published_at", "created_at")
    readonly_fields = ('published_at','created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')
    fieldsets = (
        (_("محتوا"), {"fields": ("title", "text")}),
        (_("وضعیت انتشار"), {"fields": ("is_published", "published_at")}),
        (_("تاریخ‌ها"), {"fields": ("created_at", "updated_at")}),
    )
    inlines = [NotificationReadInline]  # استفاده از Inline برای users


# ============================
# Custom Filter is_read
# ============================
from django.contrib.admin import SimpleListFilter

class IsReadFilter(SimpleListFilter):
    title = _("خوانده شده")
    parameter_name = "is_read"

    def lookups(self, request, model_admin):
        return (
            ("read", _("خوانده شده")),
            ("unread", _("خوانده نشده")),
        )

    def queryset(self, request, queryset):
        if self.value() == "read":
            return queryset.filter(read_at__isnull=False)
        elif self.value() == "unread":
            return queryset.filter(read_at__isnull=True)
        return queryset


# ============================
# NotificationRead Admin
# ============================
@admin.register(NotificationRead)
class NotificationReadAdmin(admin.ModelAdmin):
    list_display = ("user", "notification","is_read","read_at", "created_at")
    search_fields = ("user__username", "notification__title")
    list_filter = (IsReadFilter, "read_at", "created_at") 
    readonly_fields = ('is_read','read_at','created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')
    fieldsets = (
        (_("کاربر و اعلان"), {"fields": ("user", "notification")}),
        (_("وضعیت"), {"fields": ("is_read", "read_at")}),
        (_("تاریخ‌ها"), {"fields": ("created_at", "updated_at")}),
    )

    def is_read(self, obj):
        return obj.is_read
    is_read.boolean = True
    is_read.short_description = _("خوانده شده")
