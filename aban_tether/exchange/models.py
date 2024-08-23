from django.db import models

from exchange.enums import ORDER_STATUS_PENDING, CRYPTO_CHOICES, ORDER_STATUS_CHOICES


class Order(models.Model):
    account = models.ForeignKey(to='account.Account', on_delete=models.CASCADE)
    crypto_currency = models.CharField(max_length=50, choices=CRYPTO_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    submit_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_PENDING)
    batch_id = models.UUIDField(null=True, blank=True)
