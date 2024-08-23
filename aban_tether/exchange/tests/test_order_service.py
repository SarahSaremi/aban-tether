from django.test import TestCase
from decimal import Decimal

from account.models import Account, Wallet
from exchange.models import Order
from exchange.services import OrderService, InsufficientFundsError


class OrderServiceTests(TestCase):
    def setUp(self):
        self.account = Account.objects.create(username="Test Customer", email='hi@sldk')
        self.wallet = Wallet.objects.create(account=self.account, balance=Decimal('100.00'))

    def test_create_order_with_sufficient_funds(self):
        service = OrderService(self.account)
        order = service.create_order(Decimal('25.00'), crypto='tether')

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().amount, Decimal('25.00'))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('75.00'))

    def test_create_order_with_insufficient_funds(self):
        service = OrderService(self.account)

        with self.assertRaises(InsufficientFundsError):
            service.create_order(Decimal('150.00'), crypto='tether')

        self.assertEqual(Order.objects.count(), 0)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('100.00'))
