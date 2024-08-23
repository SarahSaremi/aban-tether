import random

from celery import shared_task
from django.db.models import Sum

from .enums import ORDER_STATUS_PENDING, EXCHANGE_THRESHOLD, ORDER_STATUS_PROCESSED, ORDER_STATUS_FAILED
from .models import Order
import uuid


def buy_from_exchange(orders):
    is_success = random.randint(0, 100)
    if is_success >= 4:
        return {'status_code': 200}
    else:
        return {'status_code': 500}


@shared_task
def aggregate_and_buy_from_exchange():
    pending_orders = Order.objects.filter(status=ORDER_STATUS_PENDING)
    total_price = pending_orders.aggregate(Sum('price'))['price__sum'] or 0

    if total_price >= EXCHANGE_THRESHOLD:
        print('total_amount', total_price)
        batch_id = uuid.uuid4()
        orders_to_process = []

        current_sum = 0
        for order in pending_orders:
            print('order', order)
            if current_sum + order.amount > EXCHANGE_THRESHOLD:
                break
            current_sum += order.amount
            orders_to_process.append(order)

        print('orders_to_process', orders_to_process)
        if orders_to_process:
            for order in orders_to_process:
                order.status = ORDER_STATUS_PROCESSED
                order.batch_id = batch_id
                order.save()

            response = buy_from_exchange(orders_to_process)
            if response['status_code'] == 200:
                Order.objects.filter(batch_id=batch_id).update(status=ORDER_STATUS_PROCESSED)
            else:
                Order.objects.filter(batch_id=batch_id).update(status=ORDER_STATUS_FAILED)
