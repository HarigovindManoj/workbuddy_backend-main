from django.db import models
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import os
from django.utils.deconstruct import deconstructible
from phonenumber_field.modelfields import PhoneNumberField

@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid.uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join('hospital/', filename)

class CustomAccountManager(BaseUserManager):
    def create_user(self, email, password, **other_fields):

        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault('role', 'ADMIN')
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must be assigned to is_active=True'))
        if other_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must be assigned to is_active=True'))

        if not email:
            raise ValueError(_('You must provide an email address'))

        return self.create_user(email, password, **other_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        MANAGER = "MANAGER", 'Manager'
        EMPLOYEE = "EMPLOYEE", 'Employee'

    base_role = Role.ADMIN

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=50, choices=Role.choices, default=Role.EMPLOYEE)
    start_date = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class EmployeeManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.EMPLOYEE)

class Employee(User):
    base_role = User.Role.EMPLOYEE

    class Meta:
        proxy = True

    objects = EmployeeManager()


class ManagerManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.MANAGER)

class Manager(User):
    base_role = User.Role.MANAGER

    class Meta:
        proxy = True

    objects = ManagerManager()

class AdminManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.ADMIN)

class Admin(User):
    base_role = User.Role.ADMIN

    class Meta:
        proxy = True

    objects = AdminManager()

class Skill(models.Model):
    name = models.CharField(max_length=225)

    def __str__(self):
        return self.name

class UserDetail(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = "M", 'Male'
        FEMALE = "F", 'Female'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=225)
    last_name = models.CharField(max_length=225)
    address = models.TextField()
    skillset = models.ManyToManyField(Skill)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    pic = models.ImageField(upload_to=PathAndRename('users/'), blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GenderChoices.choices, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    phone = PhoneNumberField(blank=True, null=True)

    def __str__(self):
        return self.first_name
    
    def get_pic(self):
      if self.pic:
          return 'http://127.0.0.1:8000' + self.pic.url
      return ''