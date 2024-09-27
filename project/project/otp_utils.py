import random
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from twilio.rest import Client
from datetime import timezone, timedelta

def generate_otp():
    return get_random_string(length=6, allowed_chars='1234567890')

def send_otp_via_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}. Please use it to verify your identity.'
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [email])

def send_otp_via_sms(phone_number, otp):
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f'Your OTP code is {otp}. Please use it to verify your identity.',
        from_='your_twilio_phone_number',
        to=phone_number
    )

def send_otp(user, otp):
    if user.preferred_contact_method == 'email':
        send_otp_via_email(user.email, otp)
    elif user.preferred_contact_method == 'sms':
        send_otp_via_sms(user.phone_number, otp)

def verify_otp(user, provided_otp):
    if user.otp == provided_otp and timezone.now() < user.otp_expiration:
        return True
    return False

def set_otp(user):
    otp = generate_otp()
    user.otp = otp
    user.otp_expiration = timezone.now() + timedelta(minutes=5)
    user.save()
    send_otp(user, otp)
