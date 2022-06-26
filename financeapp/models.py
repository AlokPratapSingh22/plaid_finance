from django.db import models
from django.conf import settings


class Institution(models.Model):
    institution_id = models.CharField(max_length=200)
    name = models.CharField(max_length=256)

    def __str__(self) -> str:
        return f"{self.institution_id} {self.name}"

    class Meta:
        ordering = ['institution_id']


class PlaidItem(models.Model):
    """model class for plaid item"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False,
                             blank=False, on_delete=models.CASCADE, default=None)
    access_token = models.CharField(max_length=200, unique=True)
    item_id = models.CharField(max_length=200, unique=True)

    def __str__(self) -> str:
        return self.item_id


class Account(models.Model):
    """model class for plaid account"""
    account_id = models.CharField(max_length=200, null=True, unique=True)
    curr_balance = models.FloatField(null=True)
    available_balance = models.FloatField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                             blank=True, on_delete=models.CASCADE, default=None)
    name = models.CharField(max_length=200, null=True)
    mask = models.CharField(max_length=200, null=True)
    subtype = models.CharField(max_length=200, null=True)
    type = models.CharField(max_length=200, null=True)
    official_name = models.CharField(max_length=200, null=True)
    item = models.ForeignKey(
        PlaidItem, on_delete=models.CASCADE, default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.type} {self.user} {self.official_name}"

    class Meta:
        verbose_name = "Plaid Account"
        verbose_name_plural = "Plaid Accounts"

        ordering = ['item__id']


class Transaction(models.Model):
    """model class for plaid transaction"""
    transaction_id = models.CharField(max_length=50)
    account = models.ForeignKey(Account, on_delete=models.CASCADE,)
    category_id = models.CharField(max_length=25)
    item = models.ForeignKey(PlaidItem, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=25)
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    iso_currency_code = models.CharField(max_length=10, null=True, blank=True)
    unofficial_currency_code = models.CharField(
        max_length=20, blank=True, null=True
    )
    date = models.DateField()
    authorized_date = models.DateField(null=True, blank=True)
    payment_channel = models.CharField(max_length=50)
    pending = models.BooleanField()
    pending_transaction_id = models.CharField(
        max_length=50, null=True, blank=True
    )
    account_owner = models.CharField(max_length=100, blank=True, null=True)
    transaction_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.name}, {self.transaction_type}"
