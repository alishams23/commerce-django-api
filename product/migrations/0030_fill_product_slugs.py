# products/migrations/0002_fill_product_slugs.py
from django.db import migrations
from django.utils.text import slugify

def fill_product_slugs(apps, schema_editor):
    Product = apps.get_model('product', 'Product')
    for product in Product.objects.all():
        if not product.slug:
            base_slug = slugify(product.name, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            product.slug = slug
            product.save()

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0029_product_slug'), 
    ]

    operations = [
        migrations.RunPython(fill_product_slugs),
    ]