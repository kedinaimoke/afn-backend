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

    def test_check_service_number_valid(self):
        """Test the check_service_number endpoint with a valid service number"""
        url = reverse('check_service_number')
        data = {
            'service_number': self.service_number
        }
        print(f"Testing valid service number: {data['service_number']}")  # Debug statement
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success'})

    def test_check_service_number_invalid(self):
        """Test the check_service_number endpoint with an invalid service number"""
        url = reverse('check_service_number')
        data = {
            'service_number': "654321"  # Invalid service number
        }
        print(f"Testing invalid service number: {data['service_number']}")  # Debug statement
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Service number not found'})

    def test_check_service_number_missing(self):
        """Test the check_service_number endpoint with no service number"""
        url = reverse('check_service_number')
        data = {}
        print("Testing missing service number")  # Debug statement
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Invalid service number format'})
    
    def test_check_registered_users(self):
        """Test the check_registered_users endpoint with valid phone numbers"""
        url = reverse('check_registered_users')
        phone_numbers = ["08012345678", "08087654321"]
        query_string = f"?phone_numbers={','.join(phone_numbers)}"
        print(f"Testing with phone numbers: {phone_numbers}")  # Debug statement
        response = self.client.get(f"{url}{query_string}")

        # Expected response data
        expected_data = {
            "registered_users": [
                {
                    "id": self.personnel1.id,
                    "phone_number": self.personnel1.phone_number,
                    "name": self.personnel1.official_name,
                    "service_number": self.personnel1.service_number,
                    "email": self.personnel1.email,
                },
                {
                    "id": self.personnel2.id,
                    "phone_number": self.personnel2.phone_number,
                    "name": self.personnel2.official_name,
                    "service_number": self.personnel2.service_number,
                    "email": self.personnel2.email,
                }
            ]
        }
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, expected_data)

    def test_check_registered_users_partial_match(self):
        """Test the check_registered_users endpoint with one matching and one non-matching phone number"""
        url = reverse('check_registered_users')
        phone_numbers = ["08012345678", "08099999999"]  # One valid, one invalid
        query_string = f"?phone_numbers={','.join(phone_numbers)}"
        print(f"Testing with partial phone numbers: {phone_numbers}")  # Debug statement
        response = self.client.get(f"{url}{query_string}")

        # Expected response data (only matching personnel1)
        expected_data = {
            "registered_users": [
                {
                    "id": self.personnel1.id,
                    "phone_number": self.personnel1.phone_number,
                    "name": self.personnel1.official_name,
                    "service_number": self.personnel1.service_number,
                    "email": self.personnel1.email,
                }
            ]
        }
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, expected_data)

    def test_check_registered_users_no_match(self):
        """Test the check_registered_users endpoint with no matching phone numbers"""
        url = reverse('check_registered_users')
        phone_numbers = ["08099999999", "08088888888"]  # No valid phone numbers
        query_string = f"?phone_numbers={','.join(phone_numbers)}"
        print(f"Testing with non-matching phone numbers: {phone_numbers}")  # Debug statement
        response = self.client.get(f"{url}{query_string}")

        # Expected response data (no users found)
        expected_data = {"registered_users": []}
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, expected_data)
    
    def test_check_email_success(self):
        """Test the check_email endpoint with matching service number and email"""
        url = reverse('check_email')
        data = {
            'service_number': self.personnel.service_number,
            'email': self.personnel.email
        }
        print(f"Testing email check with service number: {data['service_number']}, email: {data['email']}")  # Debug statement
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success'})

    def test_check_email_invalid_email(self):
        """Test the check_email endpoint with a non-matching email"""
        url = reverse('check_email')
        data = {
            'service_number': self.personnel.service_number,
            'email': 'wrong.email@example.com'  # Invalid email
        }
        print(f"Testing email check with non-matching email: {data['email']}")  # Debug statement
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Email does not match'})

    def test_check_email_invalid_data(self):
        """Test the check_email endpoint with missing data"""
        url = reverse('check_email')
        data = {
            'service_number': '',  # Missing service number
            'email': ''
        }
        print("Testing email check with invalid data")  # Debug statement
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Invalid data'})

    def test_check_email_database_error(self):
        """Test the check_email endpoint when a database error occurs"""
        url = reverse('check_email')
        data = {
            'service_number': self.personnel.service_number,
            'email': self.personnel.email
        }
        print("Testing email check with database error")  # Debug statement

        # Simulate a database error by patching the Personnel.objects.filter method
        with self.assertRaises(DatabaseError):
            with patch('app.models.Personnel.objects.filter', side_effect=DatabaseError('Test DB error')):
                response = self.client.post(url, data=json.dumps(data), content_type='application/json')
                self.assertEqual(response.status_code, 500)
                self.assertJSONEqual(response.content, {'error': 'Database error: Test DB error'})

    def test_set_password_success(self):
        """Test the set_password endpoint with matching passwords"""
        url = reverse('set_password')
        data = {
            'official_name': self.personnel.official_name,
            'password': "NewPassword@123",
            'confirm_password': "NewPassword@123"
        }
        print(f"Testing password set with official name: {data['official_name']}")  # Debug statement
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'Password set successfully'})

        # Check that the password was updated correctly
        self.personnel.refresh_from_db()
        self.assertTrue(check_password("NewPassword@123", self.personnel.password))

    def test_set_password_mismatch(self):
        """Test the set_password endpoint with non-matching passwords"""
        url = reverse('set_password')
        data = {
            'official_name': self.personnel.official_name,
            'password': "NewPassword@123",
            'confirm_password': "DifferentPassword@123"
        }
        print(f"Testing password set with mismatching passwords")  # Debug statement
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Passwords do not match'})

    def test_set_password_invalid_data(self):
        """Test the set_password endpoint with missing data"""
        url = reverse('set_password')
        data = {
            'official_name': self.personnel.official_name,
            'password': "",  # Missing password
            'confirm_password': ""
        }
        print(f"Testing password set with invalid data")  # Debug statement
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Invalid data'})

    def test_set_password_user_not_found(self):
        """Test the set_password endpoint with non-existing official name"""
        url = reverse('set_password')
        data = {
            'official_name': "Nonexistent User",  # Invalid official name
            'password': "NewPassword@123",
            'confirm_password': "NewPassword@123"
        }
        print(f"Testing password set with non-existing official name")  # Debug statement
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {'error': 'User not found'})
