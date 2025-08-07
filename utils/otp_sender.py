import requests
import os
from dotenv import load_dotenv

load_dotenv()

FAST2SMS_API_KEY = os.getenv("kYH0O1LXEpPJbxN8tdcGDQRuslU7MzCTrmIiy4v9egABqFhZowqTg0QL4fldPyeI5F3bASR6auohEOpm")

def send_otp_fast2sms(mobile, otp):
    if not FAST2SMS_API_KEY:
        print("Error: FAST2SMS_API_KEY is missing in environment variables.")
        return False

    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
        "route": "otp",
        "variables_values": otp,
        "numbers": mobile,
        "flash": "0",
        "sender_id": "FSTSMS"
    }

    headers = {
        'authorization': FAST2SMS_API_KEY,
        'Content-Type': "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(url, data=payload, headers=headers)
        print(f"[Fast2SMS Response] {response.status_code}: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return False
