from decimal import Decimal

from django.db import models

from .enums import ORDER_STATUS_PENDING, CRYPTO_CHOICES, ORDER_STATUS_CHOICES, CRYPTO_PRICES


class Order(models.Model):
    account = models.ForeignKey(to='account.Account', on_delete=models.CASCADE)
    crypto_currency = models.CharField(max_length=50, choices=CRYPTO_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    submit_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_PENDING)
    batch_id = models.UUIDField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.price = Decimal(float(self.amount) * CRYPTO_PRICES[self.crypto_currency])
        super(Order, self).save(*args, **kwargs)
