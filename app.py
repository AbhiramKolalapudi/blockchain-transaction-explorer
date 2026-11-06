import os
import re
import json
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal

from bson import ObjectId
from bson.errors import InvalidId
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from mysql.connector import Error
from pymongo import ASCENDING, DESCENDING, MongoClient, UpdateOne
from pymongo.errors import PyMongoError

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
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "blockchain_explorer")
MONGO_TIMEOUT_MS = int(os.getenv("MONGO_TIMEOUT_MS", "2500"))
_mongo_client = None
_mongo_indexes_ready = False


def query(sql, params=(), one=False):
    connection = mysql.connector.connect(**DB_CONFIG)
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return rows[0] if one and rows else (None if one else rows)
    finally:
        connection.close()


def mongo_collection(name):
    """Get a Mongo collection and lazily create indexes for the two feature sets."""
    global _mongo_client, _mongo_indexes_ready
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=MONGO_TIMEOUT_MS)
    database = _mongo_client[MONGO_DB_NAME]
    if not _mongo_indexes_ready:
        database["wallet_activity"].create_index([("wallet_address", ASCENDING), ("timestamp", DESCENDING)])
        database["wallet_activity"].create_index([("wallet_address", ASCENDING), ("source_id", ASCENDING)], unique=True)
        database["transaction_events"].create_index([("transaction_hash", ASCENDING)])
        database["transaction_events"].create_index([("event_name", ASCENDING), ("contract_address", ASCENDING)])
        database["transaction_events"].create_index([("timestamp", DESCENDING)])
        _mongo_indexes_ready = True
    return database[name]


def parse_timestamp(value):
    if not value:
        raise ValueError("Choose a timestamp.")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("Enter a valid timestamp.") from error
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def mongo_json(document):
    """Convert BSON values to JSON-safe values for the event inspector."""
    if isinstance(document, ObjectId):
        return str(document)
    if isinstance(document, datetime):
        if document.tzinfo is None:
            document = document.replace(tzinfo=timezone.utc)
        return document.astimezone(timezone.utc).isoformat()
    if isinstance(document, dict):
        return {key: mongo_json(value) for key, value in document.items() if key != "_id"} | ({"_id": str(document["_id"])} if "_id" in document else {})
    if isinstance(document, list):
        return [mongo_json(value) for value in document]
    return document


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


@app.errorhandler(PyMongoError)
def mongo_database_error(error):
    app.logger.exception("MongoDB operation failed")
    return render_template("mongo_error.html", error=str(error)), 503


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


