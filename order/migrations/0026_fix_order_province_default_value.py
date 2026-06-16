from django.db import migrations


def set_default_province(apps, schema_editor):
    Order = apps.get_model("order", "Order")

    Order.objects.filter(province__isnull=True).update(
        province="yazd"
    )

    Order.objects.filter(province="").update(
        province="yazd"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0025_alter_delivery_inter_province_cost_and_more"),
    ]

    operations = [
        migrations.RunPython(set_default_province),
    ]