from flask import Blueprint
from interbend.db import db, get_user
from interbend.auth import *
import hmac
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin_bp', __name__)

def _keychecker(key):
    oskey = current_app.config['OS_KEY']
    if not oskey or not hmac.compare_digest(key, oskey):
        return False
    return True


@admin_bp.route('/salary', methods=['POST'])
def set_salary():
    data = request.get_json()
    bid = data.get('bid')
    salary_class = data.get('class')
    key = data.get('key')
    if not bid or not salary_class or not key:
        return jsonify({"error": "BID, salary class, and key are required"}), 400
    if not _keychecker(key):
        return jsonify({"error":"Admin Key required"}), 403
    user = get_user(bid)
    if not user:
        return jsonify({"error": "User not found"}), 404
    with db.cursor(dictionary=True) as cur:
        cur.execute("UPDATE users SET salary_class = %s WHERE bid = %s", (salary_class, bid))
    db.commit()
    return jsonify({"message": "Salary class updated successfully"}), 200

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
