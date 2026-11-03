# ChainScope

ChainScope is a small Flask and MySQL blockchain explorer for the `blockchain_explorer` schema in `blockchain_explorer_backup.sql`.

## Features

- Overview cards, transaction activity, recent blocks, and latest transactions
- Search by transaction hash, block number or hash, and wallet address
- Filterable transaction, block, wallet, and token transfer tables
- Transaction, block, and wallet detail pages with linked records
- Create watchlists, add or remove addresses, and switch between the seeded users
- Parameterized SQL queries using the schema's existing MySQL tables

## Run locally

1. Install MySQL 8 and make sure the MySQL server is running.
2. Import the supplied schema and sample data from this folder:

   ```powershell
   mysql -u root -p < blockchain_explorer_backup.sql
   ```

   The backup creates and selects the `blockchain_explorer` database.
3. Create and activate a virtual environment, then install dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and set your MySQL password and a Flask secret:

   ```powershell
   Copy-Item .env.example .env
   ```

5. Start the app and open `http://127.0.0.1:5000`:

   ```powershell
   python app.py
   ```

The default database settings use `localhost:3306`, user `root`, and database `blockchain_explorer`. The app does not define passwords for the seeded project users; the user selector on the Watchlists page chooses which existing user's lists to manage.

## Project structure

```text
app.py                 Flask routes and MySQL queries
templates/             Jinja pages
static/style.css       Responsive explorer styles
blockchain_explorer_backup.sql  Schema and sample records
```
