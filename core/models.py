from uuid import uuid4

from django.db import models

from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    """
    Payments user model
    """
    username = models.CharField(max_length=100, blank=True, unique=True)
    transactions = models.ManyToManyField('Transaction')
    USERNAME_FIELD = 'username'


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='profile'
    )


class Account(models.Model):
    uuid = models.UUIDField(default=uuid4, primary_key=True)
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
    balance = models.PositiveIntegerField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,on_delete=models.CASCADE,
        related_name='account'
    )


class Currency(models.Model):
    USD = 'USD'
    EUR = 'EUR'
    CNY = 'CNY'
    CURRENCY_CHOICES = (
        (USD, 'US Dollar'),
        (EUR, 'Euro'),
        (CNY, 'Chinese Yuan'),

    )
    currency = models.CharField(
        primary_key=True, max_length=3, choices=CURRENCY_CHOICES
    )

    class Meta:
        verbose_name_plural = 'Currencies'


class CurrencyConversionRate(models.Model):
    from_currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name='from_currency'
    )
    to_currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name='to_currency'
    )
    rate = models.FloatField()


class TransactionType(models.Model):
    """
    Transaction type model
    """
    FUNDS_TRANSFER_TO_SELF = 'SELF'
    FUNDS_TRANSFER_TO_OTHER = 'OTHER'
    TRANSACTION_TYPE_CHOICES = (
        (FUNDS_TRANSFER_TO_SELF, 'Funds Transfer to Self'),
        (FUNDS_TRANSFER_TO_OTHER, 'Funds Transfer to Other'),

    )
    transaction_type = models.CharField(
        max_length=5, choices=TRANSACTION_TYPE_CHOICES, primary_key=True,
    )
    commission = models.FloatField()

    def __str__(self):
        return self.transaction_type


class Transaction(models.Model):
    """
    Transaction model
    """
    amount = models.PositiveIntegerField()
    sender = models.ForeignKey(
        Account, related_name='funds_sender', on_delete=models.PROTECT
    )
    receiver = models.ForeignKey(
        Account, related_name='funds_receiver', on_delete=models.PROTECT
    )
    transaction_type = models.ForeignKey(
        TransactionType, on_delete=models.PROTECT
    )

    def save(self, *args, **kwargs):
        super(Transaction, self).save(*args, **kwargs)
        self.sender.balance = self.sender.balance - self.amount
        self.receiver.balance = self.receiver.balance + self.amount
        self.sender.save()
        self.receiver.save()
