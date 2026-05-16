import os
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel
from user.models import User
from django_ckeditor_5 import fields as ckeditor_fields
from django.utils.translation import gettext_lazy as _

# Create your models here.


class CategoryBlog(AuditableModel, SoftDeleteModel):
    name = models.CharField(
        max_length=50, unique=True, verbose_name=_("Blog Topic Name")
    )
    order = models.PositiveIntegerField(
        default=0, verbose_name=_("Display Order"), db_index=True
    )
    is_active = models.BooleanField(
        default=True, verbose_name=_("Active / Inactive"), db_index=True
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Blog Topic")
        verbose_name_plural = _("Blog Topics")
        ordering = ["-created_at"]


class Blog(AuditableModel, SoftDeleteModel):
    category = models.ForeignKey(
        CategoryBlog,
        on_delete=models.PROTECT,
        null=True,
        related_name="blogs",
        verbose_name=_("Blog Category"),
        db_index=True,
    )

    title = models.CharField(max_length=50, verbose_name=_("Blog Title"))

    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        blank=True,
        verbose_name=_("Blog Slug"),
    )

    text_body = ckeditor_fields.CKEditor5Field(verbose_name=_("Blog Content"))

    reading_time = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Reading Time (minutes)"),
        help_text=_("Estimated reading time for this blog post in minutes."),
    )

    cover = models.ImageField(
        null=True,
        upload_to="blog/images/cover/",
        verbose_name=_("Blog Cover Image"),
        help_text=_("Used for displaying the blog in blog lists."),
    )

    is_published = models.BooleanField(default=True, verbose_name=_("Published"))

    published_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Publish Date")
    )

    likes = models.ManyToManyField(
        User, blank=True, verbose_name=_("Likes"), related_name="liked_blogs"
    )

    def clean(self):
        if not self.created_by:
            raise ValidationError(_("created_by is required"))

    def save(self, *args, **kwargs):
        self.clean()
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug

            counter = 1
            while Blog.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()

        minutes = len(self.text_body.split()) // 200
        self.reading_time = minutes if minutes > 1 else 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.title}"

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
        ordering = ["-published_at", "-created_at"]


class BlogMedia(AuditableModel, SoftDeleteModel):
    MEDIA_TYPE_CHOICES = [
        ("image", _("Image")),
        ("video", _("Video")),
    ]

    blog = models.OneToOneField(
        Blog,
        on_delete=models.CASCADE,
        related_name="media_items",
        verbose_name=_("Blog"),
    )

    media = models.FileField(
        upload_to="blog/",
        null=True,
        verbose_name=_("Media File"),
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp",
                    "mov",
                    "avi",
                    "mp4",
                    "webm",
                    "mkv",
                ]
            )
        ],
        help_text=_(
            "For each blog you must choose only one media type (image or video)."
        ),
    )

    media_type = models.CharField(
        max_length=5,
        choices=MEDIA_TYPE_CHOICES,
        verbose_name=_("Media Type"),
        null=True,
    )

    def __str__(self):
        return f"{self.blog.title}"

    def save(self, *args, **kwargs):

        extension = os.path.basename(self.media.name).split(".")[-1].lower()

        if extension in ["jpg", "jpeg", "png", "webp"]:
            self.media_type = "image"

        elif extension in ["mov", "avi", "mp4", "webm", "mkv"]:
            self.media_type = "video"

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Blog Media")
        verbose_name_plural = _("Blog Media Items")
        ordering = ["created_at"]


class BlogCommentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_approved=True)


class BlogComment(AuditableModel, SoftDeleteModel):
    blog = models.ForeignKey(
        Blog, on_delete=models.CASCADE, related_name="comments", verbose_name=_("Blog")
    )

    text = models.TextField(verbose_name=_("Comment Text"))

    reply = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="replies",
        verbose_name=_("Reply To"),
    )

    is_approved = models.BooleanField(default=True, verbose_name=_("Approved"))
    objects = BlogCommentManager()

    all_objects = models.Manager()

    def __str__(self):
        return f"{self.blog.title}"

    class Meta:
        verbose_name = _("Blog Comment")
        verbose_name_plural = _("Blog Comments")
