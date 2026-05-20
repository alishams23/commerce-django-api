from django.contrib import admin

class AuditableExcludeAdmin(admin.ModelAdmin):
    exclude = ('created_at', 'updated_at', 'created_by', 'updated_by','is_deleted')