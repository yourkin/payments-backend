from .models import User, Transaction, TransactionType, Account

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_jwt.settings import api_settings


class AccountSerializer(serializers.ModelSerializer):
    client = serializers.CharField(source='get_username', read_only=True)

    class Meta:
        model = Account
        fields = ('uuid', 'currency', 'balance', 'client')


class UserSerializerWithToken(serializers.ModelSerializer):

    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    def get_token(self, obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('token', 'username', 'password')


class TransactionTypeSerializer(serializers.ModelSerializer):
    transaction_type = serializers.CharField(
        max_length=5,
        validators=[UniqueValidator(queryset=TransactionType.objects.all())]
    )

    class Meta:
        model = TransactionType
        fields = ('transaction_type', 'commission_rate')


class TransactionSerializer(serializers.ModelSerializer):
    transaction_date = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', read_only=True)
    sender_currency = serializers.CharField(read_only=True)
    commission_rate = serializers.FloatField(read_only=True)
    commission = serializers.DecimalField(read_only=True,
                                          max_digits=6, decimal_places=2)
    receiver_currency = serializers.CharField(read_only=True)
    conversion_rate = serializers.FloatField(read_only=True)
    received_amount = serializers.DecimalField(read_only=True,
                                               max_digits=6, decimal_places=2)

    class Meta:
        model = Transaction
        fields = (
            'id', 'sender_account', 'sender_username', 'sent_amount',
            'sender_currency', 'receiver_account', 'receiver_username',
            'commission_rate', 'commission', 'receiver_currency',
            'conversion_rate', 'received_amount', 'transaction_date',
        )


class UserSerializer(serializers.ModelSerializer):
    accounts = AccountSerializer(
        source='get_accounts', many=True, read_only=True
    )

    class Meta:
        model = User
        fields = ('uuid', 'username', 'accounts')
