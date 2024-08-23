from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'amount', 'status', 'submit_date']


class OrderRequestSerializer(serializers.Serializer):
    account_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    crypto = serializers.CharField(max_length=100, required=True)
