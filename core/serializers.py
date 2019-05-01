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
        fields = ('transaction_type', 'commission')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'sent_amount', 'sender_account', 'receiver_account')


class UserSerializer(serializers.ModelSerializer):
    accounts = AccountSerializer(
        source='get_accounts', many=True, read_only=True
    )
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'accounts', 'transactions')
