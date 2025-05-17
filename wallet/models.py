from decimal import Decimal
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models
from user.models import User
from django.conf import settings


# Create your models here.


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    account_number = models.CharField(max_length=11, unique=True)

    def deposit(self, amount):
        if amount > Decimal("0.00"):
            self.balance += amount
            self.save()
            return True
        return False

    def withdraw(self, amount):
        if amount > Decimal("0.00"):
            if amount < self.balance:
                self.balance -= amount
                self.save()
            return  True
        return False

class Transactions(models.Model):
    TRANSACTION_TYPE = [
        ("D", "Deposit"),
        ("W", "Withdraw"),
        ("T", "Transfer"),
    ]
    reference = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPE, default="D")
    verified = models.BooleanField(default=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender", null=True)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receiver", null=True)

    def save(self, *args, **kwargs):
        if self.sender is None and self.receiver is None:
            raise ValidationError("Sender and receiver cannot be None")
        super().save(*args, **kwargs)


