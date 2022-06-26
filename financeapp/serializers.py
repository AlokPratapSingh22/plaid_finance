"""serializers for all models"""

from rest_framework import serializers
from .models import Account, Institution, Transaction


class InstitutionSeriralizer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__'


class TransactionsSerializer(serializers.ModelSerializer):
    """Serializer for plaid transaction model"""
    class Meta:
        model = Transaction
        fields = (
            'transaction_id', 'account', 'category_id',
            'transaction_type', 'name', 'amount',
            'payment_channel', 'date', 'authorized_date',
            'pending', 'pending_transaction_id',
            'account_owner', 'transaction_code',
            'item',
        )


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for plaid account model"""
    class Meta:
        model = Account
        fields = [
            'item',
            'account_id',
            'name',
            'official_name',
            'type',
            'subtype',
            'mask',
            'available_balance',
            'curr_balance',
        ]
