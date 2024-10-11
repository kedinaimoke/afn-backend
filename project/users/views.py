from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import update_session_auth_hash
from django.db import IntegrityError, DatabaseError
from django.utils.http import base36_to_int, int_to_base36
from django.core.mail import send_mail
from django.conf import settings
from project.otp_utils import generate_otp, send_otp, verify_otp, set_otp
from .models import Personnel
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .serializers import (UserRegistrationSerializer, UserLoginSerializer, OfficialNameSerializer,
                           UserProfileSerializer, ChangePasswordSerializer)
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash
from django.contrib.sessions.models import Session
from django.utils import timezone
import json

@api_view(['POST'])
def register(request):
    """
    Method: POST
    
    Description: Registers a new user in the system.
    
    Request: Requires the user's registration data (e.g., official name, email, phone number, password).
    
    Response:
    Success: Returns a success message and a status code of 201 Created.
    Failure: Returns validation errors with a status code 400 Bad Request.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'status': 'User registered successfully!'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    """
    Method: POST

    Description: Authenticates a user based on their credentials (e.g., username/password).
    
    Request: Requires the user's official name and password.
    
    Response:
    Success: Returns refresh and access JWT tokens, and a 200 OK status.
    Failure: Returns validation errors with a status code 400 Bad Request.
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']

        existing_sessions = Session.objects.filter(expire_date__gt=timezone.now())
        for session in existing_sessions:
            if session.get_decoded().get('_auth_user_id') == str(user.id):
                session.delete()

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@require_http_methods(["POST"])
def check_service_number(request):
    """
    Method: POST
    
    Description: Verifies if a given service number exists.
    
    Request: The service number is passed in the body of the request.
    
    Response:
    Success: Returns a success status if the service number exists.
    Failure: Returns an error if the service number is invalid or not found.
    """
    data = json.loads(request.body)
    service_number = data.get('service_number')

    if service_number:
        if Personnel.objects.filter(personnel_id=service_number).exists():
            return JsonResponse({'status': 'success'}, status=200)
        return JsonResponse({'error': 'Service number not found'}, status=400)
    return JsonResponse({'error': 'Invalid service number format'}, status=400)


@require_http_methods(["POST"])
def check_official_name(request):
    """
    Method: POST
    
    Description: Verifies if the given official name exists.
    
    Request: Accepts official name data and validates it using the OfficialNameSerializer.

    Response:
    Success: Returns a message that the official name matches.
    Failure: Returns validation errors.
    """
    data = json.loads(request.body)
    serializer = OfficialNameSerializer(data=data)

    if serializer.is_valid():
        return JsonResponse({'status': 'Official name matches'}, status=200)
    return JsonResponse(serializer.errors, status=400)


@require_http_methods(["POST"])
def check_phone_number(request):
    """
    Method: POST

    Description: Checks if the phone number matches the service number, then sends an OTP for verification.
    
    Request: Expects service_number and phone_number in the request body.
    
    Response:
    Success: If the phone number matches, sends an OTP and returns a success status.
    Failure: Returns an error if the phone number does not match or the data is invalid.
    """
    data = json.loads(request.body)
    service_number = data.get('service_number')
    phone_number = data.get('phone_number')

    if service_number and phone_number:
        personnel = Personnel.objects.filter(personnel_id=service_number, phone_number=phone_number).first()
        if personnel:
            set_otp(personnel)
            return JsonResponse({'status': 'success'}, status=200)
        return JsonResponse({'error': 'Phone number does not match'}, status=400)
    return JsonResponse({'error': 'Invalid data'}, status=400)


@require_http_methods(["POST"])
def verify_phone_otp(request):
    """
    Method: POST
    
    Description: Verifies the phone OTP entered by the user.
    
    Request: Requires the service number and OTP sent to the phone.

    Response:
    Success: If the OTP is valid, returns success.
    Failure: If the OTP is invalid, returns an error.
    """
    data = json.loads(request.body)
    service_number = data.get('service_number')
    phone_otp = data.get('phone_otp')

    if service_number and phone_otp:
        personnel = Personnel.objects.filter(personnel_id=service_number).first()
        if personnel and verify_otp(personnel, phone_otp):
            return JsonResponse({'status': 'success'}, status=200)
        return JsonResponse({'error': 'Invalid OTP'}, status=400)
    return JsonResponse({'error': 'Invalid data'}, status=400)


@require_http_methods(["POST"])
def check_email(request):
    """
    Method: POST

    Description: Checks if the email matches the service number, then sends an OTP for verification.
    
    Request: Expects service_number and email.
    
    Response:
    Success: Sends OTP to the email if it matches.
    Failure: Returns an error if the email does not match or database issues arise.
    """
    data = json.loads(request.body)
    service_number = data.get('service_number')
    email = data.get('email')

    if service_number and email:
        try:
            personnel = Personnel.objects.filter(service_number=service_number, email=email).first()
            if personnel:
                set_otp(personnel)
                return JsonResponse({'status': 'success'}, status=200)
            return JsonResponse({'error': 'Email does not match'}, status=400)
        except DatabaseError as e:
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid data'}, status=400)


