"""
URL configuration for DeepINKCommunity.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from django_otp.admin import OTPAdminSite

from accounts.views import StaffLoginView


# Create a proper admin site that requires two-factor authentication.
otp_admin_site = OTPAdminSite(OTPAdminSite.name)

# Copy all existing model registrations to the protected admin site.
for model, model_admin in admin.site._registry.items():
    otp_admin_site.register(
        model,
        model_admin.__class__,
    )

otp_admin_site.site_header = 'Deep Ink Community Centre Administration'
otp_admin_site.site_title = 'Deep Ink Administration'
otp_admin_site.index_title = 'Administration'


urlpatterns = [
    path(
        'admin/',
        otp_admin_site.urls,
    ),

    path(
        'login/',
        StaffLoginView.as_view(),
        name='login',
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout',
    ),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html',
        ),
        name='password_reset',
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html',
        ),
        name='password_reset_done',
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
        ),
        name='password_reset_confirm',
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),

    path(
        '',
        include('accounts.urls'),
    ),

    path(
        '',
        include('dashboard.urls'),
    ),

    path(
        '',
        include('app.urls'),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )