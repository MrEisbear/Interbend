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
            cur.execute("SELECT * FROM user_jobs WHERE bid = %s", (bid,))
            user_jt = cur.fetchone()
        if not user_jt:
            return jsonify({"error": "You dont have any Jobs"}), 404
        active_cooldown = user_jt["collected"]
    except mysql.connector.Error as err:
        current_app.logger.error(f"Database error in collect, salary: {err}")
        return jsonify({"error": "A database error occurred, please try again later."}), 500
    if active_cooldown + timedelta(hours=cooldown) > datetime.now(timezone.utc):
        remaining_time = (active_cooldown + timedelta(hours=cooldown)) - datetime.now(timezone.utc)
        hours = int(remaining_time.total_seconds() // 3600)
        minutes = int(remaining_time.total_seconds() % 3600 // 60)
        return jsonify({"error": f"You can only collect your salary every {cooldown} hours. Please wait {hours}h {minutes}m."}), 429
    job = user_jt["job_id"]
    try:
        with db.cursor(dictionary=True) as cur:
            cur.execute("SELECT * FROM jobs WHERE job_id = %i", (job,))
            job_data = cur.fetchone()
    except mysql.connector.Error as err:
        current_app.logger.error(f"Database error in collect, salary: {err}")
        return jsonify({"error": "A database error occurred, please try again later."}), 500
    if not job_data:
        return jsonify({"error": "Invalid Job","message":"If you believe this is an error, contact a "
                                                         "Administrator"}), 404
    salary_class = job_data["salary_class"]
    try:
        with db.cursor(dictionary=True) as cur:
            cur.execute("SELECT * FROM salary WHERE class = %i", (salary_class,))
            salary_data = cur.fetchone()
    except mysql.connector.Error as err:
        current_app.logger.error(f"Database error in collect, salary: {err}")
        return jsonify({"error": "A database error occurred, please try again later."}), 500
    if not salary_data:
        return jsonify({"error": "Invalid Salary Class"}), 500
    amount = salary_data["money"]
    try:
        with db.cursor(dictionary=True) as cur:
            cur.execute("UPDATE users SET balance = balance + %s WHERE bid = %s", (amount, bid,))
            cur.execute("UPDATE user_jobs SET collected = %s WHERE bid = %s", (datetime.now(timezone.utc), bid,))
            cur.execute("SELECT balance FROM users WHERE bid = %s", (bid,))
            new_bal2 = cur.fetchone()
            new_bal = new_bal2["balance"]
            db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        current_app.logger.error(f"Database error in collect, salary: {err}")
        return jsonify({"error": "A database error occurred, please try again later."}), 500
    return jsonify({"message":"Salary Collected","New Balance":new_bal}), 200

@transactions_bp.route('/transfer', methods=['POST'])
@jwt_required
def transfer():
    # Ignore warning because it's dynamically added via jwt required.
    user_bid = request.bid
    data = request.get_json()
    fbid = data.get('from')
    tbid = data.get('to')
    amount = data.get('amount')
    if not tbid or not amount:
        return jsonify({"error": "To and amount are required"}), 400
    if not fbid:
        fbid = user_bid
    if fbid != user_bid:
        return jsonify({"error": "Unauthorized transfer from another account"}), 401
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
    if sender["balance"] < amount:
        return jsonify({"error": "Insufficient funds"}), 400
    try:
        db.start_transaction()
        with db.cursor(dictionary=True) as cur:
            cur.execute("UPDATE users SET balance = balance - %s WHERE bid = %s", (amount, fbid))
            cur.execute("UPDATE users SET balance = balance + %s WHERE bid = %s", (amount, tbid))
        db.commit()
        return jsonify({"message": "Transfer successful"}), 200
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Transactional Error: {err}")
        return jsonify({"error": "A database error occurred during the transfer."}), 500