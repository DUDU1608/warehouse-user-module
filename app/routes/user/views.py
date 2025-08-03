from flask import Blueprint, render_template, session, redirect, url_for
from flask_login import login_required

from app import db
from app.models import Seller, Stockist, Purchase, Payment, LoanData, MarginData, StockData


def login_required(func):
    from functools import wraps
    from flask import session, redirect, url_for

    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'mobile' not in session:
            return redirect(url_for('user_auth.login'))
        return func(*args, **kwargs)
    return wrapper


user_view_bp = Blueprint('user_views', __name__, url_prefix='/user')


@user_view_bp.route('/')
def index():
    return render_template('user/index.html')

@user_view_bp.route('/home')
def home():
    if 'mobile' not in session:
        return redirect(url_for('user_auth.login'))

    mobile = session['mobile']
    seller = Seller.query.filter_by(mobile=mobile).first()
    stockist = Stockist.query.filter_by(mobile=mobile).first()

    is_seller = seller is not None
    is_stockist = stockist is not None

    # Prefer seller name, fallback to stockist
    if is_seller and seller.name:
        display_name = seller.name
    elif is_stockist and stockist.name:
        display_name = stockist.name
    else:
        display_name = "User"

    return render_template('user/home.html',
                           is_seller=is_seller,
                           is_stockist=is_stockist,
                           display_name=display_name)


from datetime import date

@user_view_bp.route('/seller')
@login_required
def seller_module():
    mobile = session.get('mobile')
    seller = Seller.query.filter_by(mobile=mobile).first()
    if not seller:
        return redirect(url_for('user_auth.login'))

    # Get seller name to match purchase/payment tables
    name = seller.name

    # Purchases
    purchases = Purchase.query.filter_by(seller_name=name).all()
    purchase_summary = {
        'quantity': sum(p.quantity or 0 for p in purchases),
        'reduction': sum(p.reduction or 0 for p in purchases),
        'net_qty': sum(p.net_qty or 0 for p in purchases),
        'cost': sum(p.cost or 0 for p in purchases),
        'handling': sum(p.handling or 0 for p in purchases),
        'net_cost': sum(p.net_cost or 0 for p in purchases)
    }

    # Payments
    payments = Payment.query.filter_by(seller_name=name).all()
    payment_summary = {
        'amount': sum(p.amount_paid or 0 for p in payments)
    }

    # Payment Due
    net_cost = purchase_summary.get('net_cost') or 0
    amount_paid = payment_summary.get('amount') or 0
    payment_due = net_cost - amount_paid

    return render_template(
        'user/seller_module.html',
        purchases=purchases,
        payments=payments,
        purchase_summary=purchase_summary,
        payment_summary=payment_summary,
        net_cost=net_cost,
        amount_paid=amount_paid,
        payment_due=payment_due,
        today=date.today().strftime("%d/%m/%Y")
    )

@user_view_bp.route('/stockist')
@login_required
def stockist_module():
    mobile = session.get('mobile')
    stockist = Stockist.query.filter_by(mobile=mobile).first()
    if not stockist:
        return redirect(url_for('user_auth.login'))

    name = stockist.name

    # --------------------------------
    # 1. My Materials Stored
    # --------------------------------
    stock_data = StockData.query.filter_by(stockist_name=name).all()

    # Summary by warehouse and commodity (in MT)
    material_summary = {}
    for entry in stock_data:
        wh = entry.warehouse
        com = entry.commodity
        qty = (entry.quantity or 0) / 1000  # Convert kg to MT

        if wh not in material_summary:
            material_summary[wh] = {}
        material_summary[wh][com] = material_summary[wh].get(com, 0) + qty

    # --------------------------------
    # 2. Loans Received
    # --------------------------------
    loan_data = LoanData.query.filter_by(stockist_name=name).all()

    # Initialize summary structure
    loan_summary = {}
    for entry in loan_data:
        wh = entry.warehouse
        loan_type = entry.loan_type
        amt = entry.amount or 0

        if wh not in loan_summary:
            loan_summary[wh] = {'cash': 0, 'margin': 0}

        if loan_type.lower() == 'cash':
            loan_summary[wh]['cash'] += amt
        elif loan_type.lower() == 'margin':
            loan_summary[wh]['margin'] += amt

    # --------------------------------
    # 3. Margins Paid
    # --------------------------------
    margin_data = MarginData.query.filter_by(stockist_name=name).all()

    margin_summary = {}
    for entry in margin_data:
        wh = entry.warehouse
        com = entry.commodity
        amt = entry.amount or 0

        if wh not in margin_summary:
            margin_summary[wh] = 0
        margin_summary[wh] += amt

    return render_template(
        'user/stockist_module.html',
        stock_data=stock_data,
        material_summary=material_summary,
        loan_data=loan_data,
        loan_summary=loan_summary,
        margin_data=margin_data,
        margin_summary=margin_summary
    )


