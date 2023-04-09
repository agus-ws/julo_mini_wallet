## JULO Mini Wallet API

Case Study: [link](https://documenter.getpostman.com/view/8411283/SVfMSqA3?version=latest).


API Docs:


Notes:
- All ids must be in UUID format(based on API docs), prefer to use postgres UUID data type instead of VARCHAR.
- API Docs is not provided but all endpoints should reflect the study case example.


Requirements (Tested on):
- Docker v23
- Docker compose v1.27

How to run the app:
1. `docker-compose up`

Endpoints:
- `http://127.0.0.1:8000/api/v1/init` [POST]
- `http://127.0.0.1:8000/api/v1/wallet` [POST, GET, PATCH]
- `http://127.0.0.1:8000/api/v1/wallet/transactions` [GET]
- `http://127.0.0.1:8000/api/v1/wallet/deposits` [POST]
- `http://127.0.0.1:8000/api/v1/wallet/withdrawals` [POST]
