from rest_framework import serializers

from wallets.models import Wallet


class WalletBalanceSerializer(serializers.ModelSerializer):
    '''Сериализатор для получения баланса кошелька.'''

    class Meta:
        model = Wallet
        fields = ['balance']


class WalletOperationSerializer(serializers.Serializer):
    '''Сериализатор для проведения операций с кошельком.'''

    operation_type = serializers.ChoiceField(choices=('DEPOSIT', 'WITHDRAW'))
    amount = serializers.IntegerField(min_value=1)

    def validate(self, data):
        '''Валидация для установки лимита на снятие средств за раз.'''

        if data['operation_type'] == 'WITHDRAW' and data['amount'] > 50000:
            raise serializers.ValidationError({
                'error': 'Withdrawal amount exceeds one-time limit'
            })
        return data
