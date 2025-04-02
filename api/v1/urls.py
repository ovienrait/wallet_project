from django.urls import path

from .views import WalletBalanceView, WalletOperationView

WALLETS_BASE_URL = 'wallets/<str:wallet_uuid>'

urlpatterns = [
    path(
        f'v1/{WALLETS_BASE_URL}',
        WalletBalanceView.as_view(),
        name='wallet-balance'
    ),
    path(
        f'v1/{WALLETS_BASE_URL}/operation',
        WalletOperationView.as_view(),
        name='wallet-operation'
    )
]
