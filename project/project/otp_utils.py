import random
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from twilio.rest import Client
from datetime import timezone, timedelta

def generate_otp():
    """Generates a random 6-digit OTP."""
    return get_random_string(length=6, allowed_chars='1234567890')

def send_otp_via_email(email, otp):
    """Sends OTP via email."""
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}. Please use it to verify your identity.'
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [email])

def send_otp_via_sms(phone_number, otp):
    """Sends OTP via SMS using Twilio."""
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'
    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body=f'Your OTP code is {otp}. Please use it to verify your identity.',
            from_='your_twilio_phone_number',
            to=phone_number
        )
    except Exception as e:
        print(f"Failed to send SMS: {e}")

def send_otp(user, otp):
    """Sends OTP to the user based on their preferred contact method."""
    if user.preferred_contact_method == 'email':
        send_otp_via_email(user.email, otp)
    elif user.preferred_contact_method == 'sms':
        send_otp_via_sms(user.phone_number, otp)

def verify_otp(user, provided_otp):
    """Verifies the provided OTP against the stored OTP for the user."""
    if hasattr(user, 'otp') and hasattr(user, 'otp_expiration'):
        if user.otp == provided_otp and timezone.now() < user.otp_expiration:
            return True
    return False

def set_otp(user):
    """Generates and sets a new OTP for the user, also sends it."""
    otp = generate_otp()
    user.otp = otp
    user.otp_expiration = timezone.now() + timedelta(minutes=5)
    user.save()
    send_otp(user, otp)
