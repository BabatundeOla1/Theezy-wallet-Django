from decimal import Decimal
from uuid import uuid4

from django.contrib.sites import requests
import requests
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from theezyWallet import settings
from .models import Transactions, Wallet
from wallet.serializers import FundSerializer, TransferSerializer


# Create your views here.
@api_view()
def welcome(request):
    return Response(f"Welcome to WhitePay")

def greeting(request,name):
    return render(request,'hello.html',context={'name':name})

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def fund_wallet(request):
    data = FundSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    amount = data.validated_data['amount']
    amount *= 100
    email = request.user.email
    reference = f"ref_{uuid4().hex}"
    Transactions.objects.create(
        amount=amount,
        reference=reference,
        sender=request.user,
    )
    url = 'https://api.paystack.co/transaction/initialize'
    secret = settings.PAYSTACK_SECRET_KEY
    headers = {
        'Authorization': f'Bearer {secret}'
    }
    data = {
        'amount': amount,
        'reference':reference,
        'email':email,
        "callback_url": "http://localhost:8000/wallet/fund/verify"
    }
    try:
        response_str = requests.post(url=url, data=data, headers=headers)
        response = response_str.json()
        if response['status']:
            return Response(data=response, status=status.HTTP_200_OK)
        return None
    except requests.exceptions.RequestException as e:
        return Response({"message": "Unable to complete transaction"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def verify_funds(request):
    reference = request.GET.get('reference')
    secret = settings.PAYSTACK_SECRET_KEY
    headers = {
        'Authorization': f'Bearer {secret}'
    }
    url = f'https://api.paystack.co/transaction/verify/{reference}'
    response_str = requests.get(url=url, headers=headers)
    response = response_str.json()
    if response['status'] and response['data']['status'] == "success":
        amount = (response['data']['amount'] / 100)
        try:
            transaction = Transactions.objects.get(reference=reference, verified=False)
        except Transactions.DoesNotExist:
            return Response({"message": "Transaction does not exist"}, status=status.HTTP_404_NOT_FOUND)


        wallet = get_object_or_404(Wallet, user=transaction.sender)
        wallet.deposit(Decimal(amount))

        subject = "Theezy-Wallet Alert"
        message = f"""Transaction occurred on your wallet
                    You received : {amount} 
                    from {transaction.sender.username}
                """

        from_email = settings.EMAIL_HOST_USER
        recipient_email = request.user.email
        print("Receiver", recipient_email)
        send_mail(
            subject= subject,
            message=message,
            from_email= from_email,
            recipient_list=[recipient_email]
        )

        transaction.verified = True
        transaction.save()
        return Response({"message": "Deposit successful"}, status=status.HTTP_200_OK)
    return Response({"message": "Transaction not successful"}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def transfer_funds(request):
    data = TransferSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    amount = data.validated_data['amount']
    account_number = data.validated_data['account_number']
    sender = request.user
    sender_wallet = get_object_or_404(Wallet, user=sender)
    receiver_wallet = get_object_or_404(Wallet, account_number=account_number)
    receiver = receiver_wallet.user
    with transaction.atomic():
        reference = f"ref_{uuid4().hex}"
        try:
            sender_wallet.withdraw(amount)
        except ValueError:
            return Response({"message": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
        Transactions.objects.create(
            amount = amount,
            sender=sender,
            account_number = account_number,
            reference = reference,
            transaction_type = "T",
            verified = True
        )
        subject = "Theezy-Wallet Alert"
        message = f"""Debit Transaction occurred on your wallet
                    You received : {amount} 
                    from {sender.first_name} {sender.last_name}
                    ****Thank you for banking with us****
                """

        from_email = settings.EMAIL_HOST_USER
        recipient_email = sender.email

        send_mail(
            subject= subject,
            message=message,
            from_email= from_email,
            recipient_list=[recipient_email]
        )


        reference = f"ref_{uuid4().hex}"
        receiver.deposit(amount)
        Transactions.objects.create(
            amount=amount,
            receiver = receiver,
            account_number=account_number,
            reference=reference,
            transaction_type="D",
            verified = True
        )
        subject = "Theezy-Wallet Alert"
        message = f"""Credit Transaction occurred on your wallet
                    You received : {amount} 
                    from {receiver.first_name} {receiver.last_name}
                    ****Thank you for banking with us****
                """

        from_email = settings.EMAIL_HOST_USER
        recipient_email = receiver.email
        send_mail(
            subject= subject,
            message=message,
            from_email= from_email,
            recipient_list=[recipient_email]
        )
        return Response({"message": "Transfer Successful"}, status=status.HTTP_200_OK)

