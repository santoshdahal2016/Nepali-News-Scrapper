import six
import logging

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import JsonResponse
from django.utils import dateparse, timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from rest_framework import serializers

from app.models.user import User
from app.services.communication_service import send_activation_email, send_reset_password_email

logger = logging.getLogger(__name__)


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
                six.text_type(user.user_id)
                + six.text_type(timestamp)
                + six.text_type(user.is_active)
        )


token_generator = TokenGenerator()


def create_user(user):
    user = User.objects.create_user(
        first_name=user['first_name'],
        last_name=user['last_name'],
        email=user['email'],
        password=user['password'],
        phone=user['phone'],
    )

    token = token_generator.make_token(user)
    send_activation_email(user, token)
    return {"user": user}


def change_password(user, new_password, password_confirm, old_password):
    if not user.check_password(old_password):
        raise serializers.ValidationError(
            {"old_password": "Old password is not correct"}
        )

    user.set_password(new_password)
    user.save()


def forget_password(email):
    user = User.objects.filter(email=email.lower()).first()

    if not user:
        raise serializers.ValidationError(
            {"email": "Email is not associated with any user"}
        )

    else:
        token = token_generator.make_token(user)
        send_reset_password_email(user, token)

        return email


def check_token_validity(token_and_expiry_date, obj):
    try:
        token, expiry_date = token_and_expiry_date.split("_")
        token = force_str(urlsafe_base64_decode(token))
        expiry_date = force_str(urlsafe_base64_decode(expiry_date))
        expiry_date = dateparse.parse_datetime(expiry_date)

        if (not token) or (not expiry_date):
            raise Exception
    except:
        return serializers.ValidationError("Token is invalid or has expired.")

    current_time = timezone.now()

    if current_time > expiry_date:
        return serializers.ValidationError("Token is has expired.")

    if not token_generator.check_token(obj, token):
        raise serializers.ValidationError("Token is invalid or has expired.")
    else:
        return True


def reset_password(obj, token_and_expiry_date, password):

    check_token_validity(token_and_expiry_date, obj)

    if not obj.is_active:
        # If user is inactive, activate user after token verification
        obj.is_active = True
        obj.save()

    obj.set_password(password)
    try:
        obj.save()
    except:
        raise serializers.ValidationError("Unexpected error occurred while saving password")



