from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from django.urls import reverse

from account.models import Account, Wallet
from exchange.models import Order


class SubmitOrderAPITests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        # Set up s and wallets
        self.account1 = Account.objects.create(username="account 1", email='hi@hio')
        self.wallet1 = Wallet.objects.create(account=self.account1, balance=Decimal('50.00'))

        self.account2 = Account.objects.create(username="account 2", email='hi@hio')
        self.wallet2 = Wallet.objects.create(account=self.account2, balance=Decimal('5.00'))

    def test_submit_order_with_sufficient_funds(self):
        url = reverse('submit-order')
        data = {
            "account_id": self.account1.id,
            "amount": "10.00"
        }

        response = self.client.post(url, data, format='json')

        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify that the order was created
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.account, self.account1)
        self.assertEqual(order.amount, Decimal('10.00'))

        # Verify that the wallet balance was deducted
        self.wallet1.refresh_from_db()
        self.assertEqual(self.wallet1.balance, Decimal('40.00'))

    def test_submit_order_with_insufficient_funds(self):
        url = reverse('submit-order')
        data = {
            "account_id": self.account2.id,
            "amount": "10.00"
        }

        response = self.client.post(url, data, format='json')

        # Assert that the response indicates insufficient funds
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Insufficient funds")

        # Verify that no order was created
        self.assertEqual(Order.objects.count(), 0)

        # Verify that the wallet balance remains unchanged
        self.wallet2.refresh_from_db()
        self.assertEqual(self.wallet2.balance, Decimal('5.00'))

    def test_submit_order_with_exact_funds(self):
        url = reverse('submit-order')
        data = {
            "account_id": self.account2.id,
            "amount": "5.00"
        }

        response = self.client.post(url, data, format='json')

        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify that the order was created
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.account, self.account2)
        self.assertEqual(order.amount, Decimal('5.00'))

        # Verify that the wallet balance was deducted
        self.wallet2.refresh_from_db()
        self.assertEqual(self.wallet2.balance, Decimal('0.00'))

    def test_submit_order_without_account(self):
        url = reverse('submit-order')
        data = {
            "amount": "10.00"
        }

        response = self.client.post(url, data, format='json')

        # Assert that the response indicates a bad request due to missing account
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify that no order was created
        self.assertEqual(Order.objects.count(), 0)
