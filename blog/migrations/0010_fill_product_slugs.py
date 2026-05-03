from django.db import migrations
from django.utils.text import slugify

def fill_blog_slugs(apps, schema_editor):
    Blog = apps.get_model('blog', 'Blog')
    for blog in Blog.objects.all():
        if not blog.slug:
            base_slug = slugify(blog.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Blog.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            blog.slug = slug
            blog.save()

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_blog_slug'), 
    ]

    operations = [
        migrations.RunPython(fill_blog_slugs),
    ]