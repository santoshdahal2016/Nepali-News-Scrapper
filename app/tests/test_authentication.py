import re
import time
from django.test import TestCase
from django.urls import reverse
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from app.models.user import User


class AuthenticationTest(APITestCase):
    user_data = {
        "user": {
            "email": "test@test.com",
            "password": "password342",
            "password_confirm": "password342",
            "phone": "9811316068",
            "first_name": "Test",
            "last_name": "User",
        },
    }

    def setUp(self):
        self.mail = mail
        self.login_url = reverse("login")
        self.logout_url = reverse("auth_logout")
        # self.change_password_url = reverse('change-password')
        self.token_refresh_url = reverse("token_refresh")
        # self.activate_url = reverse('activate')

    def test_user_cannot_register_with_no_data(self):
        register_url = reverse("auth_register")
        res = self.client.post(register_url)
        self.assertEqual(res.status_code, 400)

    def test_user_can_register(self):
        register_url = reverse("auth_register")
        res = self.client.post(register_url, data=self.user_data, format="json")
        # Sleep some time so the email thread can send the activation email before checking
        time.sleep(3)
        self.assertEqual(res.data["user"]["email"], self.user_data["user"]["email"])
        self.assertEqual(res.status_code, 201)
        self.assertEqual(len(self.mail.outbox), 1)
        self.assertEqual(self.mail.outbox[0].subject, "Activate your account")

    def test_user_activation(self):
        register_url = reverse("auth_register")
        res = self.client.post(register_url, data=self.user_data, format="json")
        self.assertEqual(res.data["user"]["email"], self.user_data["user"]["email"])
        self.assertEqual(res.status_code, 201)

        # Sleep some time so the email thread can send the activation email before checking
        time.sleep(3)
        self.assertEqual(len(self.mail.outbox), 1)

        email = self.user_data["user"]["email"]
        user = User.objects.get(email=email)

        self.assertEqual(user.is_active, False)

        email_body = self.mail.outbox[0].alternatives
        body_str = email_body[0][0]

        # URL is around the end of html body so taking only characters after 900th index
        activation_url = re.search(
            "(?P<url>https?://[^\s]+)", str(body_str)[900:]
        ).group("url")

        token = activation_url.split("/")[-2]
        uidb64 = activation_url.split("/")[-3]

        # Verify token
        verify_url = reverse("verify_token", kwargs={"uidb64": uidb64, "token": token})
        response = self.client.get(verify_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Activate User
        activation_url = reverse("activate", kwargs={"uidb64": uidb64, "token": token})
        response = self.client.get(activation_url)

        user_after_activation = User.objects.get(email=email)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_after_activation.is_active, True)

        # Test invalid token
        invalid_token = token[:-4] + "abcd"
        activation_url = reverse(
            "activate", kwargs={"uidb64": uidb64, "token": invalid_token}
        )

        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid UUID
        invalid_uid = uidb64[:-4] + "abcd"
        activation_url = reverse(
            "activate", kwargs={"uidb64": invalid_uid, "token": token}
        )

        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid UUID and token
        invalid_uid = uidb64[:-4] + "abcd"
        invalid_token = token[:-4] + "abcd"
        activation_url = reverse(
            "activate", kwargs={"uidb64": invalid_uid, "token": invalid_token}
        )

        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test Null UUID and token
        invalid_uid = None
        invalid_token = None
        activation_url = reverse(
            "activate", kwargs={"uidb64": invalid_uid, "token": invalid_token}
        )

        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password(self):
        register_url = reverse("auth_register")
        res = self.client.post(register_url, data=self.user_data, format="json")
        self.assertEqual(res.data["user"]["email"], self.user_data["user"]["email"])
        self.assertEqual(res.status_code, 201)

        # Sleep some time so the email thread can send the activation email before checking
        time.sleep(3)
        self.assertEqual(len(self.mail.outbox), 1)

        email = self.user_data["user"]["email"]
        user = User.objects.get(email=email)
        user.is_active = True
        user.save()

        reset_password_url = reverse("forgot_password")
        response = self.client.post(
            reset_password_url, data={"email": user.email}, format="json"
        )

        # Take the 2nd email in outbox, as the first one is for email verification
        email_body = self.mail.outbox[1].alternatives
        body_str = email_body[0][0]

        # URL is around the end of html body so taking only characters after 900th index
        reset_url = re.search("(?P<url>https?://[^\s]+)", str(body_str)[900:]).group(
            "url"
        )

        token = reset_url.split("/")[-2]
        uidb64 = reset_url.split("/")[-3]

        # Verify token
        verify_url = reverse("verify_token", kwargs={"uidb64": uidb64, "token": token})
        response = self.client.get(verify_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Reset password User
        reset_url = reverse("reset_password", kwargs={"uidb64": uidb64, "token": token})
        password_data = {"new_password": "#test1234#", "password_confirm": "#test1234#"}
        response = self.client.put(reset_url, data=password_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try logging in with old password
        response = self.client.post(
            self.login_url, self.user_data["user"], format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try loggin in with new password
        login_data = {"email": email, "password": "#test1234#"}

        response = self.client.post(self.login_url, login_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_login_with_unverified_email(self):
        res = self.client.post(
            self.login_url, data=self.user_data["user"], format="json"
        )
        self.assertEqual(res.status_code, 401)

    def test_user_can_login_after_verification(self):
        register_url = reverse("auth_register")
        response = self.client.post(register_url, self.user_data, format="json")
        email = response.data["user"]["email"]

        user = User.objects.get(email=email)
        user.is_active = True
        user.save()

        res = self.client.post(self.login_url, self.user_data["user"], format="json")
        self.assertEqual(res.status_code, 200)


    def test_get_self_info(self):
        url = reverse("user_details")

        register_url = reverse("auth_register")
        response = self.client.post(register_url, self.user_data, format="json")
        email = response.data["user"]["email"]

        user = User.objects.get(email=email)
        user.is_active = True
        user.save()


        # Login to get Auth token
        authorized_client = APIClient()
        response = authorized_client.post(self.login_url, self.user_data["user"])
        token = response.data.get("access")

        # Authenticate client instance
        authorized_client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        response = authorized_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data
        self.assertIsInstance(result["data"], dict)
        self.assertEqual(result["data"]["user_id"], str(user.user_id))

