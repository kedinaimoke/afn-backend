from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
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
from .serializers import UserRegistrationSerializer, UserLoginSerializer, OfficialNameSerializer, UserProfileSerializer, ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash
import json

@api_view(['POST'])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'status': 'User registered successfully!'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@require_http_methods(["POST"])
def check_service_number(request):
    data = json.loads(request.body)
    service_number = data.get('service_number')

    if service_number:
        if Personnel.objects.filter(personnel_id=service_number).exists():
            return JsonResponse({'status': 'success'}, status=200)
        return JsonResponse({'error': 'Service number not found'}, status=400)
    return JsonResponse({'error': 'Invalid service number format'}, status=400)


@require_http_methods(["POST"])
def check_official_name(request):
    data = json.loads(request.body)
    serializer = OfficialNameSerializer(data=data)

    if serializer.is_valid():
        return JsonResponse({'status': 'Official name matches'}, status=200)
    return JsonResponse(serializer.errors, status=400)


@require_http_methods(["POST"])
def check_phone_number(request):
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

from django.contrib.auth import update_session_auth_hash
from .serializers import UserProfileSerializer, ChangePasswordSerializer

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    GET - Retrieve profile
    PUT - Update profile
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
    personnel = request.user
    serializer = UserProfileSerializer(personnel, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({'status': 'Profile picture updated successfully'}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
