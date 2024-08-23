from django.test import TestCase
from decimal import Decimal
from unittest.mock import patch

from account.models import Account, Wallet

from exchange.models import Order
from exchange.tasks import aggregate_and_buy_from_exchange
from exchange.enums import ORDER_STATUS_PROCESSED

from exchange.enums import ORDER_STATUS_FAILED


class OrderRollbackTests(TestCase):

    def setUp(self):
        self.account = Account.objects.create(username="Test Customer", email="<EMAIL>")
        self.wallet = Wallet.objects.create(account=self.account, balance=Decimal('100.00'))

    def test_rollback_order(self):
        order = Order.create_order(self.account, 50.00, crypto_currency='tether')
        batch_id = Order.assign_batch_id(Order.objects.filter(id=order.id))

        Order.rollback_batch(batch_id)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('100.00'))

        order.refresh_from_db()
        self.assertEqual(order.status, 'failed')

    @patch('exchange.tasks.buy_from_exchange')
    def test_aggregate_and_buy_from_exchange_with_failure(self, mock_buy_from_exchange):
        order1 = Order.create_order(self.account, 5.00, crypto_currency='tether')
        order2 = Order.create_order(self.account, 6.00, crypto_currency='tether')

        mock_buy_from_exchange.return_value = {'status_code': 500}

        aggregate_and_buy_from_exchange()

        order1.refresh_from_db()
        order2.refresh_from_db()
        self.assertEqual(order1.status, ORDER_STATUS_FAILED)
        self.assertEqual(order2.status, ORDER_STATUS_FAILED)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('100.00'))

    @patch('requests.post')
    def test_aggregate_and_buy_from_exchange_with_success(self, mock_post):
        order1 = Order.create_order(self.account, 5.00, crypto_currency='tether')
        order2 = Order.create_order(self.account, 6.00, crypto_currency='tether')

        mock_post.return_value = {'status_code': 200}

        aggregate_and_buy_from_exchange()

        order1.refresh_from_db()
        order2.refresh_from_db()
        self.assertEqual(order1.status, ORDER_STATUS_PROCESSED)
        self.assertEqual(order2.status, ORDER_STATUS_PROCESSED)

        self.assertIsNotNone(order1.batch_id)
        self.assertEqual(order1.batch_id, order2.batch_id)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('89.00'))
