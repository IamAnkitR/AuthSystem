import random
from flask_mail import Message
from datetime import datetime, timedelta

def generate_otp():
    """Generate a 6-digit OTP."""
    return f"{random.randint(100000, 999999)}"

def send_email(mail, recipient, otp):
    """Send OTP email."""
    msg = Message("Your OTP Code", sender="noreply@example.com", recipients=[recipient])
    msg.body = f"Your OTP is: {otp}\nIt is valid for 5 minutes."
    mail.send(msg)

def is_otp_valid(otp_entry):
    """Check if an OTP is valid."""
    if not otp_entry:
        return False
    expiration_time = otp_entry.created_at + timedelta(minutes=5)
    return datetime.utcnow() <= expiration_time
