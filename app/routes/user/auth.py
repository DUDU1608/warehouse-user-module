from flask import Blueprint, render_template, request, redirect, session, url_for, flash

# If you want to re-enable SMS later, just uncomment this import and the send call.
# from utils.otp_sender import send_otp_fast2sms

user_auth_bp = Blueprint('user_auth', __name__, url_prefix='/user')

# ---- Test mode settings ----
DEFAULT_OTP = "123456"   # ← temporary fixed OTP
otp_store = {}           # in-memory store (optional)

@user_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile = request.form.get('mobile', '').strip()

        if not mobile or len(mobile) != 10 or not mobile.isdigit():
            flash("Please enter a valid 10-digit mobile number.", "danger")
            return render_template('user/login.html')

        # --- TEST MODE: always use fixed OTP ---
        otp_store[mobile] = DEFAULT_OTP

        # If you want to actually send this fixed OTP via SMS, uncomment:
        # try:
        #     send_otp_fast2sms(mobile, DEFAULT_OTP)
        #     flash("OTP sent to your mobile.", "info")
        # except Exception:
        #     flash("Failed to send OTP, but you can use 123456 for testing.", "warning")

        # Show the test OTP hint
        flash("Test mode: Use OTP 123456 to continue.", "info")
        return render_template('user/verify_otp.html', mobile=mobile)

    return render_template('user/login.html')


@user_auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    mobile = request.form.get('mobile', '').strip()
    entered_otp = request.form.get('otp', '').strip()

    if not mobile or not entered_otp:
        flash("Missing mobile number or OTP.", "danger")
        return redirect(url_for('user_auth.login'))

    # Accept fixed OTP unconditionally in test mode
    if entered_otp == DEFAULT_OTP:
        session['mobile'] = mobile
        return redirect(url_for('user_views.home'))

    # (Optional) also check store if you want
    expected_otp = otp_store.get(mobile)
    if expected_otp and entered_otp == expected_otp:
        session['mobile'] = mobile
        return redirect(url_for('user_views.home'))

    flash("Invalid OTP. Please try again.", "danger")
    return render_template('user/verify_otp.html', mobile=mobile)


@user_auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user_auth.login'))
