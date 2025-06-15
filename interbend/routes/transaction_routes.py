from flask import Blueprint
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

@transactions_bp.route('/transfer', methods=['POST'])
@jwt_required
def transfer():
    # Ignore warning because its dynamically added via jwt required.
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

@transactions_bp.route('/collect', methods=['POST'])
def collect_salary():
    return jsonify({"message":"no implementation"}), 501