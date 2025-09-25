from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from .routes.auth_routes import auth_bp
    from .routes.transaction_routes import transactions_bp
    from .routes.admin_routes import admin_bp
    from .routes.discord_routes import discord_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(discord_bp, url_prefix='/discord')

    return app