from flask import Flask
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

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///warehouse.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    app.jinja_env.filters['format_inr'] = format_inr
    app.jinja_env.filters['kg_to_mt'] = kg_to_mt

    from .routes import auth
    app.register_blueprint(auth.bp)

    from app.routes.seller import dashboard, seller, purchase, payment, due

    app.register_blueprint(dashboard.bp)
    app.register_blueprint(seller.bp)
    app.register_blueprint(purchase.bp)
    app.register_blueprint(payment.bp)
    app.register_blueprint(due.bp)

    from app.routes.stockist import dashboard, stockist, stockdata, stockexit, loandata, margindata, rental_calculator
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(stockist.bp)
    app.register_blueprint(stockdata.bp)
    app.register_blueprint(stockexit.bp)
    app.register_blueprint(loandata.bp)
    app.register_blueprint(margindata.bp)
    app.register_blueprint(rental_calculator.bp)

    from app.routes.company import dashboard as company_dashboard, companyloan, loanrepayment, interest_payble, interest_receivable, rental_due, expenditure, breakeven_calculator, profit_loss
    app.register_blueprint(company_dashboard.bp)
    app.register_blueprint(companyloan.bp)
    app.register_blueprint(loanrepayment.bp)
    app.register_blueprint(interest_payble.bp)
    app.register_blueprint(interest_receivable.bp)
    app.register_blueprint(rental_due.bp)
    app.register_blueprint(expenditure.bp)
    app.register_blueprint(breakeven_calculator.bp)
    app.register_blueprint(profit_loss.bp)


    from app.routes.stock_summary import bp as stock_summary_bp
    app.register_blueprint(stock_summary_bp)

    from app.routes.company.interest_receivable import calculate_interest_receivable_upto_today
    from app.routes.company.interest_payble import calculate_interest_payable_upto_today

    from app.routes.user import user_auth_bp, user_view_bp

    app.register_blueprint(user_auth_bp)
    app.register_blueprint(user_view_bp)


    return app
