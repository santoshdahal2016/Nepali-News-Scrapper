import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of username.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


# User model for login
class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model based on AbstractBaseUser of Django"""

    user_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField(unique=True)
    phone = models.TextField(null=False)
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)


    # Users with unverified emails will have is_active false
    is_active = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    # By default, Django uses `username` field for logging in users.
    # We redefine it to our email field which we use for logging in the users
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # CustomUserManager manages the user objects during queries
    objects = CustomUserManager()

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        app_label = "app"

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name
