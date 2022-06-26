from django.urls import path
from .views import GetInstitutions, WebhookTest, WebhookTransactions, home, CreatePublicToken, CreateAccessToken, TransactionListView, AccountListView

urlpatterns = [
    path('', home),

    path('get-institutions/', GetInstitutions.as_view()),

    path('get-public-token/', CreatePublicToken.as_view()),
    path('get-access-token/', CreateAccessToken.as_view()),
    path('get-accounts/', AccountListView.as_view()),
    path('get-transactions/', TransactionListView.as_view()),

    path('webhook-test/', WebhookTest.as_view()),
    path('webhook-transactions/', WebhookTransactions.as_view()),
]
