from decimal import Decimal
import uuid

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _


from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

User = get_user_model()


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owned_by = models.OneToOneField(User, on_delete=models.PROTECT)

    class STATUS(models.TextChoices):
        ENABLED = 'enabled', _('enabled')
        DISABLED = 'disabled', _('disabled')

    status = models.CharField(choices=STATUS.choices, max_length=8, default=STATUS.DISABLED)
    enabled_at = models.DateTimeField(default=None, null=True)
    disabled_at = models.DateTimeField(default=None, null=True)

    @property
    def is_enabled(self):
        return self.status == self.STATUS.ENABLED

    @property
    def is_disabled(self):
        return self.status == self.STATUS.DISABLED

    @property
    def balance(self):
        return self.transactions.all().aggregate(total=Coalesce(Sum('amount'), Decimal('0')))['total']


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, related_name='transactions', on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    executed_by = models.ForeignKey(User, on_delete=models.PROTECT)

    class TRANSACTION_TYPE(models.TextChoices):
        DEPOSIT = 'deposit', _('deposit')
        WITHDRAW = 'withdraw', _('withdraw')

    transaction_type = models.CharField(choices=TRANSACTION_TYPE.choices, max_length=8)

    class STATUS(models.TextChoices):
        SUCCESS = 'success', _('success')
        FAILED = 'failed', _('failed')

    status = models.CharField(choices=STATUS.choices, max_length=7, default=STATUS.SUCCESS)

    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    reference_id = models.UUIDField(unique=True)

    @property
    def abs_amount(self):
        if self.amount < 0:
            return self.amount * -1

        return self.amount
