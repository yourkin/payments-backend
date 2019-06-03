from django.db import transaction
from django.shortcuts import render

from rest_framework import permissions, viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import TransactionType, Transaction, Account, User, Currency
from .serializers import (UserSerializer, UserSerializerWithToken,
                          TransactionSerializer, TransactionTypeSerializer,
                          AccountSerializer)

from .conf import CURRENCY, INITIAL_BALANCE


@api_view(['GET'])
def current_user(request):
    """
    Determine the current user by their token and return their data
    """

    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializerWithToken
    permission_classes = (permissions.AllowAny,)

    @transaction.atomic()
    def perform_create(self, serializer):
        if serializer.is_valid():
            instance = serializer.save()

            # Setup client accounts with initial amounts
            for cur in CURRENCY:
                cur_obj = Currency.objects.get(currency=cur)
                Account.objects.create(currency=cur_obj,
                                       balance=INITIAL_BALANCE[cur],
                                       user=instance)


class TransactionTypeViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    queryset = TransactionType.objects.all()
    serializer_class = TransactionTypeSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @transaction.atomic()
    def perform_create(self, serializer):
        instance = serializer.save()
        instance.sender_account.user.transactions.add(instance)
        if instance.sender_account.user != instance.receiver_account.user:
            instance.receiver_account.user.transactions.add(instance)


class AccountViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


def index(request):
    return render(request, 'index.html')
