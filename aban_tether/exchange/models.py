import logging
from uuid import uuid4

from decimal import Decimal
from django.db import models, transaction

from .enums import ORDER_STATUS_PENDING, ORDER_STATUS_FAILED, ORDER_STATUS_PROCESSING, CRYPTO_CHOICES, ORDER_STATUS_CHOICES, CRYPTO_PRICES


logger = logging.getLogger(__name__)


class Order(models.Model):
    account = models.ForeignKey(to='account.Account', on_delete=models.CASCADE)
    crypto_currency = models.CharField(max_length=50, choices=CRYPTO_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    submit_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_PENDING)
    batch_id = models.UUIDField(null=True, blank=True)

    @classmethod
    def create_order(cls, account, amount, crypto_currency):
        with transaction.atomic():
            price = Decimal(amount * CRYPTO_PRICES[crypto_currency])
            wallet = account.wallet
            if not wallet.withdraw(price):
                raise ValidationError("Insufficient funds")
            order = cls(account=account, amount=amount, crypto_currency=crypto_currency, price=price)
            order.save()
            logger.info(f'Order {order.id} created for account {account.id} with amount {amount}.')
            return order

    @staticmethod
    def assign_batch_id(orders):
        batch_id = uuid4()
        orders.update(batch_id=batch_id, status=ORDER_STATUS_PROCESSING)
        logger.info(f'Assigned batch ID {batch_id} to orders {[order.id for order in orders]}.')
        return batch_id

    @classmethod
    def rollback_batch(cls, batch_id):
        orders = cls.objects.filter(batch_id=batch_id, status=ORDER_STATUS_PROCESSING)
        with transaction.atomic():
            for order in orders:
                wallet = order.account.wallet
                wallet.deposit(order.price)
                order.status = ORDER_STATUS_FAILED
                order.save()
                logger.info(f'Order {order.id} rolled back for account {order.account.id}. Amount {order.amount} returned to wallet.')
            logger.info(f'Rollback complete for batch ID {batch_id}.')
