from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError, DatabaseError
from django.utils.http import base36_to_int, int_to_base36
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from project.otp_utils import generate_otp, send_otp, verify_otp, set_otp
from .forms import ServiceNumberForm, OfficialNameForm, PhoneNumberForm, OTPForm, EmailForm, SetPasswordForm
from .models import User
import json

# make sure CSRF tokens are included in requests made from the frontend

@require_http_methods(["POST"])
def check_service_number(request):
    data = json.loads(request.body)
    service_number = data.get('service_number')
    form = ServiceNumberForm({'service_number': service_number})
    
    if form.is_valid():
        try:
            if User.objects.filter(service_number=service_number).exists():
                return JsonResponse({'status': 'success'}, status=200)
            return JsonResponse({'error': 'Service number not found'}, status=400)
        except DatabaseError as e:  # Catch any database error (includes IntegrityError)
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid service number format'}, status=400)


@require_http_methods(["POST"])
def check_official_name(request):
    data = json.loads(request.body)
    official_name = data.get('official_name')
    form = OfficialNameForm({'official_name': official_name})
    
    if form.is_valid():
        try:
            user = User.objects.filter(official_name=official_name).first()
            if user:
                set_otp(user)
                return JsonResponse({'status': 'success'}, status=200)
            return JsonResponse({'error': 'Official name does not match'}, status=400)
        except DatabaseError as e:
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid data'}, status=400)


@require_http_methods(["POST"])
def check_phone_number(request):
    data = json.loads(request.body)
    service_number = data.get('service_number')
    phone_number = data.get('phone_number')
    form = PhoneNumberForm({'service_number': service_number, 'phone_number': phone_number})
    
    if form.is_valid():
        try:
            user = User.objects.filter(service_number=service_number, phone_number=phone_number).first()
            if user:
                set_otp(user)  # For phone number verification
                return JsonResponse({'status': 'success'}, status=200)
            return JsonResponse({'error': 'Phone number does not match'}, status=400)
        except DatabaseError as e:
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid data'}, status=400)


@require_http_methods(["POST"])
def verify_phone_otp(request):
    data = json.loads(request.body)
    service_number = data.get('service_number')
    phone_otp = data.get('phone_otp')
    
    try:
        user = User.objects.filter(service_number=service_number).first()
        if verify_otp(user, phone_otp):
            return JsonResponse({'status': 'success'}, status=200)
        return JsonResponse({'error': 'Invalid OTP'}, status=400)
    except DatabaseError as e:
        return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)


@require_http_methods(["POST"])
def check_email(request):
    data = json.loads(request.body)
    service_number = data.get('service_number')
    email = data.get('email')
    form = EmailForm({'service_number': service_number, 'email': email})
    
    if form.is_valid():
        try:
            user = User.objects.filter(service_number=service_number, email=email).first()
            if user:
                set_otp(user)
                return JsonResponse({'status': 'success'}, status=200)
            return JsonResponse({'error': 'Email does not match'}, status=400)
        except DatabaseError as e:
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid data'}, status=400)


@require_http_methods(["POST"])
def verify_email_otp(request):
    data = json.loads(request.body)
    service_number = data.get('service_number')
    email_otp = data.get('email_otp')
    
    try:
        user = User.objects.filter(service_number=service_number).first()
        if verify_otp(user, email_otp):
            return JsonResponse({'status': 'success'}, status=200)
        return JsonResponse({'error': 'Invalid OTP'}, status=400)
    except DatabaseError as e:
        return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)


@require_http_methods(["POST"])
def set_password(request):
    data = json.loads(request.body)
    official_name = data.get('official_name')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    form = SetPasswordForm({'password': password, 'confirm_password': confirm_password})
    
    if form.is_valid():
        if password == confirm_password:
            try:
                user = User.objects.get(official_name=official_name)
                user.password = make_password(password)
                user.save()
                return JsonResponse({'status': 'success'}, status=200)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=400)
            except DatabaseError as e:
                return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
        return JsonResponse({'error': 'Passwords do not match'}, status=400)
    return JsonResponse({'error': 'Invalid data'}, status=400)


@require_http_methods(["POST"])
def request_password_reset(request):
    data = json.loads(request.body)
    email = data.get('email')
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Email not found'}, status=400)
    except DatabaseError as e:
        return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
    
    try:
        token = default_token_generator.make_token(user)
        uid = int_to_base36(user.pk)
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
        send_mail(
            'Password Reset Request',
            f'Please use the following link to reset your password: {reset_link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        return JsonResponse({'status': 'Password reset email sent'}, status=200)
    except Exception as e:
        return JsonResponse({'error': f'Failed to send email: {str(e)}'}, status=500)


@require_http_methods(["POST"])
def reset_password(request, uidb36, token):
    data = json.loads(request.body)
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    if new_password != confirm_password:
        return JsonResponse({'error': 'Passwords do not match'}, status=400)
    
    try:
        user_id = int(base36_to_int(uidb36))
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Invalid link'}, status=400)
    
    if not default_token_generator.check_token(user, token):
        return JsonResponse({'error': 'Invalid or expired token'}, status=400)
    
    try:
        user.set_password(new_password)
        user.save()
        return JsonResponse({'status': 'Password successfully reset'}, status=200)
    except DatabaseError as e:
        return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
