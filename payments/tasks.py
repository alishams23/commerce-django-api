# from celery import shared_task
from django.db import transaction

from order.models import Cart, Order, OrderItem
from user.models import User


# @shared_task
def create_order(validated_data,user_id,tracking_code):
    with transaction.atomic():
        user = User.objects.get(id = user_id)
        order = Order.objects.create(
            created_by = user,
            phone_number = user.phone_number,
            first_name = validated_data["first_name"],
            last_name = validated_data["last_name"],
            email = validated_data.get("email"),
            is_different_address = validated_data["is_different_address"],
            province = validated_data["province"],
            city = validated_data["city"],
            address = validated_data["address"],
            zip_code = validated_data["zip_code"],
            description = validated_data.get("description"),
            transaction_code = tracking_code,
        )

        order.number = order.generate_number()
        order.save()


# @shared_task
def completing_order(cart_id, tracking_code):

    with transaction.atomic():
        user_cart = Cart.objects.select_for_update().get(id=cart_id)
        order = Order.objects.select_for_update().get(transaction_code=tracking_code)
        
        if order.final_price != 0:
            return
        
        order.total_price = user_cart.total_price
        order.discount_price = user_cart.total_price - user_cart.discounted_price
        order.delivery_price = (
            user_cart.delivery_type.cost if user_cart.delivery_type else 0
        )

        order.final_price = (
            order.total_price - order.discount_price + order.delivery_price
        )

        for cart_item in user_cart.items.all().select_related("product_color"):
            product_color = cart_item.product_color
            order_item = OrderItem.objects.create(
                order=order,
                product_name=product_color.product.name,
                color_code=product_color.color.code,
                color_name=product_color.color.name,
                product_price=product_color.price,
                product_count=cart_item.count,
            )
            product_color.stock -= cart_item.count
            product_color.save()
            order_item.total_price = order_item.calculate_total_price()
            order_item.save()
            cart_item.delete_hard()
        
        if user_cart.discount_code:
            user_cart.discount_code.increment_usage()

        order.save()

# @shared_task
def delete_order(tracking_code):
    try:
        Order.objects.get(transaction_code=tracking_code).delete_hard()
    except Order.DoesNotExist:
        #log
        pass