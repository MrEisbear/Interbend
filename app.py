from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)



# DATABASE CONNECTION
db = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)
cursor = db.cursor(dictionary=True)
cursor.execute("CREATE TABLE IF NOT EXISTS users ("
               "bid VARCHAR(32) PRIMARY KEY,"
               "username VARCHAR(64) NOT NULL,"
               "email VARCHAR(128) NOT NULL,"
               "password_hash TEXT,"
               "balance INT DEFAULT 7500,"
               "job INT,"
               "salary_class INT,"
               "collected DATETIME"
               ");")

def get_user(uid):
    cursor.execute("SELECT * FROM users WHERE bid = %s", (uid,))
    return cursor.fetchone()

@app.route('/balance', methods=['GET'])
def get_balance():
    uid = request.args.get('uid')
    user = get_user(uid)
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
    password_hash = generate_password_hash(password, method='sha256')
    try:
        cursor.execute("INSERT INTO users (bid, username, email, password_hash) VALUES (%s, %s, %s, %s)",
                       (bid, username, email, password_hash))
        db.commit()
        token = None
        return jsonify({"message": "User registered successfully.","token": token}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Username or email already exists."}), 409


@app.route('/login', methods=['POST'])
def login():
    return 501

@app.route('/collect', methods=['POST'])
def collect_salary():
    return 501

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
