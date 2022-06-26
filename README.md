# plaid_finance
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

### endpoint '/'
Start page
![image](https://user-images.githubusercontent.com/60225218/175807971-f3e5b378-0a81-41ce-bb23-dd3730657c89.png)

## Authentication endpoints

### Signup - endpoint '/auth/users/'
![image](https://user-images.githubusercontent.com/60225218/175808023-48e61a42-48f2-451f-b227-de48512407cd.png)
![image](https://user-images.githubusercontent.com/60225218/175808052-117d9f7c-4726-4029-b5b5-5b6f02aac54b.png)
![image](https://user-images.githubusercontent.com/60225218/175808062-d2043d57-399c-4ee2-97b4-7acc06f7cedf.png)

### Login - endpoint '/auth/jwt/create/'
![image](https://user-images.githubusercontent.com/60225218/175808107-46da8cd0-59e3-4c41-b1fe-6d222f9df602.png)

__Copy the access token__

#### Use [MOD HEADER](https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj) Browser Extension for adding `access_token` to header
![image](https://user-images.githubusercontent.com/60225218/175808201-f28a9320-0ea5-4240-b14d-959a0d7967ff.png)
