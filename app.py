import os
import re
from decimal import Decimal

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from mysql.connector import Error

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "local-blockchain-explorer-key")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "blockchain_explorer"),
}


def query(sql, params=(), one=False):
    connection = mysql.connector.connect(**DB_CONFIG)
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return rows[0] if one and rows else (None if one else rows)
    finally:
        connection.close()


def format_value(value, places=4):
    if value is None:
        return "0"
    try:
        value = Decimal(str(value))
        rendered = f"{value:,.{places}f}"
        return rendered.rstrip("0").rstrip(".") if places else rendered
    except Exception:
        return str(value)


@app.context_processor
def template_helpers():
    return {"fmt": format_value, "short_hash": lambda v, n=12: f"{v[:n]}…{v[-6:]}" if v and len(v) > n + 6 else v}


@app.errorhandler(Error)
def database_error(error):
    app.logger.exception("Database operation failed")
    return render_template("error.html", error=str(error)), 503


@app.route("/")
def dashboard():
    stats = query("""
        SELECT (SELECT COUNT(*) FROM block) AS blocks,
               (SELECT COUNT(*) FROM blockchain_transaction) AS transactions,
               (SELECT COUNT(*) FROM address) AS addresses,
               (SELECT COUNT(*) FROM token_transfer) AS transfers
    """, one=True)
    statuses = query("SELECT status, COUNT(*) AS total FROM blockchain_transaction GROUP BY status")
    latest_blocks = query("SELECT * FROM block ORDER BY block_number DESC LIMIT 5")
    latest_transactions = query("""
        SELECT tx_hash, amount, status, timestamp, block_number, from_address, to_address
        FROM blockchain_transaction ORDER BY timestamp DESC LIMIT 7
    """)
    activity = query("""
        SELECT DATE(timestamp) AS day, COUNT(*) AS total
        FROM blockchain_transaction GROUP BY DATE(timestamp) ORDER BY day DESC LIMIT 7
    """)
    activity.reverse()
    max_activity = max((int(row["total"]) for row in activity), default=1)
    return render_template("dashboard.html", stats=stats, statuses=statuses,
                           latest_blocks=latest_blocks, latest_transactions=latest_transactions,
                           activity=activity, max_activity=max_activity)


@app.route("/search")
def search():
    term = request.args.get("q", "").strip()
    if not term:
        return redirect(url_for("dashboard"))
    if term.isdigit():
        block = query("SELECT block_number FROM block WHERE block_number = %s", (term,), one=True)
        if block:
            return redirect(url_for("block_detail", number=block["block_number"]))
    if re.fullmatch(r"0x[0-9a-fA-F]{40}", term):
        address = query("SELECT address FROM address WHERE address = %s", (term,), one=True)
        if address:
            return redirect(url_for("address_detail", address=term))
    tx = query("SELECT tx_hash FROM blockchain_transaction WHERE tx_hash = %s", (term,), one=True)
    if tx:
        return redirect(url_for("transaction_detail", tx_hash=term))
    block = query("SELECT block_number FROM block WHERE block_hash = %s", (term,), one=True)
    if block:
        return redirect(url_for("block_detail", number=block["block_number"]))
    return render_template("search.html", term=term, results={
        "transactions": query("SELECT tx_hash, amount, status, timestamp, block_number FROM blockchain_transaction WHERE tx_hash LIKE %s ORDER BY timestamp DESC LIMIT 20", (f"%{term}%",)),
        "blocks": query("SELECT block_number, block_hash, timestamp, transaction_count FROM block WHERE CAST(block_number AS CHAR) LIKE %s OR block_hash LIKE %s ORDER BY block_number DESC LIMIT 20", (f"%{term}%", f"%{term}%")),
        "addresses": query("SELECT address, address_type, current_balance FROM address WHERE address LIKE %s LIMIT 20", (f"%{term}%",)),
    })


@app.route("/transactions")
def transactions():
    status = request.args.get("status", "")
    term = request.args.get("q", "").strip()
    where, params = [], []
    if status in {"Success", "Failed", "Pending"}:
        where.append("t.status = %s")
        params.append(status)
    if term:
        where.append("(t.tx_hash LIKE %s OR t.from_address LIKE %s OR t.to_address LIKE %s OR CAST(t.block_number AS CHAR) LIKE %s)")
        params.extend([f"%{term}%"] * 4)
    clause = " WHERE " + " AND ".join(where) if where else ""
    rows = query("SELECT t.*, b.block_hash FROM blockchain_transaction t JOIN block b ON b.block_number=t.block_number" + clause + " ORDER BY t.timestamp DESC LIMIT 100", tuple(params))
    return render_template("transactions.html", rows=rows, status=status, term=term)


@app.route("/transactions/<tx_hash>")
def transaction_detail(tx_hash):
    row = query("""
        SELECT t.*, b.block_hash, b.transaction_count, b.gas_used
        FROM blockchain_transaction t JOIN block b ON b.block_number=t.block_number
        WHERE t.tx_hash=%s
    """, (tx_hash,), one=True)
    if not row:
        abort(404)
    transfers = query("SELECT * FROM token_transfer WHERE tx_hash=%s ORDER BY transfer_id", (tx_hash,))
    return render_template("transaction_detail.html", tx=row, transfers=transfers)


@app.route("/blocks")
def blocks():
    term = request.args.get("q", "").strip()
    if term:
        rows = query("SELECT * FROM block WHERE CAST(block_number AS CHAR) LIKE %s OR block_hash LIKE %s ORDER BY block_number DESC LIMIT 100", (f"%{term}%", f"%{term}%"))
    else:
        rows = query("SELECT * FROM block ORDER BY block_number DESC LIMIT 100")
    return render_template("blocks.html", rows=rows, term=term)


