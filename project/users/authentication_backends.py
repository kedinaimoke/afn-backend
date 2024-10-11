from django.contrib.auth.backends import ModelBackend
from .models import Personnel

"""
Purpose:
  This backend is used to authenticate a user using their `official_name` (from the `Personnel` model) instead of the default `username` provided by Django. It extends Django's `ModelBackend` and overrides the `authenticate()` method.

Methods:
1. authenticate(self, request, official_name=None, password=None, \*\*kwargs):
    - Parameters:
      - `request`: The HTTP request object (automatically passed by Django when the user attempts to authenticate).
      - `official_name`: The official name of the user, which is passed as part of the authentication process.
      - `password`: The password that the user provides.
      - `\*\*kwargs`: Additional keyword arguments, although these are not used directly in this function.
    
    - Logic:
      - The method tries to retrieve a `Personnel` object where the `official_name` matches the provided `official_name`.
      - If a user with the matching `official_name` is found, the backend checks whether the provided password is correct by using the `check_password()` method (a built-in Django method that verifies hashed passwords).
      - If the password is valid, the `Personnel` object (user) is returned, allowing the authentication process to proceed.
      - If no user with the given `official_name` is found or the password is incorrect, `None` is returned, indicating that authentication failed.
    
    - Returns: 
      - The authenticated `Personnel` object (user) if the `official_name` and `password` are correct.
      - `None` if the user is not found or the password is incorrect.

How It Works:
- When a user tries to log in, instead of using the `username` field, they will provide their `official_name` (a custom field in the `Personnel` model).
- The custom backend will query the `Personnel` model using the provided `official_name`. If a matching user is found and the password is correct, the user is authenticated.
- This custom backend would typically be registered in Django's settings under the `AUTHENTICATION_BACKENDS` setting to replace or supplement the default backend.
"""
class OfficialNameBackend(ModelBackend):
    def authenticate(self, request, official_name=None, password=None, **kwargs):
        try:
            user = Personnel.objects.get(official_name=official_name)
            if user.check_password(password):
                return user
        except Personnel.DoesNotExist:
            return None
