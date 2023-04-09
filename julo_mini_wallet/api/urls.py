import os

from django.urls import path, include
from django.views.generic import TemplateView

from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from .v1.views import WalletInit, WalletUpdate, WalletTransactionList, WalletDeposit, WalletWithdraw


app_name = 'api_v1'

urlpatterns = [
    path('init', WalletInit.as_view(), name='init'),
    path('wallet', WalletUpdate.as_view(), name='wallet_update'),

    path('wallet/transactions', WalletTransactionList.as_view(), name='transaction_list'),
    path('wallet/deposits', WalletDeposit.as_view(), name='deposit'),
    path('wallet/withdrawals', WalletWithdraw.as_view(), name='withdraw'),
]
