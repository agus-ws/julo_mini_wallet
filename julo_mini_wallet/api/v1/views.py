from django.contrib.auth.models import User

from rest_framework import generics, status, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema

from julo_mini_wallet.wallets.models import Wallet
from .permissions import IsWalletEnabled
from .serializers import (
    WalletInitSerializer, WalletSerializer, WalletEnableSerializer, WalletDisableSerializer, WalletTransactionSerializer,
    WalletDepositSerializer, WalletWithdrawSerializer
)

# 
class WalletAutoSchema(AutoSchema):
    pass


class ResponseMixin:
    resource_name = ['', '']

    def get_response_dict(self):
        response_dict = {
            'status': 'success',
            'data': None,
        }
        return response_dict

    def _get_single_response(self, response):
        response_dict = self.get_response_dict()
        if self.resource_name[0]:
            response_dict['data'] = {
                self.resource_name[0]: response.data
            }
        else:    
            response_dict['data'] = response.data
        response.data = response_dict
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request)
        response = self._get_single_response(response)
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request)
        response = self._get_single_response(response)
        return response

    def list(self, request, *args, **kwargs):
        response = super().list(request)
        resp_data = self.get_response_dict()
        if isinstance(response.data, list):
            resp_data['data'] = {
                self.resource_name[1]: response.data
            }
            response.data = resp_data
        else:
            resp_data.update(response.data)
            response.data = resp_data
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request)
        response = self._get_single_response(response)
        return response


class WalletInit(ResponseMixin, generics.CreateAPIView):
    schema = WalletAutoSchema(
        tags=['Wallet'],
        component_name='wallet',
        operation_id_base='wallet',
    )

    serializer_class = WalletInitSerializer
    permission_classes = [AllowAny]


class WalletUpdate(ResponseMixin, mixins.CreateModelMixin, generics.RetrieveAPIView, generics.UpdateAPIView, generics.GenericAPIView):
    schema = WalletAutoSchema(
        tags=['Wallet'],
        component_name='wallet',
        operation_id_base='wallet',
    )
    resource_name = ['wallet', 'wallets']

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        response = self._get_single_response(response)
        return response

    def get_serializer_class(self):
        serializer_class = WalletEnableSerializer  # POST / GET
        request_method = self.request.method.lower()
        if request_method == 'patch':
            serializer_class = WalletDisableSerializer

        return serializer_class

    def get_object(self):
        obj = self.request.user.wallet

        if self.request.method.lower() == 'get' and obj.is_disabled:
            raise self.permission_denied(self.request, IsWalletEnabled.message)

        self.check_object_permissions(self.request, obj)
        return obj


class WalletTransactionList(ResponseMixin, generics.ListAPIView):
    schema = WalletAutoSchema(
        tags=['Wallet'],
        component_name='transaction',
        operation_id_base='transaction',
    )
    resource_name = ['transaction', 'transactions']

    serializer_class = WalletTransactionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsWalletEnabled]

    def get_queryset(self):
        return self.request.user.wallet.transactions.order_by('-created_at')


class WalletDeposit(ResponseMixin, generics.CreateAPIView):
    schema = WalletAutoSchema(
        tags=['Wallet'],
        component_name='deposit',
        operation_id_base='deposit',
    )
    resource_name = ['deposit', 'deposits']

    serializer_class = WalletDepositSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsWalletEnabled]


class WalletWithdraw(ResponseMixin, generics.CreateAPIView):
    schema = WalletAutoSchema(
        tags=['Wallet'],
        component_name='withdrawal',
        operation_id_base='withdrawal',
    )
    resource_name = ['withdrawal', 'withdrawals']

    serializer_class = WalletWithdrawSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsWalletEnabled]
