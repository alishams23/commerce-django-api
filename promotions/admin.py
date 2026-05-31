from django.contrib import admin

from .models import Banner, Campaign, Gallery


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'position','order','is_active', 'created_at')
    list_editable = ('is_active','position','order')
    list_filter = ('position', 'is_active')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'is_active','is_valid')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('title',)
    filter_horizontal = ('products',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')
# ------------------- Gallery -------------------

@admin.register(Gallery)

class GalleryAdmin(admin.ModelAdmin):
    list_display = ('image','order','created_at', 'updated_at','is_deleted')
    list_editable = ('order','is_deleted')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')