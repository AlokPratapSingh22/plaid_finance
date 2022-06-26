# plaid_finance
### Plaid API with DjangoREST and celery

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

```
git clone https://github.com/AlokPratapSingh22/plaid_finance.git
cd plaid_finance
# create a virtual env
python -m virtualenv venv
venv/Scripts/activate
pip install -r requirements.txt
```

create a `.env` file with the following template
```
PLAID_CLIENT_ID=<client id from plaid API dashboard>
PLAID_SECRET=<sandbox secret from plaid API dashboard>
PLAID_ENV=Sandbox
PLAID_PRODUCTS=transactions
PLAID_COUNTRY_CODES=US
PLAID_REDIRECT_URI=http://localhost:3000/
```

`python manage.py makemigrations`

`python manage.py migrate`
