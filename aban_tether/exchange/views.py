from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from account.models import Account
from .serializers import OrderSerializer
from .services import OrderService, InsufficientFundsError


class SubmitOrderView(APIView):
    def post(self, request):
        account_id = request.data.get('account_id', None)
        if not account_id:
            return Response({'error': 'Missing account_id'}, status=status.HTTP_400_BAD_REQUEST)
        account = Account.objects.get(id=account_id)
        order_service = OrderService(account)

        try:
            crypto = request.data.get('crypto', None)
            order = order_service.create_order(Decimal(request.data['amount']), crypto)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except InsufficientFundsError:
            return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
