from django.contrib import admin

from core.admins.mixins import AllObjectsAdmin
from .models import Blog, BlogMedia, BlogComment, CategoryBlog


class BlogMediaInline(admin.TabularInline):
    model = BlogMedia
    extra = 1  
    fields = ('media','media_type')
    readonly_fields = ('media_type',)
    verbose_name = "رسانه"
    verbose_name_plural = "رسانه‌ها"


class BlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 1
    fields = ('created_by', 'text', 'is_approved', 'created_at')
    readonly_fields = ('created_at',)
    verbose_name = "نظر"
    verbose_name_plural = "نظرات"

@admin.register(CategoryBlog)
class CategoryBlogAdmin(AllObjectsAdmin):
    list_display = ('name', 'order', 'created_at', 'updated_at','is_active','is_deleted')
    list_editable = ('order','is_active','is_deleted')
    search_fields = ('name',)
    ordering = ('order',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by')

@admin.register(Blog)
class BlogAdmin(AllObjectsAdmin):
    list_display = ('title','reading_time','created_by', 'is_published', 'published_at', 'created_at')
    list_filter = ('category','is_published', 'created_by', 'published_at')
    prepopulated_fields = {"slug":("title",)}
    search_fields = ('title', 'created_by__username', 'text_body')
    readonly_fields = ('reading_time','created_at', 'updated_at', 'published_at','deleted_at', 'updated_by')
    inlines = [BlogMediaInline]
    ordering = ('-published_at', '-created_at')
    fieldsets = (
        (None, {
            'fields': ('created_by','category','title','slug','text_body','cover','is_published','is_deleted','likes')
        }),
        ('زمان‌بندی', {
            'fields': ('published_at', 'created_at', 'updated_at')
        }),
    )


@admin.register(BlogMedia)
class BlogMediaAdmin(AllObjectsAdmin):
    list_display = ('blog','media_type', 'created_at')
    list_filter = ('blog',)
    search_fields = ('blog__title',)
    readonly_fields = ('media_type','created_at', 'updated_at','deleted_at', 'created_by', 'updated_by')


@admin.register(BlogComment)
class BlogCommentAdmin(AllObjectsAdmin):
    list_display = ('blog', 'created_by', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'blog', 'created_by')
    search_fields = ('text', 'created_by__username', 'blog__title')
    readonly_fields = ('created_at', 'updated_at','deleted_at', 'created_by', 'updated_by')

    def get_queryset(self, request):
        return BlogComment.all_objects.all()