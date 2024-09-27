from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm, UserChangeForm as BaseUserChangeForm
from .models import User, Staff
import re

class ServiceNumberForm(forms.Form):
    service_number = forms.CharField(max_length=15, required=True)

    def clean_service_number(self):
        service_number = self.cleaned_data['service_number']
        if not re.match(r'^[A-Z]{3}/[A-Z]{2,3}/\d{6,}$', service_number):
            raise forms.ValidationError("Invalid service number format. Expected format: XYZ/AA/1234567 or XYZ/AAA/1234567.")
        return service_number


class OfficialNameForm(forms.Form):
    service_number = forms.CharField(max_length=20, required=True)
    official_name = forms.CharField(max_length=255, required=True)

    def clean(self):
        cleaned_data = super().clean()
        service_number = cleaned_data.get('service_number')
        official_name = cleaned_data.get('official_name')

        if not Staff.objects.filter(service_number=service_number, official_name=official_name).exists():
            raise forms.ValidationError("The official name and service number do not match any records")

        return cleaned_data


class PhoneNumberForm(forms.Form):
    service_number = forms.CharField(max_length=20, required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    def clean(self):
        cleaned_data = super().clean()
        service_number = cleaned_data.get('service_number')
        phone_number = cleaned_data.get('phone_number')

        if not Staff.objects.filter(service_number=service_number, phone_number=phone_number).exists():
            raise forms.ValidationError("The phone number and service number do not match any records")

        return cleaned_data


class OTPForm(forms.Form):
    phone_otp = forms.CharField(max_length=6, required=True)


class EmailForm(forms.Form):
    service_number = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        service_number = cleaned_data.get('service_number')
        email = cleaned_data.get('email')

        if not Staff.objects.filter(service_number=service_number, email=email).exists():
            raise forms.ValidationError("The email and service number do not match any records")

        return cleaned_data


class SetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ('staff',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('staff',)
