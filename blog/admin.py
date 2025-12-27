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
    fields = ('user', 'text', 'is_approved', 'created_at')
    readonly_fields = ('created_at',)
    verbose_name = "نظر"
    verbose_name_plural = "نظرات"


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'is_published', 'published_at', 'created_at')
    list_filter = ('is_published', 'author', 'published_at')
    search_fields = ('title', 'author__username', 'text_body')
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    inlines = [BlogMediaInline, BlogCommentInline]
    ordering = ('-published_at', '-created_at')
    fieldsets = (
        (None, {
            'fields': ('author', 'title', 'text_body', 'is_published')
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
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'blog', 'user', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'blog', 'user')
    search_fields = ('text', 'user__username', 'blog__title')
    readonly_fields = ('created_at', 'updated_at')