@app.route("/transactions/new", methods=["GET", "POST"])
def transaction_new():
    blocks = query("SELECT block_number FROM block ORDER BY block_number DESC")
    addresses = query("SELECT address FROM address ORDER BY address")
    form = request.form if request.method == "POST" else {}
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M")
    if request.method == "POST":
        trigger = query("""
            SELECT TRIGGER_NAME FROM information_schema.TRIGGERS
            WHERE TRIGGER_SCHEMA=%s AND TRIGGER_NAME=%s
        """, (DB_CONFIG["database"], "validate_transaction_amount"), one=True)
        if not trigger:
            flash("The validate_transaction_amount trigger is not installed in this MySQL database. Load the project schema first.", "error")
            return render_template("transaction_form.html", form=form, blocks=blocks, addresses=addresses, now_utc=now_utc), 409

        tx_hash = request.form.get("tx_hash", "").strip()
        status = request.form.get("status", "")
        try:
            amount = Decimal(request.form.get("amount", ""))
            gas_fee = Decimal(request.form.get("gas_fee", ""))
            block_number = int(request.form.get("block_number", ""))
            timestamp = parse_timestamp(request.form.get("timestamp", "")).replace(tzinfo=None)
            from_address = request.form.get("from_address", "")
            to_address = request.form.get("to_address", "")
            if not tx_hash or len(tx_hash) > 66:
                raise ValueError("Enter a transaction hash up to 66 characters long.")
            if not amount.is_finite() or not gas_fee.is_finite():
                raise ValueError("Amount and gas fee must be numeric values.")
            if status not in {"Success", "Failed", "Pending"}:
                raise ValueError("Choose a valid transaction status.")
            if not from_address or not to_address:
                raise ValueError("Choose both sender and receiver addresses.")
        except (ValueError, ArithmeticError) as error:
            flash(str(error) or "Enter valid transaction values.", "error")
            return render_template("transaction_form.html", form=form, blocks=blocks, addresses=addresses, now_utc=now_utc), 400

        connection = None
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            # Deliberately do not validate amount > 0 or gas_fee >= 0 here;
            # MySQL's BEFORE INSERT trigger must accept or reject these values.
            cursor.execute("""
                INSERT INTO blockchain_transaction
                    (tx_hash, amount, gas_fee, status, timestamp, block_number, from_address, to_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (tx_hash, amount, gas_fee, status, timestamp, block_number, from_address, to_address))
            connection.commit()
        except Error as error:
            if connection:
                connection.rollback()
            message = getattr(error, "msg", str(error))
            flash(f"MySQL rejected the insert: {message}", "error")
            return render_template("transaction_form.html", form=form, blocks=blocks, addresses=addresses, now_utc=now_utc), 400
        finally:
            if connection:
                connection.close()

        flash("Transaction inserted. The database trigger accepted these values.", "success")
        return redirect(url_for("transaction_detail", tx_hash=tx_hash))

    return render_template("transaction_form.html", form=form, blocks=blocks, addresses=addresses, now_utc=now_utc)


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


@app.route("/wallet-activity")
def wallet_activity():
    wallet = request.args.get("q", "").strip()
    token = request.args.get("token", "").strip()
    activity_type = request.args.get("type", "")
    direction = request.args.get("direction", "")
    filters = {}
    if wallet:
        filters["wallet_address"] = {"$regex": re.escape(wallet), "$options": "i"}
    if token:
        filters["token_symbol"] = {"$regex": re.escape(token), "$options": "i"}
    if activity_type in {"transaction", "token_transfer"}:
        filters["activity_type"] = activity_type
    if direction in {"incoming", "outgoing"}:
        filters["direction"] = direction
    rows = list(mongo_collection("wallet_activity").find(filters).sort("timestamp", DESCENDING).limit(250))
    common_addresses = Counter(row.get("interacted_address") for row in rows if row.get("interacted_address")).most_common(5)
    summary = {
        "total": len(rows),
        "incoming": sum(1 for row in rows if row.get("direction") == "incoming"),
        "outgoing": sum(1 for row in rows if row.get("direction") == "outgoing"),
        "counterparties": common_addresses,
    }
    return render_template("wallet_activity.html", rows=rows, wallet=wallet, token=token,
                           activity_type=activity_type, direction=direction, summary=summary)


@app.post("/wallet-activity/import")
def import_wallet_activity():
    wallet = request.form.get("wallet_address", "").strip()
    if not wallet:
        flash("Enter a wallet address to import its MySQL activity.", "error")
        return redirect(url_for("wallet_activity"))

    transactions = query("""
        SELECT tx_hash, amount, status, timestamp, block_number, from_address, to_address
        FROM blockchain_transaction
        WHERE from_address=%s OR to_address=%s
        ORDER BY timestamp DESC
    """, (wallet, wallet))
    token_transfers = query("""
        SELECT tt.transfer_id, tt.token_symbol, tt.amount, tt.timestamp, tt.tx_hash,
               tt.from_address, tt.to_address, t.status
        FROM token_transfer tt JOIN blockchain_transaction t ON t.tx_hash=tt.tx_hash
        WHERE tt.from_address=%s OR tt.to_address=%s
        ORDER BY tt.timestamp DESC
    """, (wallet, wallet))

    operations = []
    for row in transactions:
        outgoing = row["from_address"].lower() == wallet.lower()
        operations.append(UpdateOne(
            {"wallet_address": wallet, "source_id": f"tx:{row['tx_hash']}"},
            {"$setOnInsert": {
                "wallet_address": wallet, "direction": "outgoing" if outgoing else "incoming",
                "transaction_hash": row["tx_hash"], "source_id": f"tx:{row['tx_hash']}",
                "activity_type": "transaction", "amount": str(row["amount"]), "token_symbol": "ETH",
                "interacted_address": row["to_address"] if outgoing else row["from_address"],
                "timestamp": row["timestamp"].replace(tzinfo=timezone.utc),
                "summary": f"{'Sent' if outgoing else 'Received'} ETH · {row['status']}",
                "metadata": {"block_number": row["block_number"], "status": row["status"], "source": "mysql"},
                "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
            }}, upsert=True
        ))
    for row in token_transfers:
        outgoing = row["from_address"].lower() == wallet.lower()
        source_id = f"transfer:{row['transfer_id']}"
        operations.append(UpdateOne(
            {"wallet_address": wallet, "source_id": source_id},
            {"$setOnInsert": {
                "wallet_address": wallet, "direction": "outgoing" if outgoing else "incoming",
                "transaction_hash": row["tx_hash"], "source_id": source_id,
                "activity_type": "token_transfer", "amount": str(row["amount"]),
                "token_symbol": row["token_symbol"],
                "interacted_address": row["to_address"] if outgoing else row["from_address"],
                "timestamp": row["timestamp"].replace(tzinfo=timezone.utc),
                "summary": f"{'Sent' if outgoing else 'Received'} {row['token_symbol']} · {row['status']}",
                "metadata": {"status": row["status"], "transfer_id": row["transfer_id"], "source": "mysql"},
                "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
            }}, upsert=True
        ))
    result = mongo_collection("wallet_activity").bulk_write(operations, ordered=False) if operations else None
    imported = result.upserted_count if result else 0
    flash(f"History import complete: {imported} new MongoDB records added; existing records were kept.", "success")
    return redirect(url_for("wallet_activity", q=wallet))


@app.route("/wallet-activity/new", methods=["GET", "POST"])
def wallet_activity_new():
    return wallet_activity_form()


@app.route("/wallet-activity/<activity_id>/edit", methods=["GET", "POST"])
def wallet_activity_edit(activity_id):
    try:
        object_id = ObjectId(activity_id)
    except InvalidId:
        abort(404)
    return wallet_activity_form(object_id)


def wallet_activity_form(object_id=None):
    collection = mongo_collection("wallet_activity")
    existing = collection.find_one({"_id": object_id}) if object_id else None
    if object_id and not existing:
        abort(404)
    if request.method == "GET":
        return render_template("wallet_activity_form.html", activity=existing, editing=bool(existing))

    form = request.form
    wallet = form.get("wallet_address", "").strip()
    tx_hash = form.get("transaction_hash", "").strip()
    token = form.get("token_symbol", "").strip().upper()
    direction = form.get("direction", "")
    kind = form.get("activity_type", "")
    amount = form.get("amount", "").strip()
    interacted = form.get("interacted_address", "").strip()
    summary = form.get("summary", "").strip()
    try:
        timestamp = parse_timestamp(form.get("timestamp", ""))
        if not wallet or not tx_hash or not token or not amount:
            raise ValueError("Wallet, transaction hash, token and amount are required.")
        if direction not in {"incoming", "outgoing"}:
            raise ValueError("Choose incoming or outgoing direction.")
        if kind not in {"transaction", "token_transfer"}:
            raise ValueError("Choose a supported activity type.")
        try:
            numeric_amount = Decimal(amount)
        except Exception as error:
            raise ValueError("Amount must be a numeric value.") from error
        if not numeric_amount.is_finite() or numeric_amount < 0:
            raise ValueError("Amount must be a numeric value.")
        metadata = {"source": "manual"}
    except ValueError as error:
        flash(str(error), "error")
        activity = dict(form)
        return render_template("wallet_activity_form.html", activity=activity, editing=bool(existing)), 400

    now = datetime.now(timezone.utc)
    document = {
        "wallet_address": wallet, "direction": direction, "transaction_hash": tx_hash,
        "activity_type": kind, "amount": amount, "token_symbol": token,
        "interacted_address": interacted, "timestamp": timestamp, "summary": summary,
        "metadata": existing.get("metadata", metadata) if existing else metadata,
        "updated_at": now,
    }
    if existing:
        collection.update_one({"_id": object_id}, {"$set": document})
    else:
        document["source_id"] = f"manual:{ObjectId()}"
        document["created_at"] = now
        collection.insert_one(document)
    flash("Wallet activity saved to MongoDB.", "success")
    return redirect(url_for("wallet_activity", q=wallet))


@app.post("/wallet-activity/<activity_id>/delete")
def wallet_activity_delete(activity_id):
    try:
        object_id = ObjectId(activity_id)
    except InvalidId:
        abort(404)
    result = mongo_collection("wallet_activity").delete_one({"_id": object_id})
    if not result.deleted_count:
        abort(404)
    flash("Wallet activity deleted from MongoDB.", "success")
    return redirect(url_for("wallet_activity"))


@app.route("/events")
def transaction_events():
    term = request.args.get("q", "").strip()
    event_name = request.args.get("event_name", "").strip()
    contract = request.args.get("contract", "").strip()
    filters = {}
    if term:
        pattern = {"$regex": re.escape(term), "$options": "i"}
        filters["$or"] = [{"transaction_hash": pattern}, {"contract_address": pattern}, {"event_name": pattern}]
    if event_name:
        filters["event_name"] = {"$regex": re.escape(event_name), "$options": "i"}
    if contract:
        filters["contract_address"] = {"$regex": re.escape(contract), "$options": "i"}
    rows = list(mongo_collection("transaction_events").find(filters).sort("timestamp", DESCENDING).limit(250))
    for row in rows:
        row["json_document"] = mongo_json(row)
    return render_template("transaction_events.html", rows=rows, term=term, event_name=event_name, contract=contract)


@app.route("/events/new", methods=["GET", "POST"])
def transaction_event_new():
    return transaction_event_form()


@app.route("/events/<event_id>/edit", methods=["GET", "POST"])
def transaction_event_edit(event_id):
    try:
        object_id = ObjectId(event_id)
    except InvalidId:
        abort(404)
    return transaction_event_form(object_id)


def transaction_event_form(object_id=None):
    collection = mongo_collection("transaction_events")
    existing = collection.find_one({"_id": object_id}) if object_id else None
    if object_id and not existing:
        abort(404)
    if request.method == "GET":
        return render_template("transaction_event_form.html", event=existing, editing=bool(existing))

    form = request.form
    tx_hash = form.get("transaction_hash", "").strip()
    contract = form.get("contract_address", "").strip()
    event_name = form.get("event_name", "").strip()
    try:
        block_number = int(form.get("block_number", ""))
        if block_number < 0:
            raise ValueError
    except ValueError:
        flash("Block number must be a non-negative integer.", "error")
        return render_template("transaction_event_form.html", event=dict(form), editing=bool(existing)), 400
    try:
        timestamp = parse_timestamp(form.get("timestamp", ""))
        if not tx_hash or not contract or not event_name:
            raise ValueError("Transaction hash, contract address and event name are required.")
        event_data = json.loads(form.get("event_data", "{}"))
        if not isinstance(event_data, dict):
            raise ValueError("Event data must be a JSON object, for example {\"from\": \"0x...\"}.")
    except (ValueError, json.JSONDecodeError) as error:
        flash(str(error) or "Event data must contain valid JSON.", "error")
        return render_template("transaction_event_form.html", event=dict(form), editing=bool(existing)), 400

    now = datetime.now(timezone.utc)
    document = {
        "transaction_hash": tx_hash, "block_number": block_number,
        "contract_address": contract, "event_name": event_name,
        "timestamp": timestamp, "event_data": event_data, "updated_at": now,
    }
    if existing:
        collection.update_one({"_id": object_id}, {"$set": document})
    else:
        document["created_at"] = now
        collection.insert_one(document)
    flash("Smart contract event saved to MongoDB.", "success")
    return redirect(url_for("transaction_events", q=tx_hash))


@app.post("/events/<event_id>/delete")
def transaction_event_delete(event_id):
    try:
        object_id = ObjectId(event_id)
    except InvalidId:
        abort(404)
    result = mongo_collection("transaction_events").delete_one({"_id": object_id})
    if not result.deleted_count:
        abort(404)
    flash("Smart contract event deleted from MongoDB.", "success")
    return redirect(url_for("transaction_events"))


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
