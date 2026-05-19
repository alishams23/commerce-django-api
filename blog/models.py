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
# Create your models here.

class CategoryBlog(AuditableModel, SoftDeleteModel):
    name = models.CharField(max_length=50, unique = True ,verbose_name="نام موضوع برند")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش ",db_index=True)
    is_active = models.BooleanField(default=True, verbose_name="فعال/غیرفعال",db_index=True)

    def __str__(self):
        return f"{self.name}"
    class Meta:
        verbose_name = "موضوع برند"
        verbose_name_plural = "موضوعات برند"
        ordering = ['-created_at']
    

class Blog(AuditableModel, SoftDeleteModel):
    category = models.ForeignKey(
        CategoryBlog,
        on_delete=models.PROTECT,
        null = True,
        related_name="blogs",
        verbose_name="موضوع بلاگ",db_index=True
    )
    title = models.CharField(max_length = 50 , verbose_name = "عنوان بلاگ")
    slug = models.SlugField(max_length=255, unique=True,allow_unicode=True,blank = True,verbose_name='اسلاگ محصول')
    text_body = ckeditor_fields.CKEditor5Field(verbose_name = "متن بلاگ")
    reading_time = models.PositiveIntegerField(default = 0,verbose_name = "زمان مطالعه بلاگ",help_text = "زمان تخمینی برای خواندن این پست وبلاگ به دقیقه.")
    cover = models.ImageField(null = True,upload_to = "blog/images/cover/",verbose_name = "کاور بلاگ",help_text = "برای نمایش داخل لیست بلاگ ها")
    is_published = models.BooleanField(default = True,verbose_name = "وضعیت انتشار")
    published_at = models.DateTimeField(blank = True,null = True,verbose_name = "تاریخ انتشار")
    likes = models.ManyToManyField(User,blank = True,verbose_name = 'لایک ها',related_name = "liked_blogs")

    def clean(self):
        if not self.created_by:
            raise ValidationError("created_by is required")

    def save(self,*args,**kwargs):
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

        super().save(*args,**kwargs)
    
    def __str__(self):
        return f"وبلاگ {self.id} - {self.title}"
    
    class Meta:
        verbose_name = "وبلاگ"
        verbose_name_plural = "وبلاگ ها"
        ordering = ['-published_at', '-created_at']
        
class BlogMedia(AuditableModel, SoftDeleteModel):
    MEDIA_TYPE_CHOICES = [
        ('image', ("عکس")),
        ('video', ("ویدئو")),
    ]
    blog = models.OneToOneField(Blog,on_delete = models.CASCADE,related_name = "media_items",verbose_name = "وبلاگ")
    media = models.FileField(upload_to="blog/",null=True,verbose_name = "رسانه",validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png','webp','mov','avi','mp4','webm','mkv'])],help_text = "برای هر بلاگ فقط یکی از این دو رسانه(عکس یا ویدئو) رو باید انتخاب کنید.") 
    media_type = models.CharField(max_length=5,choices=MEDIA_TYPE_CHOICES,verbose_name="نوع رسانه",null=True)

    def __str__(self):
        return f"رسانه {self.id} - {self.blog.title}"
    
    def save(self, *args, **kwargs):
        
        extension = os.path.basename(self.media.name).split('.')[-1].lower()

        if extension in ['jpg', 'jpeg', 'png','webp']:
            self.media_type = 'image'
            
        elif extension in ['mov','avi','mp4','webm','mkv']:
            self.media_type = 'video'
            
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "رسانه وبلاگ"
        verbose_name_plural = "رسانه های وبلاگ ها"
        ordering = ['created_at']

class BlogCommentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_approved = True)


class BlogComment(AuditableModel, SoftDeleteModel):
    blog = models.ForeignKey(Blog,on_delete = models.CASCADE,related_name = "comments",verbose_name = "وبلاگ")
    text = models.TextField(verbose_name = "متن نظر")
    reply = models.ForeignKey("self",on_delete = models.CASCADE,blank = True,null = True,related_name = "replies",verbose_name = "در جواب نظر")
    is_approved = models.BooleanField(default=True,verbose_name = "وضعیت تایید نظر")

    objects = BlogCommentManager() 
   
    all_objects = models.Manager()
    
    def __str__(self):
        return f"نظر وبلاگ {self.created_by} - {self.blog.title}"
    
    class Meta:
        verbose_name = "نظر وبلاگ"
        verbose_name_plural = "نظرات وبلاگ ها"