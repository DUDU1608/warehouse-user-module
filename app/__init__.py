from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

import re

def format_inr(value):
    try:
        value = float(value or 0)
        s = f"{value:.2f}"
        x = s.split('.')
        int_part = x[0]
        dec_part = x[1]

        # If number is less than 1,000 – just return as-is
        if len(int_part) <= 3:
            return f"₹{int_part}.{dec_part}"

        # Handle the last 3 digits separately
        last_three = int_part[-3:]
        rest = int_part[:-3]

        # Add commas to the rest (every 2 digits from right)
        rest = ''.join([',' + rest[max(i-2,0):i] for i in range(len(rest), 0, -2)][::-1]).lstrip(',')

        formatted = rest + ',' + last_three if rest else last_three
        return f"₹{formatted}.{dec_part}"
    except:
        return "₹0.00"

def kg_to_mt(value):
    try:
        return "{:.2f} MT".format((value or 0) / 1000)
    except:
        return "0.00 MT"

def format_date(value):
    from datetime import datetime
    try:
        if hasattr(value, "strftime"):
            return value.strftime('%d-%m-%Y')
        elif isinstance(value, str):
            # Try to parse the string
            try:
                dt = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return dt.strftime('%d-%m-%Y')
        else:
            return value
    except Exception:
        return value

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '5e4a6264c704ebe73ae348c4b3283d0b43ba1d04ab380c83dd4ab523f3f2c39d'
    # This makes the DB path work on any computer/server, if warehouse.db is in the project root
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///warehouse.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    db.init_app(app)
    login_manager.init_app(app)
    # login_manager.login_view = 'user_auth.login'  # Uncomment if you use flask_login

    # Register Jinja filters
    app.jinja_env.filters['format_inr'] = format_inr
    app.jinja_env.filters['kg_to_mt'] = kg_to_mt
    app.jinja_env.filters['format_date'] = format_date

    # Only register user module blueprints
    from app.routes.user.auth import user_auth_bp
    from app.routes.user.views import user_view_bp

    app.register_blueprint(user_auth_bp)
    app.register_blueprint(user_view_bp)

    # This is the CORRECT way to register the root route
    @app.route('/')
    def root():
        return render_template('user/index.html')

    return app
