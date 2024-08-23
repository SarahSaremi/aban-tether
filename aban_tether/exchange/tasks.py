import logging
import random

from celery import shared_task
from django.db import transaction

from .enums import ORDER_STATUS_PENDING, EXCHANGE_THRESHOLD, ORDER_STATUS_PROCESSED, ORDER_STATUS_FAILED, \
    ORDER_STATUS_PROCESSING
from .models import Order


logger = logging.getLogger(__name__)


def buy_from_exchange(orders):
    is_success = random.randint(0, 100)
    if is_success >= 4:
        return {'status_code': 200}
    else:
        return {'status_code': 500}


@shared_task
def aggregate_and_buy_from_exchange():
    pending_orders = Order.objects.filter(status=ORDER_STATUS_PENDING)

    if not pending_orders.exists():
        logger.info('No pending orders to process.')
        return

    total_amount = sum(order.price for order in pending_orders)

    if total_amount < EXCHANGE_THRESHOLD:
        logger.info(f'Total pending order amount ({total_amount}) is less than ${EXCHANGE_THRESHOLD}. Aggregation postponed.')
        return

    batch_id = Order.assign_batch_id(pending_orders)
    response = buy_from_exchange(pending_orders)

    if response['status_code'] != 200:
        logger.error(f'Failed to buy from foreign exchange.')
        Order.rollback_batch(batch_id)
        return

    with transaction.atomic():
        Order.objects.filter(status=ORDER_STATUS_PROCESSING, batch_id=batch_id).update(status=ORDER_STATUS_PROCESSED)
        logger.info(f'Successfully completed orders in batch {batch_id}.')
