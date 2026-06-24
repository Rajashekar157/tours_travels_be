import requests
import os
from dotenv import load_dotenv

load_dotenv()


MSG91_AUTH_KEY = os.getenv("MSG91_AUTH_KEY")

def send_sms_otp(mobile: str, otp: str):

    print("AUTH KEY:", MSG91_AUTH_KEY)

    url = "https://control.msg91.com/api/v5/otp"

    payload = {
        "mobile": f"91{mobile}",
        "otp": otp
    }

    headers = {
        "authkey": MSG91_AUTH_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

    return response.json()