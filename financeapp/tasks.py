"""tasks handled by celery"""

import json
import structlog

from django.conf import settings
from datetime import datetime, timedelta
from celery import shared_task
from plaid import ApiException
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from django.contrib.auth import get_user_model

from .models import Account, PlaidItem, Transaction
from .plaid_client import Plaid_Client

logger = structlog.get_logger('celery')

User = get_user_model()

client = Plaid_Client.getInstance()


@shared_task(bind=True, max_retries=3)
def fetch_accounts_data(self, user_id, itemid):
    """
        fetches accounts belonging to item and stores in db
    """
    user = User.objects.get(id=user_id)

    try:
        item = PlaidItem.objects.get(item_id=itemid)

        request = AccountsGetRequest(access_token=item.access_token)
        response = client.accounts_get(request)
        accounts = response['accounts']

        for account in accounts:

            try:
                acc_obj = Account.objects.get(account_id=account['account_id'])

            except Account.DoesNotExist:
                acc_obj = Account(
                    user=user,
                    item=item,
                    account_id=account['account_id'],
                    mask=account["mask"],
                    name=account["name"],
                    official_name=account["official_name"],
                    type=account.get("type", None),
                    subtype=account.get("subtype", None),
                    curr_balance=account["balances"].get("current", None),
                    available_balance=account["balances"].get(
                        "available", None) if account["balances"] else None
                )
                acc_obj.save()

        logger.info(
            "fetch_accounts_data success",
            # fetch_accounts="success",
            # status="202",
        )
        return "Fetch account data success"

    except PlaidItem.DoesNotExist as exi:
        raise self.retry(exc=exi, countdown=5)
    except ApiException as err:
        logger.info(
            err.status,
            token_exchange='fail',
            # request_id=err.body['request_id']
        )

        raise self.retry(countdown=60*5, exc=err)
    except Exception as e:
        logger.info(
            "Failed to save",
            error=e
        )


@shared_task(bind=True, max_retries=5)
def store_transactions_in_db(self, itemid):
    """
    Fetches different accounts transactions and stores in db
    Making separate calls for different accounts can reduce time running this task
    """

    try:
        item = PlaidItem.objects.get(item_id=itemid)

        start_date = datetime.date(datetime.now()-timedelta(days=30))
        end_date = datetime.date(datetime.now())

        getTransactionsReq = TransactionsGetRequest(
            access_token=item.access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions()
        )

        response = client.transactions_get(getTransactionsReq)
        logger.info(response["total_transactions"])
        transactions = response['transactions']

        for transaction in transactions:
            try:
                account_obj = Account.objects.get(
                    account_id=transaction["account_id"])
                try:
                    obj = Transaction.objects.get(
                        transaction_id=transaction['transaction_id'])

                    Transaction.objects.filter(

                        transaction_id=transaction["transaction_id"]).update(
                            amount=transaction['amount'],
                            item=item,
                        date=transaction['date'],
                        name=transaction['name'],
                        payment_channel=transaction['payment_channel']
                    )
                except Transaction.DoesNotExist:
                    trans_obj = Transaction(
                        account=account_obj,
                        item=item,
                        transaction_id=transaction["transaction_id"],
                        category_id=transaction.get("category_id", None),
                        transaction_type=transaction.get(
                            "transaction_type", None),
                        name=transaction["name"],
                        amount=transaction["amount"],
                        iso_currency_code=transaction.get(
                            "iso_currency_code", None),
                        unofficial_currency_code=transaction.get(
                            "unofficial_currency_code", None),
                        date=transaction["date"],
                        authorized_date=transaction.get(
                            "authorized_date", None),
                        payment_channel=transaction["payment_channel"],
                        pending=transaction["pending"],
                        pending_transaction_id=transaction.get(
                            "pending_transaction_id", None),
                        account_owner=transaction.get("account_owner", None),
                        transaction_code=transaction.get(
                            "transaction_code", None),
                    )
                    trans_obj.save()
            except Account.DoesNotExist as er:
                logger.info("accounts not created. Retrying")
                raise self.retry(countdown=10, exc=er)
    except PlaidItem.DoesNotExist as exc:
        logger.info("plaidItem not created. Retrying")
        raise self.retry(countdown=10, exc=exc)
    except ApiException as err:
        e = json.loads(err.body)
        if e.code == "PRODUCT_NOT_READY":
            logger.info("fetch_transaction failed",
                        token_exchange="fail",
                        error_type=e.type,
                        error_code=e.code,
                        plaid_request_id=e.request_id
                        )
            raise self.self.retry(countdown=60*4, exc=exc)
        logger.info(
            token_exchange='failed to fetch transactions',
            plaid_request_id=response['request_id'],
            message=e,
        )

        raise self.retry(countdown=60*5, exc=err)
    except Exception as exc:
        logger.info(f"{exc} outer")


@shared_task(bind=True, max_retries=2)
def delete_transactions_from_db(self, item_id, removed_transactions):
    """remove transaction from database"""
    for transaction in removed_transactions:
        try:
            Transaction.objects.filter(
                transaction_id=transaction.transaction_id).delete()

        except Transaction.DoesNotExist:
            logger.info("transaction object does not exist", status="fail")
            raise self.retry(countdown=5)
    logger.log("transaction deleted", status="success")
    return "Transactions deleted"
