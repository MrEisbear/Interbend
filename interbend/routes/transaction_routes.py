from flask import Blueprint

from config import Config
from interbend.db import db, get_user
from interbend.auth import *
import mysql.connector

transactions_bp = Blueprint('transactions_bp', __name__)

@transactions_bp.route('/balance', methods=['GET'])
def get_balance():
    bid = request.args.get('bid')
    user = get_user(bid)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"balance": user["balance"]})

@transactions_bp.route('/collect', methods=['POST'])
@jwt_required
def collect():
    bid = request.bid
    cooldown = Config.COLLECT_COOLDOWN

    try:
        with db.cursor(dictionary=True) as cur:
            # 1. Get user job
            cur.execute("SELECT * FROM user_jobs WHERE bid = %s", (bid,))
            user_jt = cur.fetchone()
            if not user_jt:
                return jsonify({"error": "You dont have any Jobs"}), 404

            # 2. Check cooldown
            active_cooldown = user_jt.get("collected")
            if active_cooldown and (active_cooldown + timedelta(hours=cooldown) > datetime.now(timezone.utc)):
                remaining_time = (active_cooldown + timedelta(hours=cooldown)) - datetime.now(timezone.utc)
                hours = int(remaining_time.total_seconds() // 3600)
                minutes = int(remaining_time.total_seconds() % 3600 // 60)
                return jsonify({"error": f"You can only collect your salary every {cooldown} hours. Please wait {hours}h {minutes}m."}), 429

            # 3. Get job details
            job_id = user_jt["job_id"]
            cur.execute("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
            job_data = cur.fetchone()
            if not job_data:
                return jsonify({"error": "Invalid Job", "message": "If you believe this is an error, contact an Administrator"}), 404

            # 4. Get salary details
            salary_class = job_data["salary_class"]
            cur.execute("SELECT * FROM salary WHERE class = %s", (salary_class,))
            salary_data = cur.fetchone()
            if not salary_data:
                return jsonify({"error": "Invalid Salary Class"}), 500

            amount = salary_data["money"]

            # 5. Perform transaction
            db.start_transaction()
            cur.execute("UPDATE users SET balance = balance + %s WHERE bid = %s", (amount, bid))
            cur.execute("UPDATE user_jobs SET collected = %s WHERE bid = %s", (datetime.now(timezone.utc), bid))
            cur.execute(
                "INSERT INTO transactions (source, target, amount, type, timestamp, status) VALUES (%s, %s, %s, %s, %s, %s)",
                ("SYSTEM", bid, amount, "salary", datetime.now(timezone.utc), "completed")
            )
            cur.execute("SELECT balance FROM users WHERE bid = %s", (bid,))
            new_balance = cur.fetchone()["balance"]
            db.commit()

            return jsonify({"message": "Salary Collected", "New Balance": new_balance}), 200

    except mysql.connector.Error as err:
        db.rollback()
        current_app.logger.error(f"Database error in /collect: {err}")
        return jsonify({"error": "A database error occurred, please try again later."}), 500
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"An unexpected error occurred in /collect: {e}")
        return jsonify({"error": "An unexpected server error occurred."}), 500

@transactions_bp.route('/transactions', methods=['GET'])
@jwt_required
def get_transactions():
    user_bid = request.bid
    limit = request.args.get('limit', default=10, type=int)
    try:
        with db.cursor(dictionary=True) as cur:
            cur.execute("SELECT * FROM transactions WHERE source = %s OR target = %s ORDER BY timestamp DESC LIMIT %s", (user_bid, user_bid, limit))
            transactions = cur.fetchall()
            return jsonify({"transactions": transactions}), 200
    except mysql.connector.Error as err:
        current_app.logger.error(f"Database error in /transactions: {err}")
        return jsonify({"error": "A database error occurred, please try again later."}), 500
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred in /transactions: {e}")
        return jsonify({"error": "An unexpected server error occurred."}), 500
    

# this should be fine (not)

def transfer_boilerplate(user_bid, fbid, tbid, amount, note, type):
    if not user_bid or not fbid or not tbid or not amount:
        return jsonify({"error": "From, To, and amount are required"}), 400
    if not note:
        print(f"{type} failed to provide note. No trace available because I am lazy to program such things.")
        return jsonify ({"error": "Note shouldve been passed by internal method."}), 500
    if not type in [0, 1, 2, 3, 4, 5, 6, 7, 8]: # 0 = personal, 1 = business, 2 = fine, 3 = salary, 4 = bill, 5 = admin adjustment, 6 = placeholder, 7 = placeholder2, 8 = other
        print(f"type was {type}, which is invalid. This is a bug. Internal Method failed to provide a valid type. No trace available because I am lazy to program such things.")
        return jsonify({"error": "Internal method failed to provide a valid type."}), 500
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid amount","message":"Try to request Money instead"}), 400
    sender = get_user(fbid)
    receiver = get_user(tbid)
    if not sender or not receiver:
        return jsonify({"error":"User not found"}), 404
    # here is space to add tax if its a business transaction.
    if type == 1:  # Business Transfer
        gtax = 0.3  # 30% tax for business transactions - configurable later TO DO
        tax = amount * gtax
        note += f" (Tax applied: {tax})"
        tax_account_bid = Config.TAX_ACCOUNT_BID
        if sender["balance"] < amount + tax:
            return jsonify({"error": "Insufficient funds"}), 400
        
    if sender["balance"] < amount:
        return jsonify({"error": "Insufficient funds"}), 400
    try:
        db.start_transaction()
        with db.cursor(dictionary=True) as cur:
            cur.execute("UPDATE users SET balance = balance - %s WHERE bid = %s", (amount, fbid))
            cur.execute("UPDATE users SET balance = balance + %s WHERE bid = %s", (amount, tbid))
            if type == 1:  # Business Transfer
                cur.execute("UPDATE users SET balance = balance - %s WHERE bid = %s", (tax, fbid))
                cur.execute("UPDATE users SET balance = balance + %s WHERE bid = %s", (tax, tax_account_bid))
            cur.execute("INSERT INTO transactions (source, target, amount, note, type, timestamp, status) VALUES (%s, %s, "
                        "%s, %s, %s, %s)", fbid, tbid, amount, note, "transfer", datetime.now(timezone.utc),
                        "completed", )
        db.commit()
        return jsonify({"message": "Transfer successful"}), 200
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Transactional Error: {err}")
        return jsonify({"error": "A database error occurred during the transfer."}), 500

# PERSONAL TRANSFERS
@transactions_bp.route('/transfer', methods=['POST'])
@jwt_required
def transfer():
    # Ignore warning because it's dynamically added via jwt required.
    user_bid = request.bid
    data = request.get_json()
    fbid = data.get('from')
    tbid = data.get('to')
    amount = data.get('amount')
    note = data.get('note')
    type = int(0) # Personal Transfer
    if not fbid:
        user_bid = fbid
    if fbid != user_bid:
        return jsonify({"error": "Unauthorized transfer from another account"}), 401
    if not note:
        note = "No note provided, Personal Transfer from " + fbid
    return transfer_boilerplate(user_bid, fbid, tbid, amount, note, type)

# BUSINESS TRANSFERS
@transactions_bp.route('/transfer-business', methods=['POST'])
@jwt_required
def transfer_business():
    # Ignore warning because it's dynamically added via jwt required.
    user_bid = request.bid
    data = request.get_json()
    fbid = data.get('from')
    tbid = data.get('to')
    amount = data.get('amount')
    note = data.get('note')
    type = int(1) # Business Transfer
    if not fbid:
        user_bid = fbid
    if fbid != user_bid:
        return jsonify({"error": "Unauthorized transfer from another account"}), 401
    if not note:
        note = "No note provided, Business Transfer from " + fbid
    return transfer_boilerplate(user_bid, fbid, tbid, amount, note, type)