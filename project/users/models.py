from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class PersonnelManager(BaseUserManager):
    def create_user(self, email, official_name, service_number, password=None, **extra_fields):
        """
        Create and return a regular user with the provided official name and service number.
        """
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            official_name=official_name,
            service_number=service_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, official_name, password=None, **extra_fields):
        """
        Create and return a superuser with an email, official name, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, official_name, service_number=None, password=password, **extra_fields)


class ArmOfService(models.Model):
    arm_of_service_id = models.AutoField(primary_key=True)
    arm_of_service_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.arm_of_service_name


class Headquarters(models.Model):
    headquarters_id = models.AutoField(primary_key=True)
    headquarters_name = models.CharField(max_length=100, unique=True)
    arm_of_service = models.ForeignKey(ArmOfService, on_delete=models.SET_NULL, null=True, blank=True, related_name='headquarters')

    def __str__(self):
        return self.headquarters_name


class Directorate(models.Model):
    directorate_id = models.AutoField(primary_key=True)
    directorate_name = models.CharField(max_length=100)
    headquarter = models.ForeignKey(Headquarters, on_delete=models.CASCADE, related_name='directorates')

    def __str__(self):
        return f"{self.directorate_name} ({self.headquarter.headquarters_name})"


class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=100)
    directorate = models.ForeignKey(Directorate, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return f"{self.team_name} ({self.directorate.directorate_name})"


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=100)

    def __str__(self):
        return self.course_name


class Rank(models.Model):
    rank_id = models.AutoField(primary_key=True)
    rank_name = models.CharField(max_length=100)

    def __str__(self):
        return self.rank_name


class Personnel(AbstractBaseUser, PermissionsMixin):
    personnel_id = models.AutoField(primary_key=True)
    official_name = models.CharField(max_length=255, null=True, help_text="Full official name of the user.")
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    service_number = models.CharField(max_length=50, unique=True, null=True)
    rank = models.ForeignKey(Rank, on_delete=models.SET_NULL, null=True, related_name='personnel')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name='personnel')
    directorate = models.ForeignKey(Directorate, on_delete=models.SET_NULL, null=True, blank=True, related_name='personnel')
    arm_of_service = models.ForeignKey(ArmOfService, on_delete=models.SET_NULL, null=True, related_name='personnel')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['official_name']

    objects = PersonnelManager()

    def __str__(self):
        return self.email if self.email else self.official_name



class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    appointment_name = models.CharField(max_length=100)
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='appointments')
    headquarter = models.ForeignKey(Headquarters, on_delete=models.CASCADE, related_name='appointments')

    def __str__(self):
        return f"{self.appointment_name} ({self.headquarter.headquarters_name})"


class PersonnelTeams(models.Model):
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('personnel', 'team'),)
