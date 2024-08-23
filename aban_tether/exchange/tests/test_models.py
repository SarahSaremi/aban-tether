from django.test import TestCase
from decimal import Decimal

from account.models import Wallet, Account
from exchange.models import Order

from exchange.enums import ORDER_STATUS_PENDING


class ModelsTestCase(TestCase):
    def setUp(self):
        self.account = Account.objects.create(username="Test Customer", email='hi@sldk')
        self.wallet = Wallet.objects.create(account=self.account, balance=Decimal('100.00'))

    def test_wallet_balance(self):
        self.assertEqual(self.wallet.balance, Decimal('100.00'))

    def test_create_order(self):
        order = Order.objects.create(account=self.account, amount=Decimal('20.00'))
        self.assertEqual(order.amount, Decimal('20.00'))
        self.assertEqual(order.status, ORDER_STATUS_PENDING)
