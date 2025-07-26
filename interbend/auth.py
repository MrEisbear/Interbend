import secrets
import string
from functools import wraps
from flask import request, jsonify, current_app
import jwt
from datetime import datetime, timedelta, timezone

def _getconfig():
    jwt_key = current_app.config['JWT_KEY']
    jwt_expire = current_app.config['JWT_EXPIRE']  # In days
    return jwt_key, jwt_expire

def r_gen2(length):
    if length < 1:
        raise ValueError("Length must be at least 1")
    first_digit = secrets.choice(string.digits.replace('0', ''))
    return first_digit + ''.join(secrets.choice(string.digits) for _ in range(length - 1))

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        jwt_key, _ = _getconfig()
        token = request.cookies.get("token")
        if not token:
            return jsonify({"error": "Authentication token missing"}), 400
        try:
            payload = jwt.decode(token, jwt_key, algorithms=["HS256"])
            request.bid = payload["bid"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated_function

def token_gen(bid):
    jwt_key, jwt_expire = _getconfig()
    exptime = datetime.now(timezone.utc) + timedelta(days=jwt_expire)
    token = jwt.encode(
        {"bid": bid, "exp": exptime},
        jwt_key,
        algorithm="HS256")
    return token