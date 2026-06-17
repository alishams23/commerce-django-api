from django.contrib import admin


class HardDeleteAdmin(admin.ModelAdmin):

    actions = [
        "hard_delete_selected",
    ]

    @admin.action(description="حذف دائمی")
    def hard_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete_hard()

class AllObjectsAdmin(HardDeleteAdmin):

    def get_queryset(self, request):
        return self.model.all_objects.all()