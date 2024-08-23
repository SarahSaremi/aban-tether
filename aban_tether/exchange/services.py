from django.db import transaction

from account.models import Wallet
from exchange.models import Order


class InsufficientFundsError(Exception):
    pass


class OrderService:
    def __init__(self, account):
        self.account = account

    def create_order(self, amount, crypto):
        if self.withdraw_from_wallet(amount):
            order = Order.objects.create(account=self.account, amount=amount, crypto_currency=crypto)
            return order
        else:
            raise InsufficientFundsError("Insufficient funds in wallet")

    @transaction.atomic
    def withdraw_from_wallet(self, amount):
        wallet = Wallet.objects.select_for_update().get(account=self.account)
        if wallet.balance >= amount:
            wallet.balance -= amount
            wallet.save()
            return True
        return False
