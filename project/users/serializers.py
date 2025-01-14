from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
from .models import Personnel
from project.otp_utils import send_otp
import re

User = get_user_model()

def validate_password(password):
    """
    Validate password complexity requirements.
    Must include one uppercase, one lowercase, one number, and one special character.
    """
    if len(password) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise serializers.ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise serializers.ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'\d', password):
        raise serializers.ValidationError("Password must contain at least one digit.")
    if not re.search(r'\W', password):
        raise serializers.ValidationError("Password must contain at least one special character.")
    return password

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    - Validates passwords to ensure they meet complexity requirements.
    - Hashes the password before saving the user.
    - Generates the official_name from first, middle, and last names.
    """
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Personnel
        fields = ['email', 'official_name', 'service_number', 'password', 'confirm_password']

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        validate_password(password)
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data['password'] = make_password(validated_data['password'])
        return Personnel.objects.create(**validated_data)

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    - Authenticates user based on service_number and password.
    """
    service_number = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        service_number = data.get('service_number')
        password = data.get('password')

        user = authenticate(request=self.context.get('request'), service_number=service_number, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid service number or password.")

        data['user'] = user
        return data

class ServiceNumberSerializer(serializers.Serializer):
    """
    Serializer for validating a service number.

    - Checks if the service number exists in the Personnel model.
    """
    service_number = serializers.CharField(max_length=20)

    def validate_service_number(self, value):
        if not Personnel.objects.filter(personnel_id=value).exists():
            raise serializers.ValidationError("Invalid service number.")
        return value

class OfficialNameSerializer(serializers.Serializer):
    """
    Serializer for validating official name based on service number.

    - Retrieves user by service number.
    - Compares expected official name (constructed from first, middle, and last names) with the provided official_name.
    """
    service_number = serializers.CharField(max_length=20)
    official_name = serializers.CharField(max_length=255)

    def validate(self, data):
        service_number = data.get('service_number')
        official_name = data.get('official_name')

        personnel = User.objects.filter(personnel_id=service_number).first()

        if personnel:
            expected_official_name = f"{personnel.first_name[0].upper()}{personnel.middle_name[0].upper() if personnel.middle_name else ''} {personnel.surname}".strip()

            if official_name != expected_official_name:
                raise serializers.ValidationError(f"Official name does not match. Expected: {expected_official_name}")
        else:
            raise serializers.ValidationError("Invalid service number.")
        return data

class PhoneNumberSerializer(serializers.Serializer):
    """
    Serializer for phone number verification.

    - Validates the service number to ensure it exists.
    - Checks if the provided phone number matches the one associated with the service number in the Personnel model.
    - Calls the `send_otp` function to send an OTP (One-Time Password) to the phone number and email address of the user.
    """
    service_number = serializers.CharField(max_length=20)
    phone_number = serializers.CharField(max_length=15)

    def validate(self, data):
        service_number = data.get('service_number')
        phone_number = data.get('phone_number')

        personnel = Personnel.objects.filter(personnel_id=service_number, phone_number=phone_number).first()
        if not personnel:
            raise serializers.ValidationError("Phone number does not match.")

        send_otp(personnel.phone_number, personnel.email)

        return data

class PasswordCreationSerializer(serializers.Serializer):
    """
    Serializer for password creation.

    - Validates the service number to ensure it exists.
    - Validates the password complexity.
    - Checks if passwords match and throws an error if not.
    - Sets the new password using `make_password` and saves the user.
    """
    service_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        validate_password(password)
        return data

    def save(self):
        service_number = self.validated_data['service_number']
        password = self.validated_data['password']

        personnel = Personnel.objects.filter(personnel_id=service_number).first()
        personnel.password = make_password(password)
        personnel.save()

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profiles, including optional profile picture.

    - Inherits from `serializers.ModelSerializer` for automatic field generation.
    - Includes an optional `profile_picture` field for uploading profile images.
    """
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = Personnel
        fields = ('first_name', 'middle_name', 'surname', 'phone_number', 'rank', 'course', 'profile_picture')

    def update(self, instance, validated_data):
        """
        Updates specific user profile fields and handles profile picture upload.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.middle_name = validated_data.get('middle_name', instance.middle_name)
        instance.surname = validated_data.get('surname', instance.surname)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.rank = validated_data.get('rank', instance.rank)
        instance.course = validated_data.get('course', instance.course)
        if 'profile_picture' in validated_data:
            instance.profile_picture = validated_data['profile_picture']
        instance.save()
        return instance

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing a user's password.

    - Requires both the old and new password.
    - Validates the new password for complexity requirements.
    - Compares the old password with the stored password.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        return validate_password(value)

    def validate(self, data):
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if old_password == new_password:
            raise serializers.ValidationError("The new password must be different from the old password.")
        
        return data

class PersonnelSerializer(serializers.ModelSerializer):
    """
    A serializer for the Personnel model that includes all fields.
    """
    class Meta:
        model = Personnel
        fields = '__all__'

class RegisteredUserSerializer(serializers.ModelSerializer):
    """
    A serializer for the Personnel model that includes only specific fields 
    relevant for registered users.
    """
    class Meta:
        model = Personnel
        fields = ['id', 'phone_number', 'official_name', 'service_number', 'email']
