# plaid_finance
[![Windows](https://badgen.net/badge/icon/windows?icon=windows&label)](https://microsoft.com/windows/)  [![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/) ![django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) 
![Terminal](https://badgen.net/badge/icon/terminal?icon=terminal&label) ![SQLITE](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)  ![Celery](https://a11ybadges.com/badge?logo=celery)  ![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?&style=for-the-badge&logo=redis&logoColor=white)  ![ngrok](https://a11ybadges.com/badge?logo=ngrok)
### Plaid API with DjangoREST and celery

`sqlite` Database  

`celery` handles async tasks  

`redis` message broker  

localhost exposed via `ngrok`  

## Signup, Login and Logout API endpoints

- `auth/users/` - Create user using username, email, password, first_name and last_name.
- `auth/jwt/create/` - Login with username and password. Returns a `refresh_token` and `access_token`, use the `access_token` in the header with the prefix `JWT`, use refresh_token when access_token expires.  
- `auth/users/me/` - Returns a User profile.  
- Logout by removing access_token from header.

## Plaid API authentication endpoints

- `get-public-key` - posts a `institution_id` and `webhook` and generates a `public-key`
- `get-access-key` - exchanges a `public-key` with `access-key`

## Fetch API endpoints

- `get-institutions` - Get all institution_ids and names
- `get-accounts/` - Get all accounts fetched from Plaid and stored in db
- `get-transactions/` - Get all transactions fetched from Plaid and stored in db

## Webhooks

- `webhook-test/` - fires a test sandbox webhook
- `webhook-transactions/` - Transactions webhook

# Setup

## Creating and activating virtualenv
```
git clone https://github.com/AlokPratapSingh22/plaid_finance.git
cd plaid_finance
# create a virtual env
python -m virtualenv venv
venv/Scripts/activate
pip install -r requirements.txt
```

## Environment variables

create a `.env` file with the following template
```
PLAID_CLIENT_ID=<client id from plaid API dashboard>
PLAID_SECRET=<sandbox secret from plaid API dashboard>
PLAID_ENV=Sandbox
PLAID_PRODUCTS=transactions
PLAID_COUNTRY_CODES=US
PLAID_REDIRECT_URI=http://localhost:3000/
```

## start local server

`python manage.py makemigrations`

`python manage.py migrate`  

`python manage.py runserver`

## NGROK setup

NGROK start
`ngrok http 8000`
![image](https://user-images.githubusercontent.com/60225218/175806184-c372c1bc-6beb-4e87-9bae-ce2675fa13d3.png)
Paste the copied-ID from created ngrok server at into `NGROKID` in `settings.py` file 
![image](https://user-images.githubusercontent.com/60225218/175806239-ef2a9e42-a336-4453-a98b-12af8e919fef.png)


## celery setup

Start the redis server  
`docker run -d -p 6379:6379 redis`

Start celery worker (redis should be running)
`celery -A bright worker -l info -P gevent`

DONE

# WORKINGS

### Start localserver
`python manage.py runserver`

### Start redis server
`docker run -d -p 6379:6379 redis`

### Start ngrok
`ngrok http 8000`  

Paste into NGROKID  

![image](https://user-images.githubusercontent.com/60225218/175808965-fed4c4da-ec28-4fee-b7bd-f2966a34bf0b.png)

### Start celery worker
`celery -A bright worker -l INFO -p gevent`
---
## ENDPOINTS
### endpoint `/`
Start page
![image](https://user-images.githubusercontent.com/60225218/175807971-f3e5b378-0a81-41ce-bb23-dd3730657c89.png)

## Authentication endpoints

### Signup - endpoint `/auth/users/`
![image](https://user-images.githubusercontent.com/60225218/175808023-48e61a42-48f2-451f-b227-de48512407cd.png)
![image](https://user-images.githubusercontent.com/60225218/175808052-117d9f7c-4726-4029-b5b5-5b6f02aac54b.png)
![image](https://user-images.githubusercontent.com/60225218/175808062-d2043d57-399c-4ee2-97b4-7acc06f7cedf.png)

### Login - endpoint `/auth/jwt/create/`
![image](https://user-images.githubusercontent.com/60225218/175808107-46da8cd0-59e3-4c41-b1fe-6d222f9df602.png)

__Copy the access token__

#### Use [MOD HEADER](https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj) Browser Extension for adding `access_token` to header
![image](https://user-images.githubusercontent.com/60225218/175808201-f28a9320-0ea5-4240-b14d-959a0d7967ff.png)
![image](https://user-images.githubusercontent.com/60225218/175808367-0278a794-277a-42be-bfed-ec154dd06e19.png)

### User profile view and update - endpoint `/auth/users/me/`
![image](https://user-images.githubusercontent.com/60225218/175808431-534d92a8-d450-469e-86c6-6629dfb94e5a.png)

## Plaid related APIs

### Institutions - endpoint '/get-institutions/' (No Authentication Required)
![image](https://user-images.githubusercontent.com/60225218/175808503-639dcd4b-2460-44c6-8464-4a665a395157.png)

### Plaid Public Token - endpoint `/get-public-token/`

_takes in a institution_id_

![image](https://user-images.githubusercontent.com/60225218/175808589-0cb89741-d5b2-44fd-8eff-a4339e1530ed.png)

![image](https://user-images.githubusercontent.com/60225218/175808625-78eeee1d-f44d-4098-bb34-a7ae18659802.png)

> __COPY THIS public_token for next step__  

> webhook attached

### Plaid Access Token - endpoint `/get-access-token/`

_takes in public_token_

![image](https://user-images.githubusercontent.com/60225218/175808715-b6df569d-e6c6-4421-b3a6-90c96c10d0ae.png)

> triggers an async function to fetch accounts from plaidAPI  

> transaction fetch triggered by webhooks  

> celery logs  

> ![image](https://user-images.githubusercontent.com/60225218/175808775-dc2e6b67-48e1-43f6-af00-d959e649fc63.png)

### List Accounts - endpoint `/get-accounts/`
![image](https://user-images.githubusercontent.com/60225218/175808870-abed46e5-99c0-4d40-8b56-605d3c6bc836.png)

### List Transactions - endpoint `/get-transactions/`
![image](https://user-images.githubusercontent.com/60225218/175808893-26a5d362-13b5-42ae-b17a-5ce7c139d7d9.png)




