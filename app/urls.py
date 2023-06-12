from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from app.api.account import RegisterView, ObtainTokenPairView, LogoutView, ChangePasswordView, ForgotPasswordView, \
    VerifyResetTokenView, ResetPasswordView, ActivateUserView, UserDetailsView


urlpatterns = [

    # accounts
    path('core/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('core/auth/login/', ObtainTokenPairView.as_view(), name="login"),
    path('core/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('core/auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('core/auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('core/auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('core/auth/verify-token/<str:uidb64>/<str:token>/', VerifyResetTokenView.as_view(), name='verify_token'),
    path('core/auth/reset-password/<str:uidb64>/<str:token>/', ResetPasswordView.as_view(), name='reset_password'),
    path('core/auth/activate-user/<str:uidb64>/<str:token>/', ActivateUserView.as_view(), name='activate'),

    path('core/auth/me/', UserDetailsView.as_view(), name='user_details'),
]
