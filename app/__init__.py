import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

# -------------------
# Jinja Filter Utils
# -------------------

def format_inr(value):
    try:
        value = float(value or 0)
        s = f"{value:.2f}"
        int_part, dec_part = s.split('.')

        if len(int_part) <= 3:
            return f"₹{int_part}.{dec_part}"

        # Grouping digits for Indian format
        last_three = int_part[-3:]
        rest = int_part[:-3]
        rest = ','.join([rest[max(i - 2, 0):i] for i in range(len(rest), 0, -2)][::-1]).lstrip(',')

        formatted = f"{rest},{last_three}" if rest else last_three
        return f"₹{formatted}.{dec_part}"
    except Exception:
        return "₹0.00"

def kg_to_mt(value):
    try:
        return "{:.2f} MT".format((value or 0) / 1000)
    except:
        return "0.00 MT"

def format_date(value):
    try:
        if hasattr(value, "strftime"):
            return value.strftime('%d-%m-%Y')
        elif isinstance(value, str):
            try:
                dt = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return dt.strftime('%d-%m-%Y')
        else:
            return value
    except:
        return value

# -------------------
# Create Flask App
# -------------------

def create_app():
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
                template_folder='templates')

    app.config['SECRET_KEY'] = '5e4a6264c704ebe73ae348c4b3283d0b43ba1d04ab380c83dd4ab523f3f2c39d'
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../instance/warehouse.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    # Register custom filters
    app.jinja_env.filters['format_inr'] = format_inr
    app.jinja_env.filters['kg_to_mt'] = kg_to_mt
    app.jinja_env.filters['format_date'] = format_date

    # Register Blueprints
    from app.routes.user.auth import user_auth_bp
    from app.routes.user.views import user_view_bp
    app.register_blueprint(user_auth_bp)
    app.register_blueprint(user_view_bp)

    # Root Route
    @app.route('/')
    def root():
        return render_template('user/index.html')

    # Test Route
    @app.route('/test')
    def test():
        return "✅ Test route working from VPS!"

    return app
