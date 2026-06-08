# from celery import shared_task
from celery import shared_task
from django.db import transaction

from order.models import Cart, Order, OrderItem
from user.models import User


# @shared_task
def create_order(validated_data, user_id, tracking_code):
    with transaction.atomic():
        user = User.objects.get(id=user_id)
        order = Order.objects.create(
            created_by=user,
            phone_number=user.phone_number,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data.get("email"),
            is_different_address=validated_data["is_different_address"],
            province=validated_data["province"],
            city=validated_data["city"],
            address=validated_data["address"],
            zip_code=validated_data["zip_code"],
            description=validated_data.get("description"),
            transaction_code=tracking_code,
        )
        user_cart = user.created_cart_set
        discount_code = user_cart.discount_code

        if discount_code:
            order.discount_code = discount_code.code
            order.discount_amount = discount_code.amount
            order.discount_type = "percent" if discount_code.is_percentage else "amount"
            order.discount_scope = (
                "cart" if discount_code.included_type == "cart" else "product"
            )

        for cart_item in user_cart.items.all().select_related("product_color"):
            product_color = cart_item.product_color
            order_item = OrderItem.objects.create(
                order=order,
                product_color_id=product_color.id,
                product_name=product_color.product.name,
                color_code=product_color.color.code,
                color_name=product_color.color.name,
                product_price=product_color.price,
                product_count=cart_item.count,
            )


            order_item.unit_discount_amount = (product_color.price * product_color.discount_percentage) // 100
            order_item.total_discount_amount = (cart_item.total_price - cart_item.base_discounted)
            
            order_item.coupon_discount_amount = (cart_item.base_discounted - cart_item.discounted_price)

            product_color.stock -= cart_item.count
            product_color.save()
            order_item.total_price = cart_item.total_price
            order_item.final_price = cart_item.discounted_price
            order_item.save()

        order.total_price = user_cart.total_price
        order.discount_price = user_cart.total_price - user_cart.discounted_price
        order.delivery_price = (
            user_cart.delivery_type.cost if user_cart.delivery_type else 0
        )
        order.final_price = user_cart.final_price
        order.number = order.generate_number()
        order.save()
        completing_order.apply_async(args=[user_cart.id, tracking_code], countdown=600)


@shared_task
def completing_order(cart_id, tracking_code):
    order = Order.objects.get(transaction_code=tracking_code)
    if order.status == "paid":
        with transaction.atomic():
            user_cart = Cart.objects.select_for_update().get(id=cart_id)
            discount_code = user_cart.discount_code

            if discount_code:
                discount_code.increment_usage()

            for cart_item in user_cart.items.all():
                cart_item.delete_hard()

            order.status = "pending_review"
            order.save()

    elif order.status == "pending_pay":
        order.status = "cancelled"
        order.cancel_reason = "payment_timeout"
        order.save()
