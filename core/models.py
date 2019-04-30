from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


FUNDS_TRANSFER_TO_SELF = 'SELF'
FUNDS_TRANSFER_TO_OTHER = 'OTHER'


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
    balance = models.DecimalField(max_digits=6, decimal_places=2)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,on_delete=models.CASCADE,
        related_name='account'
    )

    def __str__(self):
        return f'{self.user} - {self.currency.currency} : {self.balance}'


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

    def __str__(self):
        return self.currency

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

    def __str__(self):
        return f'{self.from_currency.currency} - {self.to_currency.currency}'


class TransactionType(models.Model):
    """
    Transaction type model
    """
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
    sender = models.ForeignKey(
        Account, related_name='funds_sender', on_delete=models.PROTECT
    )
    receiver = models.ForeignKey(
        Account, related_name='funds_receiver', on_delete=models.PROTECT
    )
    transaction_type = models.ForeignKey(
        TransactionType, on_delete=models.PROTECT
    )

    # Explicitly storing all finance data as post-calculations might differ
    sent_amount = models.DecimalField(max_digits=6, decimal_places=2)
    received_amount = models.DecimalField(max_digits=6, decimal_places=2)
    commission = models.DecimalField(max_digits=6, decimal_places=2)

    # Storing values for permanence and data encapsulation
    sender_currency = models.CharField(max_length=3)
    receiver_currency = models.CharField(max_length=3)
    conversion_rate = models.FloatField()

    def get_transaction_type(self):
        if self.sender.user != self.receiver.user:
            t = FUNDS_TRANSFER_TO_OTHER
        else:
            t = FUNDS_TRANSFER_TO_SELF
        return TransactionType.objects.get(transaction_type=t)

    def get_commission(self):
        return self.sent_amount * self.transaction_type.commission

    def get_conversion_rate(self):
        if self.sender_currency != self.receiver_currency:
            rate = CurrencyConversionRate.objects.get(
                from_currency=self.sender.currency,
                to_currency=self.receiver_currency).rate
        else:
            rate = 1
        return rate

    def save(self, *args, **kwargs):
        self.transaction_type = self.get_transaction_type()
        self.sender_currency = self.sender.currency
        self.receiver_currency = self.receiver.currency
        self.commission = self.get_commission()
        self.conversion_rate = self.get_conversion_rate()
        self.received_amount = (self.sent_amount * self.conversion_rate -
                                self.commission)

        super(Transaction, self).save(*args, **kwargs)

        self.sender.balance = self.sender.balance - self.sent_amount
        self.receiver.balance = self.receiver.balance + self.received_amount
        self.sender.save()
        self.receiver.save()

    def __str__(self):
        return f'{self.sender.user} -> {self.receiver.user}: {self.sent_amount} {self.sender_currency}'
