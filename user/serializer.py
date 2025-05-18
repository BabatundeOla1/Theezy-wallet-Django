from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from wallet.models import Transactions, Wallet
from .models import Profile, User



class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['first_name', 'last_name', 'email','username','password','phone']


class ProfileSerializer(serializers.ModelSerializer):
    bvn = serializers.CharField(max_length=11, min_length=11)
    class Meta:
        model = Profile
        field = ['image', 'address', 'nin', 'bvn']

class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    account_number = serializers.CharField(max_length=10)

class UserSerializer(serializers.ModelSerializer):
    wallets = WalletSerializer()
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone', 'wallet']


class TransactionSerializer(serializers.ModelSerializer):
    sender = UserSerializer()

    class Meta:
        model = Transactions
        fields = [
            'id',
            'sender',
            'receiver',
            'amount',
            'transaction_type',
            'transaction_date',
        ]