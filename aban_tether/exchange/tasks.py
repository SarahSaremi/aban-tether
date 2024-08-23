from celery import shared_task
from django.db.models import Sum
from .models import Order
import requests
import uuid


@shared_task
def aggregate_and_buy_from_exchange():
    pending_orders = Order.objects.filter(status='PENDING')
    total_amount = pending_orders.aggregate(Sum('amount'))['amount__sum'] or 0

    if total_amount >= 10:
        print('total_amount', total_amount)
        batch_id = uuid.uuid4()
        orders_to_process = []

        current_sum = 0
        for order in pending_orders:
            print('order', order)
            if current_sum + order.amount > 10:
                break
            current_sum += order.amount
            orders_to_process.append(order)

        print('orders_to_process', orders_to_process)
        if orders_to_process:
            for order in orders_to_process:
                order.status = 'PROCESSED'
                order.batch_id = batch_id
                order.save()

            response = requests.post('https://foreign-exchange-system.com/api/buy', json={
                "batch_id": str(batch_id),
                "orders": [{"order_id": order.id, "amount": float(order.amount)} for order in orders_to_process]
            })

            print(response.status_code)
            if response.status_code == 200:
                Order.objects.filter(batch_id=batch_id).update(status='PROCESSED')
            else:
                Order.objects.filter(batch_id=batch_id).update(status='FAILED')
