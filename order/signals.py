

from django.dispatch import receiver

from order.models import Order

from django.db.models.signals import pre_save



from django.db import transaction

from django.db.models import F

from product.models import ProductColor


@receiver(pre_save, sender=Order)
def restore_stock_on_cancel(sender, instance, **kwargs):
    
    if not instance.pk:
        return

    previous_status = (
        sender.objects.filter(pk=instance.pk)
        .values_list("status", flat=True)
        .first()
    )

    if previous_status == "cancelled":
        return

    if instance.status != "cancelled":
        return

    with transaction.atomic():
        for item in instance.items.all():

            if not item.product_color_id:
                continue

            ProductColor.objects.filter(
                pk=item.product_color_id
            ).update(
                stock=F("stock") + item.product_count
            )
