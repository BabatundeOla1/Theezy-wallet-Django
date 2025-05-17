from itsdangerous import Serializer
from rest_framework import serializers


class FundSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=1000000, decimal_places=2)

class TransferSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1000, max_value=10000000)
    account_number = serializers.CharField(min_length=10, max_length=10)

