from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import update_session_auth_hash
from django.db import DatabaseError
from django.utils.http import base36_to_int, int_to_base36
from django.core.mail import send_mail
from django.conf import settings
from project.otp_utils import verify_otp, set_otp, send_otp_via_email
from .models import Personnel
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (UserRegistrationSerializer, UserLoginSerializer, OfficialNameSerializer,
                           UserProfileSerializer, ChangePasswordSerializer, PersonnelSerializer)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from django.contrib.sessions.models import Session
from django.utils import timezone

class RegisterView(APIView):
    """
    Method: POST
    
    Description: Registers a new user in the system.
    
    Request: Requires the user's registration data (e.g., official name, email, phone number, password).
    
    Response:
    Success: Returns a success message and a status code of 201 Created.
    Failure: Returns validation errors with a status code 400 Bad Request.
    """
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            email = serializer.data['email']
            otp = send_otp_via_email(email)

            return Response({
                'status': 'User registered successfully!',
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    Method: POST

    Description: Authenticates a user based on their credentials (e.g., username/password).
    
    Request: Requires the user's official name and password.
    
    Response:
    Success: Returns refresh and access JWT tokens, and a 200 OK status.
    Failure: Returns validation errors with a status code 400 Bad Request.
    """
    
    def post(self, request):
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

class CheckServiceNumberAPIView(APIView):
    """
    Method: POST
    
    Description: Verifies if a given service number exists.
    
    Request: The service number is passed in the body of the request.
    
    Response:
    Success: Returns a success status if the service number exists.
    Failure: Returns an error if the service number is invalid or not found.
    """
    def post(self, request):
        service_number = request.data.get('service_number')
        
        if not service_number:
            return Response({'error': 'Invalid service number format'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Personnel.objects.filter(personnel_id=service_number).exists():
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        return Response({'error': 'Service number not found'}, status=status.HTTP_400_BAD_REQUEST)



class CheckOfficialNameView(APIView):
    """
    Method: POST
    
    Description: Verifies if the given official name exists.
    
    Request: Accepts official name data and validates it using the OfficialNameSerializer.

    Response:
    Success: Returns a message that the official name matches.
    Failure: Returns validation errors.
    """
    def post(self, request):
        serializer = OfficialNameSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'status': 'Official name matches'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckPhoneNumberView(APIView):
    """
    Method: POST

    Description: Checks if the phone number matches the service number, then 
    sends an OTP for verification.
    
    Request: Expects service_number and phone_number in the request body.
    
    Response:
    Success: If the phone number matches, sends an OTP and returns a success status.
    Failure: Returns an error if the phone number does not match or the data is invalid.
    """
    def post(self, request):
        service_number = request.data.get('service_number')
        phone_number = request.data.get('phone_number')
        
        if service_number and phone_number:
            personnel = Personnel.objects.filter(personnel_id=service_number, phone_number=phone_number).first()
            if personnel:
                set_otp(personnel)
                return Response({'status': 'success'}, status=status.HTTP_200_OK)
            return Response({'error': 'Phone number does not match'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyPhoneOTPView(APIView):
    """
    Method: POST
    
    Description: Verifies the phone OTP entered by the user.
    
    Request: Requires the service number and OTP sent to the phone.

    Response:
    Success: If the OTP is valid, returns success.
    Failure: If the OTP is invalid, returns an error.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        service_number = request.data.get('service_number')
        otp = request.data.get('otp')

        if not service_number or not otp:
            return JsonResponse({'error': 'Service number and OTP are required.'}, status=400)

        personnel = Personnel.objects.filter(service_number=service_number).first()
        
        if not personnel:
            return JsonResponse({'error': 'Personnel not found.'}, status=404)

        if verify_otp(personnel, otp):
            return JsonResponse({'success': 'OTP verified successfully.'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid OTP.'}, status=400)


class CheckEmailView(APIView):
    """
    Method: POST

    Description: Checks if the email matches the service number, then sends an OTP for verification.
    
    Request: Expects service_number and email.
    
    Response:
    Success: Sends OTP to the email if it matches.
    Failure: Returns an error if the email does not match or database issues arise.
    """
    def post(self, request):
        service_number = request.data.get('service_number')
        email = request.data.get('email')
        
        if service_number and email:
            try:
                personnel = Personnel.objects.filter(service_number=service_number, email=email).first()
                if personnel:
                    set_otp(personnel)
                    return Response({'status': 'success'}, status=status.HTTP_200_OK)
                return Response({'error': 'Email does not match'}, status=status.HTTP_400_BAD_REQUEST)
            except DatabaseError as e:
                return Response({'error': f'Database error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)



class VerifyEmailOTPView(APIView):
    """
    Method: POST

    Description: Verifies the email OTP entered by the user.
    
    Request: Requires service_number and OTP sent to the email.
    
    Response:
    Success: Returns a success message if OTP is valid.
    Failure: Returns an error if OTP is invalid or if a database error occurs.
    """
    def post(self, request):
        service_number = request.data.get('service_number')
        email_otp = request.data.get('otp')

        if service_number and email_otp:
            try:
                personnel = Personnel.objects.filter(service_number=service_number).first()
                if verify_otp(personnel, email_otp):
                    return Response({'status': 'success'}, status=status.HTTP_200_OK)
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except DatabaseError as e:
                return Response({'error': f'Database error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


class SetPasswordView(APIView):
    """
    Method: POST
    
    Description: Allows the user to set a new password by verifying their official 
    name and password match.
    
    Request: Requires official_name, password, and confirm_password.
    
    Response:
    Success: Password is set successfully if both passwords match.
    Failure: Returns an error if passwords do not match or if data is invalid.
    """
    def post(self, request):
        official_name = request.data.get('official_name')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if password and confirm_password:
            if password == confirm_password:
                try:
                    personnel = Personnel.objects.get(official_name=official_name)
                    personnel.set_password(password)
                    personnel.save()
                    return Response({'status': 'Password set successfully'}, status=status.HTTP_200_OK)
                except Personnel.DoesNotExist:
                    return Response({'error': 'Personnel not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordResetView(APIView):
    """
    Method: POST
    
    Description: Sends an email with a password reset link containing a token and UID.
    
    Request: Requires the user's email to generate the reset link.
    
    Response:
    Success: Sends an email with the reset link.
    Failure: Returns an error if the email is not found or if sending fails.
    """
    def post(self, request):
        email = request.data.get('email')

        if email:
            try:
                personnel = Personnel.objects.get(email=email)
            except Personnel.DoesNotExist:
                return Response({'error': 'Email not found'}, status=status.HTTP_400_BAD_REQUEST)
            except DatabaseError as e:
                return Response({'error': f'Database error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

                return Response({'status': 'Password reset email sent'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'error': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """
    Method: POST

    Description: Resets the user's password using a token and UID sent in the password reset email.
    
    Request: Requires uidb36, token, new_password, and confirm_password.
    
    Response:
    Success: Password is successfully reset.
    Failure: Returns an error if the token is invalid, passwords do not match, 
    or a database error occurs.
    """
    def post(self, request, uidb36, token):
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            personnel_id = base36_to_int(uidb36)
            personnel = Personnel.objects.get(pk=personnel_id)
        except (Personnel.DoesNotExist, ValueError):
            return Response({'error': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(personnel, token):
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            personnel.set_password(new_password)
            personnel.save()
            return Response({'status': 'Password successfully reset'}, status=status.HTTP_200_OK)
        except DatabaseError as e:
            return Response({'error': f'Database error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

class PersonnelListCreateView(generics.ListCreateAPIView):
    """
    Description: The PersonnelListCreateView is responsible for listing all personnel in the 
    system & creating new personnel entries.

    Methods:
    GET: Returns a list of all personnel in the system.
    POST: Creates a new personnel entry with the provided data.
    
    URL:/api/personnel/
    
    HTTP Methods Supported:
    GET: Retrieve the list of personnel.
    POST: Create a new personnel record.
    
    Authentication & Permissions:   
    Authentication: TokenAuthentication is required. This means a valid authentication token 
    needs to be provided in the header.
    Permission: The user must be authenticated (IsAuthenticated) to access this endpoint.
    
    Request Headers (for both GET and POST):
    Authorization: Token
    """
    queryset = Personnel.objects.all()
    serializer_class = PersonnelSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

class PersonnelDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Description: The PersonnelDetailView is responsible for handling the following operations on a 
    specific personnel record:
    1. Retrieve details of a specific personnel by their personnel_id.
    2. Update the personnel details.
    3. Delete a personnel entry.
    
    URL:/api/personnel/<personnel_id>/

    HTTP Methods Supported:
    GET: Retrieve a single personnel entry.
    PUT: Update a personnel entry.
    PATCH: Partially update a personnel entry.
    DELETE: Delete a personnel entry.

    Authentication & Permissions:
    Authentication: TokenAuthentication is required.
    Permission: The user must be authenticated (IsAuthenticated) to access this endpoint.
    
    Request Headers (for GET, PUT, PATCH, DELETE):
    Authorization: Token
    """
    queryset = Personnel.objects.all()
    serializer_class = PersonnelSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

class CheckRegisteredUsers(APIView):
    """
    API view to check which phone numbers belong to registered users.

    Method: GET

    Request:
    - Query parameter `phone_numbers`: A list of phone numbers to check.

    Response:
    - Returns a JSON response containing the registered users with their IDs, phone numbers, official names, service numbers, and emails.    
    """
    permission_classes = [AllowAny]

    def post(self, request):
        service_number = request.data.get('service_number')

        if not service_number:
            return JsonResponse({'error': 'Service number is required.'}, status=400)

        personnel = Personnel.objects.filter(service_number=service_number).first()

        if personnel:
            return JsonResponse({'success': 'Personnel found.'}, status=200)
        else:
            return JsonResponse({'error': 'No personnel found for this service number.'}, status=404)