@require_http_methods(["POST"])
def verify_email_otp(request):
    """
    Method: POST

    Description: Verifies the email OTP entered by the user.
    
    Request: Requires service_number and OTP sent to the email.
    
    Response:
    Success: Returns a success message if OTP is valid.
    Failure: Returns an error if OTP is invalid or if a database error occurs.
    """
    data = json.loads(request.body)
    service_number = data.get('service_number')
    email_otp = data.get('email_otp')

    if service_number and email_otp:
        try:
            personnel = Personnel.objects.filter(service_number=service_number).first()
            if verify_otp(personnel, email_otp):
                return JsonResponse({'status': 'success'}, status=200)
            return JsonResponse({'error': 'Invalid OTP'}, status=400)
        except DatabaseError as e:
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid data'}, status=400)


@require_http_methods(["POST"])
def set_password(request):
    """
    Method: POST
    
    Description: Allows the user to set a new password by verifying their official name and password match.
    
    Request: Requires official_name, password, and confirm_password.
    
    Response:
    Success: Password is set successfully if both passwords match.
    Failure: Returns an error if passwords do not match or if data is invalid.
    """
    data = json.loads(request.body)
    official_name = data.get('official_name')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if password and confirm_password:
        if password == confirm_password:
            personnel = Personnel.objects.get(official_name=official_name)
            personnel.password = make_password(password)
            personnel.save()
            return JsonResponse({'status': 'Password set successfully'}, status=200)
        return JsonResponse({'error': 'Passwords do not match'}, status=400)
    return JsonResponse({'error': 'Invalid data'}, status=400)


@require_http_methods(["POST"])
def request_password_reset(request):
    """
    Method: POST
    
    Description: Sends an email with a password reset link containing a token and UID.
    
    Request: Requires the user's email to generate the reset link.
    
    Response:
    Success: Sends an email with the reset link.
    Failure: Returns an error if the email is not found or if sending fails.
    """
    data = json.loads(request.body)
    email = data.get('email')

    if email:
        try:
            personnel = Personnel.objects.get(email=email)
        except Personnel.DoesNotExist:
            return JsonResponse({'error': 'Email not found'}, status=400)
        except DatabaseError as e:
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)

        try:
            token = default_token_generator.make_token(personnel)
            uid = int_to_base36(personnel.pk)
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
    return JsonResponse({'error': 'Invalid email'}, status=400)


@require_http_methods(["POST"])
def reset_password(request, uidb36, token):
    """
    Method: POST

    Description: Resets the user's password using a token and UID sent in the password reset email.
    
    Request: Requires uidb36, token, new_password, and confirm_password.
    
    Response:
    Success: Password is successfully reset.
    Failure: Returns an error if the token is invalid, passwords do not match, or a database error occurs.
    """
    data = json.loads(request.body)
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if new_password != confirm_password:
        return JsonResponse({'error': 'Passwords do not match'}, status=400)

    try:
        personnel_id = int(base36_to_int(uidb36))
        personnel = Personnel.objects.get(pk=personnel_id)
    except (Personnel.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Invalid link'}, status=400)

    if not default_token_generator.check_token(personnel, token):
        return JsonResponse({'error': 'Invalid or expired token'}, status=400)

    try:
        personnel.set_password(new_password)
        personnel.save()
        return JsonResponse({'status': 'Password successfully reset'}, status=200)
    except DatabaseError as e:
        return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Method: GET, PUT

    Description:
    GET: Fetches the user's profile.
    PUT: Updates the user's profile information.
    
    Request: For PUT, user profile data is passed in the body.
    
    Response:
    Success: Profile data or updated profile is returned.
    Failure: Returns errors if the profile is not found or if the data is invalid.
    """
    try:
        personnel = request.user
        if request.method == 'GET':
            serializer = UserProfileSerializer(personnel)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = UserProfileSerializer(personnel, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': 'Profile updated successfully'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Personnel.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Method: PUT

    Description: Allows authenticated users to change their password.
    
    Request: Requires the old password and new password.
    
    Response:
    Success: Password is changed and session is updated.
    Failure: Returns an error if the old password is incorrect or data is invalid.
    """
    serializer = ChangePasswordSerializer(data=request.data)

    if serializer.is_valid():
        personnel = request.user
        if not personnel.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        personnel.set_password(serializer.validated_data['new_password'])
        personnel.save()

        update_session_auth_hash(request, personnel)

        return Response({'status': 'Password updated successfully'}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile_picture(request):
    """
    Method: PUT

    Description: Updates the user's profile picture.
    
    Request: Requires a new profile picture.
    
    Response:
    Success: Profile picture is updated.
    Failure: Returns errors if validation fails.
    """
    personnel = request.user
    serializer = UserProfileSerializer(personnel, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({'status': 'Profile picture updated successfully'}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
