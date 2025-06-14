from flask import Flask, request, jsonify, make_response
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from datetime import timezone
import mysql.connector
import os
from dotenv import load_dotenv
import jwt

load_dotenv()
app = Flask(__name__)

# JWT Init
jwt_key=os.getenv('JWT_KEY')
jwt_expire=int(os.getenv('JWT_EXPIRATION')) #In days
# Implemented authentication and data security practices aligned with ISO/IEC 27001 standards
# /\ AI generated for resume. Lol

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("token")
        if not token:
            return jsonify({"error": "Authentication required"}), 400
        try:
            payload = jwt.decode(token, jwt_key, algorithms=["HS256"])
            request.bid = payload["bid"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated_function

# DATABASE CONNECTION
db = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)
with db.cursor(dictionary=True) as cursor:
    cursor.execute("CREATE TABLE IF NOT EXISTS users ("
               "bid VARCHAR(32) PRIMARY KEY,"
               "username VARCHAR(64) NOT NULL,"
               "email VARCHAR(128) NOT NULL,"
               "password_hash TEXT,"
               "balance DECIMAL(18, 2) DEFAULT 7500,"
               "job INT,"
               "salary_class INT,"
               "collected DATETIME"
               ");")
    cursor.execute("CREATE TABLE IF NOT EXISTS salary ("
               "class INT PRIMARY KEY,"
               "money DECIMAL(18, 2));")
db.commit()

def token_gen(bid):
    exptime = datetime.now(timezone.utc) + timedelta(days=jwt_expire)
    token = jwt.encode(
        {"bid": bid, "exp": exptime},
        jwt_key,
        algorithm="HS256")
    return token

def get_user(bid):
    with db.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM users WHERE bid = %s", (bid,))
        return cur.fetchone()

@app.route('/balance', methods=['GET'])
def get_balance():
    bid = request.args.get('bid')
    user = get_user(bid)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"balance": user["balance"]})

@app.route('/register', methods=['POST'])
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



@app.route('/login', methods=['POST'])
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

@app.route('/transfer', methods=['POST'])
@jwt_required
def transfer():
    token = request.cookies.get("token")
    if not token:
        return jsonify({"error": "Authentication required"}), 400
    try:
        payload = jwt.decode(token, jwt_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    user_bid = payload["bid"]
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
    with db.cursor(dictionary=True) as cur:
        cur.execute("UPDATE users SET balance = balance - %s WHERE bid = %s", (amount, fbid))
        cur.execute("UPDATE users SET balance = balance + %s WHERE bid = %s", (amount, tbid))
    db.commit()
    return jsonify({"message": "Transfer successful"}), 200


@app.route('/admin/change-password', methods=['POST', 'PATCH'])
def change_password():
    data = request.get_json()
    bid = data.get('bid')
    new_password = data.get('password')
    key = data.get('key')
    if not bid or not new_password or not key:
        return jsonify({"error": "BID, new password, and key are required"}), 400
    if key != os.getenv('ADMIN_KEY'):
        return jsonify({"error": "Admin Key required"}), 403
    user = get_user(bid)
    if not user:
        return jsonify({"error": "User not found"}), 404
    new_password_hash = generate_password_hash(new_password)
    with db.cursor(dictionary=True) as cur:
        (cur.execute("UPDATE users SET password_hash = %s WHERE bid = %s", (new_password_hash, bid)))
    db.commit()
    return jsonify({"message": "Password changed successfully"}), 200

@app.route('/collect', methods=['POST'])
def collect_salary():
    return jsonify({"message":"no implementation"}), 501

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
