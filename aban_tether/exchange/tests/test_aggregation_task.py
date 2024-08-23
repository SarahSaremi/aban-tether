from django.test import TestCase
from decimal import Decimal
from unittest.mock import patch

from account.models import Account, Wallet
from exchange.models import Order
from exchange.tasks import aggregate_and_buy_from_exchange

from exchange.enums import ORDER_STATUS_PENDING


class CeleryTaskTests(TestCase):

    def setUp(self):
        self.account1 = Account.objects.create(username="Customer 1", email='chert')
        self.account2 = Account.objects.create(username="Customer 2", email='chert')
        Wallet.objects.create(account=self.account1, balance=Decimal('50.00'))
        Wallet.objects.create(account=self.account2, balance=Decimal('50.00'))

        # Create some pending orders
        Order.objects.create(account=self.account1, amount=Decimal('5.00'))
        Order.objects.create(account=self.account2, amount=Decimal('5.00'))

    @patch('exchange.tasks.requests.post')
    def test_aggregate_and_buy_from_exchange(self, mock_post):
        mock_post.return_value.status_code = 200

        aggregate_and_buy_from_exchange()

        mock_post.assert_called_once()
        self.assertEqual(Order.objects.filter(status='PROCESSED').count(), 2)

        # Check if no pending orders remain
        self.assertEqual(Order.objects.filter(status=ORDER_STATUS_PENDING).count(), 0)