@app.route("/transfers")
def transfers():
    term = request.args.get("q", "").strip()
    if term:
        match = f"%{term}%"
        rows = query("""
            SELECT tt.*, t.status FROM token_transfer tt
            JOIN blockchain_transaction t ON t.tx_hash=tt.tx_hash
            WHERE tt.token_symbol LIKE %s OR tt.tx_hash LIKE %s
               OR tt.from_address LIKE %s OR tt.to_address LIKE %s
            ORDER BY tt.timestamp DESC LIMIT 100
        """, (match, match, match, match))
    else:
        rows = query("""
            SELECT tt.*, t.status FROM token_transfer tt
            JOIN blockchain_transaction t ON t.tx_hash=tt.tx_hash
            ORDER BY tt.timestamp DESC LIMIT 100
        """)
    return render_template("transfers.html", rows=rows, term=term)


@app.route("/blocks/<int:number>")
def block_detail(number):
    block = query("SELECT * FROM block WHERE block_number=%s", (number,), one=True)
    if not block:
        abort(404)
    rows = query("SELECT * FROM blockchain_transaction WHERE block_number=%s ORDER BY timestamp", (number,))
    return render_template("block_detail.html", block=block, rows=rows)


@app.route("/addresses")
def addresses():
    term = request.args.get("q", "").strip()
    kind = request.args.get("type", "")
    where, params = [], []
    if term:
        where.append("address LIKE %s")
        params.append(f"%{term}%")
    if kind in {"EOA", "Contract"}:
        where.append("address_type=%s")
        params.append(kind)
    clause = " WHERE " + " AND ".join(where) if where else ""
    rows = query("SELECT a.*, (SELECT COUNT(*) FROM blockchain_transaction t WHERE t.from_address=a.address OR t.to_address=a.address) AS transaction_count FROM address a" + clause + " ORDER BY current_balance DESC LIMIT 100", tuple(params))
    return render_template("addresses.html", rows=rows, term=term, kind=kind)


@app.route("/addresses/<path:address>")
def address_detail(address):
    wallet = query("SELECT * FROM address WHERE address=%s", (address,), one=True)
    if not wallet:
        abort(404)
    txs = query("SELECT * FROM blockchain_transaction WHERE from_address=%s OR to_address=%s ORDER BY timestamp DESC", (address, address))
    transfers = query("SELECT * FROM token_transfer WHERE from_address=%s OR to_address=%s ORDER BY timestamp DESC", (address, address))
    lists = query("SELECT w.watchlist_id, w.name FROM watchlist w JOIN watchlist_address wa ON wa.watchlist_id=w.watchlist_id WHERE wa.address=%s ORDER BY w.name", (address,))
    return render_template("address_detail.html", wallet=wallet, txs=txs, transfers=transfers, lists=lists)


@app.route("/watchlists")
def watchlists():
    user_id = request.args.get("user_id", type=int) or 1
    users = query("SELECT user_id, name FROM users ORDER BY name")
    lists = query("""
        SELECT w.watchlist_id, w.name, w.created_at, u.name AS owner,
               COUNT(wa.address) AS address_count
        FROM watchlist w JOIN users u ON u.user_id=w.user_id
        LEFT JOIN watchlist_address wa ON wa.watchlist_id=w.watchlist_id
        WHERE w.user_id=%s GROUP BY w.watchlist_id, w.name, w.created_at, u.name
        ORDER BY w.created_at DESC
    """, (user_id,))
    for item in lists:
        item["addresses"] = query("SELECT address FROM watchlist_address WHERE watchlist_id=%s ORDER BY added_at DESC", (item["watchlist_id"],))
    return render_template("watchlists.html", lists=lists, users=users, user_id=user_id)


@app.post("/watchlists/create")
def create_watchlist():
    name = request.form.get("name", "").strip()
    user_id = request.form.get("user_id", type=int)
    if not name or not user_id:
        flash("Enter a watchlist name and choose an owner.", "error")
    else:
        connection = mysql.connector.connect(**DB_CONFIG)
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO watchlist (name, user_id) VALUES (%s, %s)", (name, user_id))
            connection.commit()
            flash("Watchlist created.", "success")
        finally:
            connection.close()
    return redirect(url_for("watchlists", user_id=user_id or 1))


@app.post("/watchlists/<int:list_id>/addresses")
def add_watchlist_address(list_id):
    address = request.form.get("address", "").strip()
    user_id = request.form.get("user_id", type=int) or 1
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO watchlist_address (watchlist_id, address) VALUES (%s, %s)", (list_id, address))
            connection.commit()
            flash("Address added to watchlist.", "success")
        finally:
            connection.close()
    except Error as error:
        flash(f"Could not add address: {error.msg}", "error")
    return redirect(url_for("watchlists", user_id=user_id))


@app.post("/watchlists/<int:list_id>/addresses/remove")
def remove_watchlist_address(list_id):
    address = request.form.get("address", "").strip()
    user_id = request.form.get("user_id", type=int) or 1
    connection = mysql.connector.connect(**DB_CONFIG)
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM watchlist_address WHERE watchlist_id=%s AND address=%s", (list_id, address))
        connection.commit()
        flash("Address removed from watchlist.", "success")
    finally:
        connection.close()
    return redirect(url_for("watchlists", user_id=user_id))


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
