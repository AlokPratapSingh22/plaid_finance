# Generated by Django 4.0.5 on 2022-06-25 21:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_id', models.CharField(max_length=200, null=True, unique=True)),
                ('curr_balance', models.FloatField(null=True)),
                ('available_balance', models.FloatField(null=True)),
                ('name', models.CharField(max_length=200, null=True)),
                ('mask', models.CharField(max_length=200, null=True)),
                ('subtype', models.CharField(max_length=200, null=True)),
                ('type', models.CharField(max_length=200, null=True)),
                ('official_name', models.CharField(max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'Plaid Account',
                'verbose_name_plural': 'Plaid Accounts',
                'ordering': ['item__id'],
            },
        ),
        migrations.CreateModel(
            name='PlaidItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(max_length=200, unique=True)),
                ('item_id', models.CharField(max_length=200, unique=True)),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(max_length=50)),
                ('category_id', models.CharField(max_length=25)),
                ('transaction_type', models.CharField(max_length=25)),
                ('name', models.CharField(max_length=200)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('iso_currency_code', models.CharField(blank=True, max_length=10, null=True)),
                ('unofficial_currency_code', models.CharField(blank=True, max_length=20, null=True)),
                ('date', models.DateField()),
                ('authorized_date', models.DateField(blank=True, null=True)),
                ('payment_channel', models.CharField(max_length=50)),
                ('pending', models.BooleanField()),
                ('pending_transaction_id', models.CharField(blank=True, max_length=50, null=True)),
                ('account_owner', models.CharField(blank=True, max_length=100, null=True)),
                ('transaction_code', models.CharField(blank=True, max_length=50, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='financeapp.account')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='financeapp.plaiditem')),
            ],
            options={
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
                'ordering': ['-date'],
            },
        ),
        migrations.AddField(
            model_name='account',
            name='item',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='financeapp.plaiditem'),
        ),
        migrations.AddField(
            model_name='account',
            name='user',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
