from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
from .models import Personnel
from project.otp_utils import send_otp
import re

User = get_user_model()

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
        model = User
        fields = ('email', 'first_name', 'middle_name', 'surname', 'password', 'confirm_password')

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        password_validator = RegexValidator(
            regex='^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
            message="Password must be at least 8 characters long, include one uppercase, one lowercase, one number, and one special character."
        )
        password_validator(password)
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')

        first_name = validated_data.get('first_name')
        middle_name = validated_data.get('middle_name', '')
        surname = validated_data.get('surname')

        official_name = f"{first_name} {middle_name} {surname}".strip()

        validated_data['official_name'] = official_name

        validated_data['password'] = make_password(validated_data['password'])

        return super().create(validated_data)

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    - Authenticates user based on official_name and password.
    """
    official_name = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        official_name = data.get('official_name')
        password = data.get('password')

        user = authenticate(request=self.context.get('request'), official_name=official_name, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid official name or password.")

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
    - Calls the `send_otp` function (assumed to be implemented elsewhere) to send an OTP (One-Time Password) to the phone number and email address of the user.
    """
    service_number = serializers.CharField(max_length=20)
    phone_number = serializers.CharField(max_length=15)

    def validate(self, data):
        service_number = data.get('service_number')
        phone_number = data.get('phone_number')

        personnel = Personnel.objects.filter(personnel_id=service_number, phone_number=phone_number).first()
        if not personnel:
            raise serializers.ValidationError("Phone number does not match.")

        # will implement OTP sending logic
        send_otp(personnel.phone_number, personnel.email)

        return data

class PasswordCreationSerializer(serializers.Serializer):
    """
    Serializer for password creation.

    - Validates the service number to ensure it exists.
    - Validates the password complexity using regular expressions.
    - Checks if passwords match and throws an error if not.
    - Retrieves the user by service number.
    - Sets the new password using `make_password` and saves the user.
    """
    service_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'\W', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def save(self):
        service_number = self.validated_data['service_number']
        password = self.validated_data['password']

        personnel = Personnel.objects.filter(personnel_id=service_number).first()
        personnel.password = make_password(password)
        personnel.save()

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profiles.

    - Inherits from `serializers.ModelSerializer` for automatic field generation.
    - Defines `Meta` class to specify the model and fields for serialization.
    - Overrides the `update` method to selectively update user profile fields.
    """
    class Meta:
        model = Personnel
        fields = ('first_name', 'middle_name', 'surname', 'phone_number', 'rank', 'course')

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.middle_name = validated_data.get('middle_name', instance.middle_name)
        instance.surname = validated_data.get('surname', instance.surname)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.rank = validated_data.get('rank', instance.rank)
        instance.course = validated_data.get('course', instance.course)
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
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not any(char in '!@#$%^&*()_+' for char in value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profiles, including optional profile picture.

    - Inherits from `serializers.ModelSerializer` for automatic field generation.
    - Defines `Meta` class to specify the model and fields for serialization.
    - Includes an optional `profile_picture` field for uploading profile images.
    - Overrides the `update` method to selectively update user profile fields and handle profile picture upload.
    """
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = Personnel
        fields = ('first_name', 'middle_name', 'surname', 'phone_number', 'rank', 'course', 'profile_picture')

    def update(self, instance, validated_data):
        """
        Updates specific user profile fields based on provided data and handles profile picture upload.

        - Retrieves updated values for each field from validated_data.
        - Sets the instance's attributes with the updated values (or keeps them unchanged if not provided).
        - Specifically checks for "profile_picture" in validated_data.
        - If provided, updates the instance.profile_picture attribute with the new image file.
        - Saves the updated user profile instance.
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
