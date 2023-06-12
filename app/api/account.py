import logging

from django.contrib.auth.models import update_last_login
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import dateparse, timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse

from rest_framework import  permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers, status
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.validators import UniqueValidator


from app.models.user import User
from app.services.account_service import token_generator, create_user, change_password, forget_password, reset_password, check_token_validity
from app.utils.serializer import inline_serializer

from app.selectors.account_selector import profile

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    class InputSerializer(serializers.Serializer):
        user = inline_serializer(many=False, fields={
            'email': serializers.EmailField(required=True, help_text="Email of the user",
                                            validators=[UniqueValidator(queryset=User.objects.all())]),
            'first_name': serializers.CharField(write_only=False, required=True, help_text="First name of the user"),
            'last_name': serializers.CharField(write_only=False, required=True, help_text="Last name of the user"),
            'password': serializers.CharField(write_only=True, required=True, validators=[validate_password],
                                              style={"input_type": "password"}, help_text="Password of the user"),
            'password_confirm': serializers.CharField(write_only=True, required=True, style={"input_type": "password"},
                                                      help_text="Password confirmation for user"),
            'phone': serializers.CharField(write_only=True, required=True, help_text="Phone number of the user"),
            'user_id': serializers.CharField(read_only=True, required=False, help_text="UUID of the user")}
                                 )

        def validate(self, attrs):
            if attrs["user"]["password"] != attrs["user"]["password_confirm"]:
                raise serializers.ValidationError(
                    {"password": "Password fields didn't match."}
                )

            return attrs

    """
    Register new user (creates new company and user)

    post: Create company then create a user with admin role in that company
    """

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = create_user(**serializer.validated_data)

        response = self.InputSerializer(data)

        return Response(response.data, status=status.HTTP_201_CREATED)


class ChangePasswordView(APIView):
    class InputSerializer(serializers.Serializer):
        new_password = serializers.CharField(write_only=True, required=True, help_text="New password to be updated.")
        password_confirm = serializers.CharField(write_only=True, required=True,
                                                 help_text="Password confirmation for new password.")
        old_password = serializers.CharField(write_only=True, required=True,
                                             help_text="Old password that will be changed.")

        def validate(self, attrs):
            """Validates if the passwords match before changing"""
            if attrs["new_password"] != attrs["password_confirm"]:
                raise serializers.ValidationError(
                    {"password": "Password fields didn't match."}
                )

            return attrs

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    """
    Change password of logged in User

    put: Update the password of authenticated user
    """

    def put(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        change_password(request.user, **serializer.validated_data)

        return Response(status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField(write_only=True, required=True, help_text="Email of the user")

    """
    Sends a password reset email to the user
    post: Verifies user and then sends a password reset email
    """

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = forget_password(**serializer.validated_data)

        return JsonResponse(
            {
                "success": True,
                "message": "A reset password link has been sent to {}".format(
                    email
                ),
                "code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    """
    Updates password of unauthenticated user through password reset link

    put: Validates token from password reset link then updates the password of user
    """

    class InputSerializer(serializers.Serializer):
        new_password = serializers.CharField(write_only=True, required=True, help_text="New password to be updated.")
        password_confirm = serializers.CharField(write_only=True, required=True,
                                                 help_text="Password confirmation for Updating.")

        def validate(self, attrs):
            if attrs["new_password"] != attrs["password_confirm"]:
                raise serializers.ValidationError(
                    {"password": "Password fields didn't match."}
                )
            return attrs

    def put(self, request, uidb64, token):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        queryset = User.objects.all()
        uid = force_str(urlsafe_base64_decode(uidb64))

        filter_kwargs = {"user_id": uid}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)

        reset_password(obj, token, serializer.validated_data["new_password"])

        return JsonResponse(
            {
                "status": "success",
                "message": "Password updated successfully.",
                "code": status.HTTP_200_OK,
            }
        )


class VerifyResetTokenView(APIView):
    """
    Verifies token from the reset password link

    get: Verifies the token from the reset password link and returns token validity status
    """


    def get(self, request, uidb64, token):
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(user_id=uid)

        if check_token_validity(token, user):
            return JsonResponse(
                {
                    "success": True,
                    "message": "Token is valid.",
                    "code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Token is invalid or has expired.",
                    "code": status.HTTP_403_FORBIDDEN,
                },
                status=status.HTTP_403_FORBIDDEN,
            )


class ObtainTokenPairView(TokenObtainPairView):
    """
    Handles the Login and returns JWT token for authentication

    post: Takes the credentials of user and returns JWT access and refresh token for authentication
    """

    class TokenObtainPairSerializer(TokenObtainSerializer):
        """Serializer for obtaining JWT token during login"""
        token_class = RefreshToken

        @classmethod
        def get_token(cls, user):
            return cls.token_class.for_user(user)

        def validate(self, attrs):
            # make email lower case before login
            username_field = User.USERNAME_FIELD
            attrs[username_field] = attrs[username_field].lower()

            data = super().validate(attrs)

            refresh = self.get_token(self.user)

            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            if api_settings.UPDATE_LAST_LOGIN:
                update_last_login(None, self.user)

            return data

    serializer_class = TokenObtainPairSerializer


class LogoutView(APIView):
    """
    Handles the logout of user

    post: Takes the refresh token of user and blacklists it to prevent unauthorized usage
    """

    permission_classes = [
        permissions.IsAuthenticated,
    ]


    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.info(f"Logout failed for user {request.user.email}.")
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ActivateUserView(APIView):
    """
    Activate the user using the token in activate user email

    get: Validates the token from the activate user email and then makes the user active
    """


    def get(self, request, uidb64, token):

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            token, expiry_date = token.split("_")
            token = force_str(urlsafe_base64_decode(token))
            expiry_date = force_str(urlsafe_base64_decode(expiry_date))
            expiry_date = dateparse.parse_datetime(expiry_date)

            if (not token) or (not expiry_date):
                raise Exception

            current_time = timezone.now()

            if current_time > expiry_date:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Token has expired.",
                        "code": status.HTTP_400_BAD_REQUEST,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.get(user_id=uid)

        except Exception as e:
            user = None

        if not token_generator.check_token(user, token):
            return JsonResponse(
                {
                    "success": False,
                    "message": "Token is invalid or expired.",
                    "code": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user and token_generator.check_token(user, token):
            user.is_active = True
            user.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": "Email verification completed successfully.",
                    "code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )

        return JsonResponse(
            {
                "success": False,
                "message": "Email verification failed.",
                "code": status.HTTP_400_OK,
            },
            status=status.HTTP_400_OK,
        )


class UserDetailsView(APIView):
    """
    Gets own details of the user

    get: Validates user authentication and returns the details of that user
    """

    permission_classes = [
        permissions.IsAuthenticated,
    ]


    def get(self, request):
        user = request.user

        response = profile(user)

        return Response(
            {
                "message": "User details retrieved successfully.",
                "success": True,
                "code": status.HTTP_200_OK,
                "data": response["data"],
            },
            status=status.HTTP_200_OK,
        )
