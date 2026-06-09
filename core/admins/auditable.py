from core.admins.mixins import AllObjectsAdmin

class AuditableExcludeAdmin(AllObjectsAdmin):
    exclude = ('created_at', 'updated_at', 'created_by', 'updated_by','is_deleted')