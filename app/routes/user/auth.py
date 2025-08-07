from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from utils.otp_sender import send_otp_fast2sms
import random

user_auth_bp = Blueprint('user_auth', __name__, url_prefix='/user')

# In-memory OTP store
otp_store = {}

@user_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        if not mobile or len(mobile) != 10 or not mobile.isdigit():
            flash("Please enter a valid 10-digit mobile number.", "danger")
            return render_template('user/login.html')

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        otp_store[mobile] = otp

        # Send OTP using Fast2SMS
        success = send_otp_fast2sms(mobile, otp)

        if success:
            flash("OTP sent successfully to your mobile number.", "info")
            return render_template('user/verify_otp.html', mobile=mobile)
        else:
            flash("Failed to send OTP. Please try again.", "danger")
            return render_template('user/login.html')

    return render_template('user/login.html')


@user_auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    mobile = request.form.get('mobile')
    entered_otp = request.form.get('otp')

    if not mobile or not entered_otp:
        flash("Missing mobile number or OTP.", "danger")
        return redirect(url_for('user_auth.login'))

    expected_otp = otp_store.get(mobile)

    if entered_otp == expected_otp:
        session['mobile'] = mobile
        return redirect(url_for('user_views.home'))
    else:
        flash("Invalid OTP. Please try again.", "danger")
        return render_template('user/verify_otp.html', mobile=mobile)


@user_auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user_auth.login'))
