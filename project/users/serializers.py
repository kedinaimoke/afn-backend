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
    service_number = serializers.CharField(max_length=20)

    def validate_service_number(self, value):
        if not Personnel.objects.filter(personnel_id=value).exists():
            raise serializers.ValidationError("Invalid service number.")
        return value
    
class OfficialNameSerializer(serializers.Serializer):
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
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = Personnel
        fields = ('first_name', 'middle_name', 'surname', 'phone_number', 'rank', 'course', 'profile_picture')

    def update(self, instance, validated_data):
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
