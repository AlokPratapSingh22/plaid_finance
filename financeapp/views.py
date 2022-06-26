"""views related to our finance_app"""

import json
import structlog

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from plaid import ApiException

from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.sandbox_public_token_create_request_options import SandboxPublicTokenCreateRequestOptions
from plaid.model.sandbox_item_fire_webhook_request import SandboxItemFireWebhookRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.institutions_get_request import InstitutionsGetRequest

from .tasks import delete_transactions_from_db, fetch_accounts_data, store_transactions_in_db
from .models import Account, Institution, PlaidItem, Transaction
from .serializers import AccountSerializer, InstitutionSeriralizer, TransactionsSerializer
from .plaid_client import Plaid_Client

from bright.settings import NGROKID

# get an instance of item
client = Plaid_Client.getInstance()

# write logs into your terminal
plaid_logger = structlog.get_logger('plaid')
celery_logger = structlog.get_logger('celery')


@ api_view()
def home(request):
    return Response('A finance app djangoRestApi using plaid Api')


class GetInstitutions(ListAPIView):
    """gets a list of institutions with ids and names"""
    serializer_class = InstitutionSeriralizer

    def get_queryset(self):

        qs = Institution.objects.all()

        if not qs.exists():
            request = InstitutionsGetRequest(
                country_codes=[CountryCode('US')],
                count=500,
                offset=0,
            )
            response = client.institutions_get(request)
            institutions = response['institutions']
            for inst in institutions:
                inst_obj = Institution(
                    institution_id=inst['institution_id'],
                    name=inst['name'],
                )
                inst_obj.save()

            qs = Institution.objects.all()

        return qs


class CreatePublicToken(APIView):
    """
        takes an `institution id` and creates a `plaid public-token`.  

        also, attaches the webhook by passing it as an argument
    """
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request):
        # ins_109512 - Houndstooth Bank
        # ins_1 - Bank of America
        try:
            institution_id = request.data['institution_id']
            try:
                pt_request = SandboxPublicTokenCreateRequest(
                    institution_id=institution_id,
                    initial_products=[Products('transactions')],
                    options=SandboxPublicTokenCreateRequestOptions(
                        webhook="https://"+NGROKID+".ngrok.io/webhook-transactions/")
                )

                res = client.sandbox_public_token_create(pt_request)

                public_token = res['public_token']

                data = {
                    'public_token': public_token
                }

                plaid_logger.info(
                    "public-token creation success",
                    plaid_request_id=res['request_id'],
                    token_exchange="success"
                )

                return Response(data, status=status.HTTP_201_CREATED)
            except ApiException as exc:
                err = json.loads(exc.body)

                plaid_logger.info(
                    "public token creation fail",
                    error=err,
                    token_exchange="fail",
                )
                data = {
                    "status": exc.status,
                    "message": err,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)


class CreateAccessToken(APIView):
    """
        takes in plaid public-token and exchanges it with a access token, 
        and creates a plaid item. 
        Later accounts are fetched in the background using celery
    """
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request):

        try:
            public_token = request.data['public_token']
            try:

                exchangeRequest = ItemPublicTokenExchangeRequest(
                    public_token=public_token
                )

                response = client.item_public_token_exchange(exchangeRequest)
                # {
                #   Output Format
                #   'access_token': '------------',
                #   'item_id': '------'',
                #   'request_id': '------'
                # }

                plaid_logger.info(
                    "public-token exchange success",
                    plaid_request_id=response['request_id'],
                    token_exchange="success"
                )
            except ApiException as e:
                # ToDo: More through error handling
                plaid_logger.info(
                    "public token exchange fail",
                    public_token=public_token,
                    token_exchange="fail",
                )
                err = json.loads(e.body)
                data = {
                    "status": e.status,
                    "message": err,
                }
                return Response(data, status=400)

            # exchange success
            access_token = response['access_token']
            item_id = response['item_id']

            # Using item_id to create or retreive created PlaidItem
            try:
                item = PlaidItem.objects.get(item_id=item_id)
                msg = 'Item already exists'

            except PlaidItem.DoesNotExist:
                # If item not existent creating a new PlaidItem
                item = PlaidItem.objects.create(
                    user=self.request.user, item_id=item_id, access_token=access_token)
                item.save()
                msg = 'Item created'

            try:
                # async task to fetch accounts
                fetch_accounts_data.apply_async(
                    args=[
                        self.request.user.id,
                        item_id
                    ]
                )

            except Exception as exc:
                celery_logger.exception('Sending task raised', exc=exc)

            data = {
                'message': f'{msg} , and fetched accounts successfuly',
                'access_token': access_token,
                'item_id': item_id,
                'request_id': response['request_id'],
            }

            return Response(data, status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AccountListView(ListAPIView):
    """
        returns a list of accounts related to the current logged in user
    """
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    http_method_names = ['get']
    serializer_class = AccountSerializer

    def get_queryset(self):

        account_qs = Account.objects.filter(user_id=self.request.user.id)

        return account_qs


class TransactionListView(ListAPIView):
    """
        returns a list of accounts related to the current user
    """
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    pagination_class = PageNumberPagination
    serializer_class = TransactionsSerializer

    def get_queryset(self):
        items = PlaidItem.objects.filter(user_id=self.request.user.id)

        transactions_qs = Transaction.objects.filter(
            item_id=items[0].id)
        for item in items[1:]:

            transactions_qs = transactions_qs | Transaction.objects.filter(
                item_id=item.id)

        return transactions_qs


class WebhookTransactions(APIView):
    """Webhook when called upon, updates the transactions asynchrously."""
    http_method_names = ['post']

    def post(self, request):
        data = request.data

        webhook_type = data['webhook_type']
        webhook_code = data['webhook_code']

        celery_logger.info(
            f"{webhook_type} type hook recieved. {webhook_code}")

        if webhook_type == "TRANSACTIONS":
            item_id = data['item_id']

            if webhook_code == "TRANSACTION_REMOVED":
                removed_transactions = data['removed_transactions']
                try:
                    delete_transactions_from_db.apply_async(
                        args=[
                            item_id,
                            removed_transactions,
                        ]
                    )
                except Exception as exc:
                    celery_logger.info(str(exc))

            else:
                new_transaction = data.get(
                    "new_transactions") if "new_transactions" in data else 0
                plaid_logger.info(
                    f"{new_transaction} New transactions available")

                try:
                    store_transactions_in_db.apply_async(
                        args=[
                            item_id
                        ],
                        countdown=10
                    )
                except Exception as exc:
                    celery_logger.info(str(exc))
            return Response({"message": "Webhook recieved"}, status=status.HTTP_202_ACCEPTED)


class WebhookTest(APIView):
    """Test if webhook is connected"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            item = PlaidItem.objects.filter(user=self.request.user)
            access_token = item[0].access_token

            # fire a DEFAULT_UPDATE webhook for an item
            req = SandboxItemFireWebhookRequest(
                access_token=access_token,
                webhook_code='DEFAULT_UPDATE'
            )
            response = client.sandbox_item_fire_webhook(req)

            print("Webhook fired: ", response['webhook_fired'])

            return Response({"message": "Webhook fired"}, status=status.HTTP_200_OK)
        except ApiException as e:
            err = json.loads(e.body)
            plaid_logger.info("api problem", error=err)

            return Response(err, status=status.HTTP_417_EXPECTATION_FAILED)
