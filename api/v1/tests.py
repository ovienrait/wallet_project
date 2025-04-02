import threading
import time
from datetime import datetime

import pytest
import requests
from django.urls import reverse
from rest_framework import status

from wallets.models import DEFAULT_BALANCE, Wallet

print_lock = threading.Lock()


@pytest.fixture
def create_wallet():
    '''Фикстура для создания объекта кошелька.'''

    def _create_wallet(uuid='existent', balance=DEFAULT_BALANCE):
        return Wallet.objects.create(uuid=uuid, balance=balance)
    return _create_wallet


@pytest.fixture
def wallet_url(live_server):
    '''Фикстура для создания URL строки.'''

    def _wallet_url(endpoint, wallet=None):
        if wallet:
            wallet_uuid = wallet.uuid
        else:
            wallet_uuid = 'nonexistent'
        relative_url = reverse(endpoint, kwargs={'wallet_uuid': wallet_uuid})
        return f'{live_server.url}{relative_url}'
    return _wallet_url


@pytest.fixture
def perform_operation(wallet_url):
    '''Фикстура для создания ответа сервера.'''

    def _perform_operation(
            wallet, operation_type, amount, status_list=None,
            multithreads=False):
        start_time = datetime.fromtimestamp(
            time.time()).strftime('%H:%M:%S.%f')
        url = wallet_url('wallet-operation', wallet=wallet)
        data = {'operation_type': operation_type, 'amount': amount}
        response = requests.post(url, json=data)
        if multithreads:
            status_list.append([response.status_code, operation_type, amount])
            with print_lock:
                print(f'{threading.current_thread().name:<20}',
                      f'status code: {response.status_code:<5}',
                      f'response: {response.text:<30}',
                      f'started at: {start_time}')
        return response
    return _perform_operation


@pytest.mark.django_db
@pytest.mark.parametrize(
    'use_wallet, expected_status, expected_result',
    [
        # Параметры теста для существующего кошелька:
        (True, status.HTTP_200_OK, ['balance', DEFAULT_BALANCE]),
        # Параметры теста для несуществующего кошелька:
        (False, status.HTTP_404_NOT_FOUND, ['error', 'Wallet not found']),
    ]
)
def test_get_balance(
    create_wallet, wallet_url, use_wallet, expected_status, expected_result
):
    '''Тест получения баланса кошелька.'''

    wallet = create_wallet() if use_wallet else None
    url = wallet_url('wallet-balance', wallet=wallet)
    response = requests.get(url)

    assert response.status_code == expected_status
    response_data = response.json()
    assert response_data[expected_result[0]] == expected_result[1]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'use_wallet, operation_type, amount, balance, expected_status, '
    'error_message',
    [
        # Параметры теста при проверке успешного пополнения:
        (True, 'DEPOSIT', 500, 1000, status.HTTP_200_OK, None),
        # Параметры теста при проверке успешного снятия:
        (True, 'WITHDRAW', 200, 1000, status.HTTP_200_OK, None),
        # Параметры теста при превышении лимита на снятие:
        (True, 'WITHDRAW', 55000, 60000, status.HTTP_400_BAD_REQUEST,
         'Withdrawal amount exceeds one-time limit'),
        # Параметры теста при недостаточном балансе:
        (True, 'WITHDRAW', 2000, 1000, status.HTTP_400_BAD_REQUEST,
         'Insufficient funds'),
        # Параметры теста при некорректном типе операции:
        (True, 'INVALID', 100, 1000, status.HTTP_400_BAD_REQUEST, None),
        # Параметры теста для несуществующего кошелька:
        (False, 'DEPOSIT', 100, None, status.HTTP_404_NOT_FOUND,
         'Wallet not found'),
    ]
)
def test_wallet_operations(
    create_wallet, perform_operation, use_wallet, operation_type, amount,
    balance, expected_status, error_message
):
    '''Тест проведения операций с кошельком.'''

    wallet = create_wallet(balance=balance) if use_wallet else None
    response = perform_operation(wallet, operation_type, amount)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        expected_balance = (
            balance + amount) if operation_type == 'DEPOSIT' else (
                balance - amount)
        assert response.json()['updated_balance'] == expected_balance
        wallet.refresh_from_db()
        assert wallet.balance == expected_balance
    elif error_message:
        assert error_message in response.json()['error']


@pytest.mark.django_db
@pytest.mark.parametrize(
    'deposit_count, deposit_amount, withdraw_count, withdraw_amount',
    [
        (10, 500, 5, 2000),  # 10 пополнений по 500, 5 снятий по 2000
    ]
)
def test_concurrent_operations(
    create_wallet, perform_operation, deposit_count, deposit_amount,
    withdraw_count, withdraw_amount
):
    '''Тест проведения одновременных операций с одним кошельком.'''

    wallet = create_wallet()
    status_list = []
    start_event = threading.Event()

    def synchronized_operation(wallet, operation_type, amount, status_list):
        start_event.wait()
        perform_operation(wallet, operation_type, amount, status_list, True)

    print('\nThreads processing:')
    threads = []
    threads.extend([threading.Thread(target=synchronized_operation, args=(
        wallet, 'DEPOSIT', deposit_amount, status_list),
        name=f'Deposit Thread {i + 1}') for i in range(deposit_count)])
    threads.extend([threading.Thread(target=synchronized_operation, args=(
        wallet, 'WITHDRAW', withdraw_amount, status_list),
        name=f'Withdraw Thread {i + 1}') for i in range(withdraw_count)])

    for thread in threads:
        thread.start()

    time.sleep(0.5)
    start_event.set()

    for thread in threads:
        thread.join()

    deposit_result = sum(x[2] for x in filter(
        lambda x: x[0] == 200 and x[1] == 'DEPOSIT', status_list))
    withdraw_result = sum(x[2] for x in filter(
        lambda x: x[0] == 200 and x[1] == 'WITHDRAW', status_list))
    expected_balance = DEFAULT_BALANCE + deposit_result - withdraw_result

    updated_wallet = Wallet.objects.get(uuid=wallet.uuid)
    assert updated_wallet.balance == expected_balance
    assert len(status_list) == deposit_count + withdraw_count
