from django.db import transaction

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TransactionType, Transaction, Account, User, Currency
from .serializers import (UserSerializer, UserSerializerWithToken,
                          TransactionSerializer, TransactionTypeSerializer,
                          AccountSerializer)

from .conf import CURRENCY, INITIAL_BALANCE


@api_view(['GET'])
def current_user(request):
    """
    Determine the current user by their token, and return their data
    """

    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserList(APIView):
    """
    Create a new user. It's called 'UserList' because normally we'd have a get
    method here for retrieving a list of all User objects.
    """

    permission_classes = (permissions.AllowAny,)

    @transaction.atomic
    def post(self, request, format=None):
        serializer = UserSerializerWithToken(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()

            # Setup client accounts with initial amounts
            for cur in CURRENCY:
                cur_obj = Currency.objects.get(currency=cur)
                Account.objects.create(
                    currency=cur_obj, balance=INITIAL_BALANCE[cur],
                    user=instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TransactionTypeViewSet(viewsets.ModelViewSet):
    queryset = TransactionType.objects.all()
    serializer_class = TransactionTypeSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.sender_account.user.transactions.add(instance)
        if instance.sender_account.user != instance.receiver_account.user:
            instance.receiver_account.user.transactions.add(transaction)


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

