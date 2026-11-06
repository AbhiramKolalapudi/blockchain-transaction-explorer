# ChainScope

ChainScope is a Flask blockchain explorer that uses MySQL for relational blockchain data and MongoDB for flexible wallet activity and smart contract event documents. It expects the existing `blockchain_explorer` schema to be available in MySQL.

## Features

- Overview cards, transaction activity, recent blocks, and latest transactions
- Search by transaction hash, block number or hash, and wallet address
- Filterable transaction, block, wallet, and token transfer tables
- Add transactions through the app; MySQL enforces valid amount and gas-fee values
- Transaction, block, and wallet detail pages with linked records
- Create watchlists, add or remove addresses, and switch between the seeded users
- Import MySQL transaction and token-transfer history into MongoDB, then create, read, edit, filter, and delete wallet activity documents
- Create, search, inspect as JSON, edit, and delete smart contract event documents
- Parameterized SQL queries using the schema's existing MySQL tables

## Run locally

1. Install MySQL 8 and MongoDB Community Server. Start both database services.
2. Create or import the `blockchain_explorer` database using your course schema materials. The schema file is not included in this repository. If using the MySQL command-line client, connect from PowerShell:

   ```powershell
   mysql -u root -p
   ```

   If `mysql` is not on PATH, launch `mysql.exe` using its full install path. Import your schema from the MySQL prompt or MySQL Workbench before starting the app.
3. Create and activate a virtual environment, then install Flask, the MySQL connector, and PyMongo:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and set your MySQL password, MongoDB URI, database name, and a Flask secret:

   ```powershell
   Copy-Item .env.example .env
   ```

5. Start the app and open `http://127.0.0.1:5000`:

   ```powershell
   python app.py
   ```

MySQL defaults to `localhost:3306`, user `root`, and database `blockchain_explorer`. MongoDB defaults to `mongodb://localhost:27017` and database `blockchain_explorer`; its `wallet_activity` and `transaction_events` collections and indexes are created automatically the first time their pages are opened. The app does not define passwords for the seeded project users; the user selector on the Watchlists page chooses which existing user's lists to manage.

The Wallet Activity page can import a selected wallet's MySQL transactions and token transfers into MongoDB. Imported records are inserted only once per source transaction/transfer; manual activity documents can also be created, edited, and deleted. The Event Explorer stores flexible JSON objects in `event_data` for Transfer, Approval, and custom event logs.

## Project structure

```text
app.py                 Flask routes, MySQL queries, and MongoDB CRUD
templates/             Jinja pages and forms
static/style.css       Responsive explorer styles
```
