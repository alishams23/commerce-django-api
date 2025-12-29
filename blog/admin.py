from django.contrib import admin
from .models import Blog, BlogMedia, BlogComment


class BlogMediaInline(admin.TabularInline):
    model = BlogMedia
    extra = 1  
    fields = ('image', 'video', 'created_at')
    readonly_fields = ('created_at',)
    verbose_name = "رسانه"
    verbose_name_plural = "رسانه‌ها"


class BlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 1
    fields = ('created_by', 'text', 'is_approved', 'created_at')
    readonly_fields = ('created_at',)
    verbose_name = "نظر"
    verbose_name_plural = "نظرات"


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_by', 'is_published', 'published_at', 'created_at')
    list_filter = ('is_published', 'created_by', 'published_at')
    search_fields = ('title', 'created_by__username', 'text_body')
    readonly_fields = ('created_at', 'updated_at', 'published_at','deleted_at', 'created_by', 'updated_by')
    inlines = [BlogMediaInline, BlogCommentInline]
    ordering = ('-published_at', '-created_at')
    fieldsets = (
        (None, {
            'fields': ('created_by', 'title', 'text_body', 'is_published','is_deleted')
        }),
        ('زمان‌بندی', {
            'fields': ('published_at', 'created_at', 'updated_at')
        }),
    )


@admin.register(BlogMedia)
class BlogMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'blog', 'image', 'video', 'created_at')
    list_filter = ('blog',)
    search_fields = ('blog__title',)
    readonly_fields = ('created_at', 'updated_at','deleted_at', 'created_by', 'updated_by')


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'blog', 'created_by', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'blog', 'created_by')
    search_fields = ('text', 'created_by__username', 'blog__title')
    readonly_fields = ('created_at', 'updated_at','deleted_at', 'created_by', 'updated_by')
