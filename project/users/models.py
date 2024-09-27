from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Headquarters(models.Model):
    headquarter_id = models.AutoField(primary_key=True)
    headquarter_name = models.CharField(unique=True, max_length=255)

    class Meta:
        db_table = 'headquarters'

    def __str__(self):
        return self.headquarter_name


class Directorate(models.Model):
    directorate_id = models.AutoField(primary_key=True)
    directorate_name = models.CharField(max_length=255)
    headquarter = models.ForeignKey(Headquarters, on_delete=models.CASCADE)

    class Meta:
        db_table = 'directorates'

    def __str__(self):
        return self.directorate_name


class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=255)
    directorate = models.ForeignKey(Directorate, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'teams'

    def __str__(self):
        return self.team_name


class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    service_number = models.CharField(max_length=15, unique=True)
    official_name = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=255, unique=True)
    headquarter = models.ForeignKey(Headquarters, on_delete=models.SET_NULL, blank=True, null=True)
    directorate = models.ForeignKey(Directorate, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'staff'

    def __str__(self):
        return self.official_name


class UserManager(BaseUserManager):
    def create_user(self, staff, password=None, **extra_fields):
        if not staff.service_number:
            raise ValueError('The Service Number field must be set')

        user = self.model(staff=staff, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, staff, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(staff, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model that is linked to the Staff model via a One-to-One relationship.
    Authentication is handled by this User model, while staff data is stored in the Staff model.
    """
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, related_name="user")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'staff'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.staff.official_name

    def get_short_name(self):
        return self.staff.first_name or self.get_full_name()

    def __str__(self):
        return self.get_full_name()
