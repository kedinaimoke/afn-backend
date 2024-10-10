from django.contrib.auth.backends import ModelBackend
from .models import Personnel

class OfficialNameBackend(ModelBackend):
    def authenticate(self, request, official_name=None, password=None, **kwargs):
        try:
            user = Personnel.objects.get(official_name=official_name)
            if user.check_password(password):
                return user
        except Personnel.DoesNotExist:
            return None
