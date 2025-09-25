from flask import Blueprint, make_response
from interbend.db import db, get_user
from interbend.auth import *
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

discord_bp = Blueprint('discord_bp', __name__)

@discord_bp.route('/register-id', methods=['POST'])
def register_id():
    data = request.get_json()
    bid = data.get('bid')
    name = data.get('name')
    origin = data.get('origin')
    age = data.get('age')
    gender = data.get('gender')
    bot_key2 = data.get('bot_key')
    if bot_key2 != current_app.config['BOT_KEY']:
        return jsonify({"error": "Unauthorized"}), 401
    if not bid or not name or not origin or not age or not gender:
        return jsonify({"error": "BID, name, origin, age, and gender are required"}), 400
    user = get_user(bid)
    if not user:
        return jsonify({"error": "User is not registered"}), 404
        # Should the user be automatically registered here?
    return jsonify({"error": "Method not implemented"}), 501