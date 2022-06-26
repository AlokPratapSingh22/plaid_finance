"""creates and returns a plaid-client instance"""

import os
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from .utils import PLAID_ENVIRON

# Loading from .env file
load_dotenv()


class Plaid_Client:
    """
        return an instance of client if already present,  
        else creates one and returns it
    """
    __instance = None

    @staticmethod
    def getInstance():
        if Plaid_Client.__instance == None:
            Plaid_Client()
        return Plaid_Client.__instance

    def __init__(self) -> None:
        if Plaid_Client.__instance != None:
            raise Exception("Singleton class")
        else:

            config = plaid.Configuration(
                host=PLAID_ENVIRON[os.environ.get('PLAID_ENV')],
                api_key={
                    'clientId': os.environ.get('PLAID_CLIENT_ID'),
                    'secret': os.environ.get('PLAID_SECRET')
                }
            )

            api_client = plaid.ApiClient(configuration=config)
            client = plaid_api.PlaidApi(api_client)

            Plaid_Client.__instance = client
