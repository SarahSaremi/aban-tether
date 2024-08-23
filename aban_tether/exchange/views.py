from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from account.models import Account

from .models import Order
from .serializers import OrderSerializer, OrderRequestSerializer
from account.exceptions import InsufficientFundsError


class SubmitOrderView(APIView):
    def post(self, request):
        serializer = OrderRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        try:
            account = Account.objects.get(id=validated_data['account_id'])
            order = Order.create_order(account, validated_data['amount'], validated_data['crypto'])
            response_serializer = OrderSerializer(order)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
        except InsufficientFundsError:
            return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
