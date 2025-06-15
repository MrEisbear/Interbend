from flask import Blueprint, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import hmac
import mysql.connector

# custom
from interbend.db import db, get_user
from interbend.auth import *

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/balance', methods=['GET'])
def get_balance():
    bid = request.args.get('bid')
    user = get_user(bid)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"balance": user["balance"]})

@main_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    bid = data.get('bid')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password or not bid:
        return jsonify({"error": "Username, email, and password are required."}), 400
    password_hash = generate_password_hash(password)
    try:
        with db.cursor(dictionary=True) as cur:
            cur.execute("INSERT INTO users (bid, username, email, password_hash) VALUES (%s, %s, %s, %s)",
                          (bid, username, email, password_hash))
        db.commit()
        token = token_gen(bid)
        response = make_response(jsonify({"message": "Login successful."}), 201)
        response.set_cookie('token', token, httponly=True, samesite='Strict', max_age=30 * 24 * 60 * 60)
        return response
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Username or email already exists."}), 409



@main_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    bid = data.get('bid')
    password = data.get('password')

    if not bid or not password:
        return jsonify({"error": "BID and password are required"}), 400
    user = get_user(bid)
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not check_password_hash(user['password_hash'], password):
        return jsonify({"error": "Invalid password"}), 401
    token = token_gen(bid)
    response = make_response(jsonify({"message": "Login successful."}), 200)
    response.set_cookie('token', token, httponly=True, samesite='Strict', max_age=30 * 24 * 60 * 60)
    # secure=True - Implement once HTTPS
    return response

@main_bp.route('/transfer', methods=['POST'])
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


@main_bp.route('/admin/change-password', methods=['POST', 'PATCH'])
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

@main_bp.route('/collect', methods=['POST'])
def collect_salary():
    return jsonify({"message":"no implementation"}), 501

@main_bp.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

