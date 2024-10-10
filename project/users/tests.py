from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Personnel
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

class UserProfileTests(APITestCase):

    def setUp(self):
        # Create a test user
        self.service_number = "123456"  # Add a service number
        print(f"Creating test user with service number: {self.service_number}")  # Debug statement
        self.user = User.objects.create_user(
            email="testuser@example.com",
            first_name="John",
            middle_name="Doe",
            surname="Smith",
            service_number=self.service_number,  # Provide the service number
            password=make_password("Password@123")
        )
        self.personnel = Personnel.objects.create(
            personnel_id=self.user.personnel_id,
            first_name="John",
            middle_name="Doe",
            surname="Smith",
            phone_number="08012345678",
            email="testuser@example.com"
        )
        print(f"Created test personnel with ID: {self.personnel.personnel_id}")  # Debug statement

        self.client.login(official_name="John D Smith", password="Password@123")

    def test_registration(self):
        url = reverse('register')  # Registration URL
        data = {
            'email': "newuser@example.com",
            'first_name': "Jane",
            'middle_name': "A",
            'surname': "Doe",
            'password': "Password@123",
            'confirm_password': "Password@123"
        }
        print(f"Testing registration with email: {data['email']}")  # Debug statement
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        url = reverse('login')  # Login URL
        data = {
            'official_name': "John D Smith",
            'password': "Password@123"
        }
        print(f"Testing login for official name: {data['official_name']}")  # Debug statement
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)  # Assuming token authentication

    def test_change_password(self):
        url = reverse('change_password')  # Change password URL
        data = {
            'old_password': "Password@123",
            'new_password': "NewPassword@123"
        }
        print(f"Testing password change for user: {self.user.email}")  # Debug statement
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_profile(self):
        url = reverse('user_profile')  # User profile URL
        print("Testing profile view")  # Debug statement
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], "John")
        self.assertEqual(response.data['surname'], "Smith")

    def test_invalid_login(self):
        url = reverse('login')  # Login URL
        data = {
            'official_name': "Invalid Name",
            'password': "Password@123"
        }
        print(f"Testing invalid login for official name: {data['official_name']}")  # Debug statement
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_phone_number_verification(self):
        url = reverse('check_phone_number')  # Check phone number URL
        data = {
            'service_number': self.service_number,  # Use the service number from setUp
            'phone_number': "08012345678"
        }
        print(f"Testing phone number verification for service number: {data['service_number']}")  # Debug statement
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_request(self):
        url = reverse('request_password_reset')  # Password reset request URL
        data = {
            'service_number': self.service_number,  # Use the service number from setUp
        }
        print(f"Testing password reset request for service number: {data['service_number']}")  # Debug statement
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset(self):
        url = reverse('reset_password', kwargs={'uidb36': 'uidb36_example', 'token': 'token_example'})  # Password reset URL
        data = {
            'password': "NewPassword@123",
            'confirm_password': "NewPassword@123"
        }
        print("Testing password reset")  # Debug statement
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_official_name_validation(self):
        url = reverse('check_official_name')  # Check official name URL
        data = {
            'service_number': self.service_number,  # Use the service number from setUp
            'official_name': "John D Smith"
        }
        print(f"Testing official name validation for service number: {data['service_number']}")  # Debug statement
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
