from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import fields, serializers


from julo_mini_wallet.wallets.models import Wallet, Transaction

User = get_user_model()


class WalletInitSerializer(serializers.Serializer):
    customer_xid = fields.UUIDField(write_only=True)
    token = fields.CharField(read_only=True)

    def create(self, validated_data):
        try:
            user = User.objects.get(username=validated_data['customer_xid'])
        except User.DoesNotExist:
            user = User.objects.create_user(validated_data['customer_xid'], password='julo')

        wallet, created = Wallet.objects.get_or_create(owned_by=user)

        validated_data['token'] = user.auth_token.key
        return validated_data


class WalletSerializer(serializers.ModelSerializer):
    owned_by = fields.CharField(read_only=True, source='owned_by.username')
    balance = fields.DecimalField(read_only=True, max_digits=15, decimal_places=0)

    class Meta:
        model = Wallet
        fields = ['id', 'owned_by', 'status', 'enabled_at', 'balance']
        read_only_fields = ['id', 'owned_by', 'status', 'enabled_at', 'balance']


class WalletEnableSerializer(serializers.ModelSerializer):
    owned_by = fields.CharField(read_only=True, source='owned_by.username')
    balance = fields.DecimalField(read_only=True, max_digits=15, decimal_places=0)

    class Meta:
        model = Wallet
        fields = ['id', 'owned_by', 'status', 'enabled_at', 'balance']
        read_only_fields = ['id', 'owned_by', 'status', 'enabled_at', 'balance']

    def validate(self, data):
        if self.instance.is_enabled:
            raise serializers.ValidationError('Already enabled')
        return data

    def update(self, instance, validated_data):
        validated_data['status'] = Wallet.STATUS.ENABLED
        validated_data['enabled_at'] = datetime.now()
        return super().update(instance, validated_data)


class WalletDisableSerializer(serializers.ModelSerializer):
    is_disabled = fields.BooleanField(write_only=True, required=True)
    owned_by = fields.CharField(read_only=True, source='owned_by.username')
    balance = fields.DecimalField(read_only=True, max_digits=15, decimal_places=0)

    class Meta:
        model = Wallet
        fields = ['is_disabled', 'id', 'owned_by', 'status', 'enabled_at', 'balance']
        read_only_fields = ['id', 'owned_by', 'status', 'enabled_at', 'balance']

    def validate_is_disabled(self, value):
        if value is not True:
            raise serializers.ValidationError('is_disabled must be true')
        return value

    def validate(self, data):
        if self.instance.is_disabled:
            raise serializers.ValidationError('Already disabled')
        return data

    def update(self, instance, validated_data):
        del validated_data['is_disabled']
        validated_data['status'] = Wallet.STATUS.DISABLED
        validated_data['disabled_at'] = datetime.now()
        return super().update(instance, validated_data)


class WalletTransactionSerializer(serializers.ModelSerializer):
    executed_by = fields.UUIDField(read_only=True, source="executed_by.username")
    amount = fields.DecimalField(read_only=True, source='abs_amount', max_digits=15, decimal_places=0)

    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'executed_by', 'status', 'created_at', 'amount', 'reference_id']


class WalletDepositSerializer(serializers.ModelSerializer):
    deposited_by = fields.UUIDField(read_only=True, source="executed_by.username")
    deposited_at = fields.DateTimeField(read_only=True, source="created_at")

    class Meta:
        model = Transaction
        fields = ['id', 'deposited_by', 'status', 'deposited_at', 'amount', 'reference_id']
        read_only_fields = ['id', 'deposited_by', 'status', 'deposited_at']
        extra_kwargs = {
            'amount': {'min_value': 1},
        }

    def create(self, validated_data):
        validated_data['transaction_type'] = Transaction.TRANSACTION_TYPE.DEPOSIT
        validated_data['executed_by'] = self.context['request'].user
        validated_data['wallet'] = self.context['request'].user.wallet

        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().filter(owned_by=self.context['request'].user).get()
            instance = super().create(validated_data)

        return instance


class WalletWithdrawSerializer(serializers.ModelSerializer):
    withdrawn_by = fields.UUIDField(read_only=True, source="executed_by.username")
    withdrawn_at = fields.DateTimeField(read_only=True, source="created_at")

    class Meta:
        model = Transaction
        fields = ['id', 'withdrawn_by', 'status', 'withdrawn_at', 'amount', 'reference_id']
        read_only_fields = ['id', 'withdrawn_by', 'status', 'withdrawn_at']
        extra_kwargs = {
            'amount': {'min_value': 1},
        }

    def validate_amount(self, value):
        if value > self.context['request'].user.wallet.balance:
            raise serializers.ValidationError('Insufficient Funds')
        return value

    def create(self, validated_data):
        validated_data['transaction_type'] = Transaction.TRANSACTION_TYPE.WITHDRAW
        validated_data['executed_by'] = self.context['request'].user
        validated_data['wallet'] = self.context['request'].user.wallet

        # Preventing race condition
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().filter(owned_by=self.context['request'].user).get()
            if validated_data['amount'] > wallet.balance:
                raise serializers.ValidationError('Insufficient Funds')

            validated_data['amount'] = validated_data['amount'] * -1
            instance = super().create(validated_data)

        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['amount'] = str(instance.abs_amount)
        return ret
