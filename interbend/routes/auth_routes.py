from flask import Blueprint, make_response
from interbend.db import db, get_user
from interbend.auth import *
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/register', methods=['POST'])
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



@auth_bp.route('/login', methods=['POST'])
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