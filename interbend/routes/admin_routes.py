import mysql.connector
from flask import Blueprint
from interbend.db import db, get_user
from interbend.auth import *
import hmac
import decimal
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin_bp', __name__)

def _keychecker(key):
    oskey = current_app.config['OS_KEY']
    if not oskey or not hmac.compare_digest(key, oskey):
        return False
    return True


@admin_bp.route('/set-job', methods=['POST'])
def set_job():
    data = request.get_json()
    bid = data.get('bid')
    job_id = data.get('job')
    key = data.get('key')
    if not bid or not job_id or not key:
        return jsonify({"error": "BID, salary class, and key are required"}), 400
    if not _keychecker(key):
        return jsonify({"error":"Admin Key required"}), 403
    user = get_user(bid)
    if not user:
        return jsonify({"error": "User not found"}), 404
    with db.cursor(dictionary=True) as cur:
        cur.execute("UPDATE user_jobs SET job_id = %s WHERE bid = %s", (job_id, bid))
    db.commit()
    return jsonify({"message": "Salary class updated successfully"}), 200

@admin_bp.route('/add-money', methods=['POST', 'PATCH'])
def add_money():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    bid = data.get('bid')
    amount = data.get('amount')
    key = data.get('key')
    if not bid or not money or not key:
        return jsonify({"error": "BID, Amount and AdminKey are required"}), 400
    if not _keychecker(key):
        return jsonify({"error":"Admin Key required"}), 403
    try:
        amount_dec = decimal.Decimal(amount)
    except (ValueError, decimal.InvalidOperation):
        return jsonify({"error": "Invalid amount"}), 400
    user = get_user(bid)
    if not user:
        return jsonify({"error": "User not found"}), 404
    balance = user["balance"]
    new_balance = balance + amount_dec
    try:
        with db.cursor(dictionary=True) as cur:
            cur.execute("UPDATE users SET balance = %s WHERE bid = %s", (new_balance, bid))
        db.commit()
        return jsonify({"message": "Money successfully updated!"}), 200
    except mysql.connector.Error as err:
        db.rollback()
        current_app.logger.error(f"Database error in add_money: {err}")
        return jsonify({"error":"A database error occurred, please try again later."}), 500

@admin_bp.route('/change-password', methods=['POST', 'PATCH'])
def change_password():
    data = request.get_json()
    bid = data.get('bid')
    new_password = data.get('password')
    key = data.get('key')
    if not bid or not new_password or not key:
        return jsonify({"error": "BID, new password, and key are required"}), 400
    oskey = current_app.config['ADMIN_KEY']
    if not oskey or not hmac.compare_digest(key, oskey):
        return jsonify({"error": "Admin Key required"}), 403
    user = get_user(bid)
    if not user:
        return jsonify({"error": "User not found"}), 404
    new_password_hash = generate_password_hash(new_password)
    with db.cursor(dictionary=True) as cur:
        (cur.execute("UPDATE users SET password_hash = %s WHERE bid = %s", (new_password_hash, bid)))
    db.commit()
    return jsonify({"message": "Password changed successfully"}), 200
