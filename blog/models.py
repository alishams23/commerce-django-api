from django.db import models
from django.utils import timezone
from core.models.auditable import AuditableModel
from core.models.soft_delete import SoftDeleteModel

# Create your models here.


class Blog(AuditableModel, SoftDeleteModel):
    title = models.CharField(max_length = 50 , verbose_name = "عنوان بلاگ")
    text_body = models.TextField(blank = True, null = True ,verbose_name = "متن بلاگ")
    is_published = models.BooleanField(default = True,verbose_name = "وضعیت انتشار")
    published_at = models.DateTimeField(blank = True,null = True,verbose_name = "تاریخ انتشار")
    
    def save(self,*args,**kwargs):
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args,**kwargs)
    
    def __str__(self):
        return f"وبلاگ {self.id} - {self.title}"
    
    class Meta:
        verbose_name = "وبلاگ"
        verbose_name_plural = "وبلاگ ها"
        ordering = ['-published_at', '-created_at']
        
class BlogMedia(AuditableModel, SoftDeleteModel):
    blog = models.ForeignKey(Blog,on_delete = models.CASCADE,related_name = "media_items",verbose_name = "وبلاگ")
    image = models.ImageField(blank = True,null = True,upload_to = "blog/image/",verbose_name = "عکس")#blog title + date 
    video = models.FileField(blank = True,null = True,upload_to = "blog/videos/",verbose_name = "ویدئو")#blog title + date 

    def __str__(self):
        return f"رسانه {self.id} - {self.blog.title}"
    
    class Meta:
        verbose_name = "رسانه وبلاگ"
        verbose_name_plural = "رسانه های وبلاگ ها"
        ordering = ['created_at']
        
class BlogComment(AuditableModel, SoftDeleteModel):
    blog = models.ForeignKey(Blog,on_delete = models.CASCADE,related_name = "comments",verbose_name = "وبلاگ")
    text = models.TextField(verbose_name = "متن نظر")
    reply = models.ForeignKey("self",on_delete = models.CASCADE,blank = True,null = True,related_name = "replies",verbose_name = "در جواب نظر")
    is_approved = models.BooleanField(default=True,verbose_name = "وضعیت تایید نظر")

    def __str__(self):
        return f"نظر وبلاگ {self.user.username} - {self.blog.title}"
    
    class Meta:
        verbose_name = "نظر وبلاگ"
        verbose_name_plural = "نظرات وبلاگ ها"