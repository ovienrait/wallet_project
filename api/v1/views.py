from django.db import transaction
from drf_spectacular.utils import (OpenApiExample, OpenApiParameter,
                                   OpenApiResponse, extend_schema)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from wallets.models import Wallet

from .serializers import WalletBalanceSerializer, WalletOperationSerializer


class WalletBalanceView(APIView):
    '''Обработчик для получения баланса кошелька.'''

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='wallet_uuid',
                type=str,
                location=OpenApiParameter.PATH,
                required=True),
        ],
        responses={
            200: OpenApiResponse(
                description='Кошелёк найден',
                response={
                    'type': 'object', 'properties': {'balance': {
                        'type': 'integer', 'example': 1000}}}),
            404: OpenApiResponse(
                description='Кошелёк не найден',
                response={
                    'type': 'object', 'properties': {'error': {
                        'type': 'string', 'example': 'Wallet not found'}}}),
        },
        description='Возвращает текущий баланс кошелька по его UUID.'
    )
    def get(self, request, wallet_uuid):
        try:
            wallet = Wallet.objects.get(uuid=wallet_uuid)
            serializer = WalletBalanceSerializer(wallet)
            return Response(serializer.data)
        except Wallet.DoesNotExist:
            return Response(
                {'error': 'Wallet not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class WalletOperationView(APIView):
    '''Обработчик для выполнения операций с кошельком.'''

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='wallet_uuid',
                type=str,
                location=OpenApiParameter.PATH,
                required=True),
        ],
        request=WalletOperationSerializer,
        examples=[
            OpenApiExample(name='Deposit Operation', value={
                'operation_type': 'DEPOSIT', 'amount': 500
            }, request_only=True),
            OpenApiExample(name='Withdraw Operation', value={
                'operation_type': 'WITHDRAW', 'amount': 200
            }, request_only=True),
        ],
        responses={
            200: OpenApiResponse(
                description='Операция выполнена успешно',
                response={
                    'type': 'object', 'properties': {'updated_balance': {
                        'type': 'integer', 'example': 1500}}}),
            400: OpenApiResponse(
                description='Ошибка валидации или недостаточно средств',
                response={
                    'type': 'object', 'properties': {'error': {
                        'type': 'string', 'enum': [
                            'Insufficient funds',
                            'Withdrawal amount exceeds one-time limit']}}}),
            404: OpenApiResponse(
                description='Кошелёк не найден',
                response={
                    'type': 'object', 'properties': {'error': {
                        'type': 'string', 'example': 'Wallet not found'}}}),
        },
        description='Позволяет пополнить (DEPOSIT) или снять (WITHDRAW) '
                    'средства с кошелька по его UUID.'
    )
    def post(self, request, wallet_uuid):
        serializer = WalletOperationSerializer(data=request.data)
        if serializer.is_valid():
            operation_type = serializer.validated_data['operation_type']
            amount = serializer.validated_data['amount']
            try:
                with transaction.atomic():
                    wallet = Wallet.objects.select_for_update(
                    ).get(uuid=wallet_uuid)
                    if operation_type == "DEPOSIT":
                        wallet.balance += amount
                    elif operation_type == "WITHDRAW":
                        if wallet.balance < amount:
                            return Response(
                                {'error': 'Insufficient funds'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        wallet.balance -= amount
                    wallet.save()
                    return Response({'updated_balance': wallet.balance})
            except Wallet.DoesNotExist:
                return Response(
                    {'error': 'Wallet not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
