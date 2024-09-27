from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import UserCreationForm, UserChangeForm

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('get_full_name', 'get_service_number', 'get_phone_number', 'get_email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('staff__official_name', 'staff__service_number', 'staff__phone_number', 'staff__email')
    ordering = ('staff__official_name',)

    fieldsets = (
        (None, {'fields': ('staff', 'password')}),  # Link to the Staff model
        ('Personal info', {'fields': ('staff__service_number', 'staff__phone_number', 'staff__email')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('staff', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    def get_full_name(self, obj):
        return obj.staff.official_name
    get_full_name.short_description = 'Official Name'

    def get_service_number(self, obj):
        return obj.staff.service_number
    get_service_number.short_description = 'Service Number'

    def get_phone_number(self, obj):
        return obj.staff.phone_number
    get_phone_number.short_description = 'Phone Number'

    def get_email(self, obj):
        return obj.staff.email
    get_email.short_description = 'Email'

admin.site.register(User, UserAdmin)
