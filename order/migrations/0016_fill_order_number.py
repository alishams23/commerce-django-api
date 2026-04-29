# products/migrations/0016_fill_order_numbers.py
from django.db import migrations, transaction
from django.utils import timezone


def fill_order_numbers_for_existing(apps, schema_editor):
    Order = apps.get_model("order", "Order")  # مطمئن شوید نام اپلیکیشن درست است

    with transaction.atomic():
        orders_to_process = Order.objects.filter(number__isnull=True).order_by("id")

        last_order_overall = (
            Order.objects.filter(number__isnull=False).order_by("number").last()
        )

        current_num = 1
        if last_order_overall:
            try:
                prefix, num_str = last_order_overall.number.split("-")

                if prefix == timezone.now().strftime("%Y%m%d"):
                    current_num = int(num_str) + 1
                else:
                    current_num = 1
            except (ValueError, IndexError):
                current_num = 1

        date_str = timezone.now().strftime("%Y%m%d")

        for order in orders_to_process:
            order.number = f"{date_str}-{current_num:03d}"
            order.save()
            current_num += 1


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0015_order_number_alter_order_status"),
    ]

    operations = [
        migrations.RunPython(
            fill_order_numbers_for_existing, reverse_code=migrations.RunPython.noop
        ),
    ]
