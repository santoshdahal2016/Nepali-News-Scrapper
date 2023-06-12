import threading
import datetime as dt
from environs import Env
from django.conf import settings
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode

env = Env()
env.read_env()

DASHBOARD_FRONTEND_DOMAIN = env("DASHBOARD_FRONTEND_DOMAIN")


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


def send_activation_email(user, token):
    expiry_date = timezone.now() + dt.timedelta(days=5)
    email_subject = "Activate your account"
    email_body = render_to_string(
        "activate.html",
        {
            "user": user,
            "domain": DASHBOARD_FRONTEND_DOMAIN,
            "uid": urlsafe_base64_encode(force_bytes(user.user_id)),
            "token": urlsafe_base64_encode(force_bytes(token))
            + "_"
            + urlsafe_base64_encode(force_bytes(str(expiry_date))),
        },
    )

    email = EmailMultiAlternatives(
        subject=email_subject,
        from_email=settings.EMAIL_FROM_USER,
        to=[user.email],
    )
    email.attach_alternative(email_body, "text/html")

    EmailThread(email).start()


def send_reset_password_email(user, token):
    expiry_date = timezone.now() + dt.timedelta(days=5)
    email_subject = "Reset password"
    email_body = render_to_string(
        "reset-password.html",
        {
            "user": user,
            "domain": DASHBOARD_FRONTEND_DOMAIN,
            "uid": urlsafe_base64_encode(force_bytes(user.user_id)),
            "token": urlsafe_base64_encode(force_bytes(token))
            + "_"
            + urlsafe_base64_encode(force_bytes(str(expiry_date))),
        },
    )

    email = EmailMultiAlternatives(
        subject=email_subject,
        from_email=settings.EMAIL_FROM_USER,
        to=[user.email],
    )
    email.attach_alternative(email_body, "text/html")

    EmailThread(email).start()

