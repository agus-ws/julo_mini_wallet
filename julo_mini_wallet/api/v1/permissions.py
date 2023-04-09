from rest_framework import permissions, status


class IsWalletEnabled(permissions.BasePermission):
    message = 'Wallet disabled.'
    code = status.HTTP_404_NOT_FOUND

    def has_permission(self, request, view):
        return request.user.wallet.is_enabled


class IsWalletDisabled(permissions.BasePermission):
    message = 'Already enabled.'
    code = status.HTTP_404_NOT_FOUND

    def has_permission(self, request, view):
        return request.user.wallet.is_disabled
