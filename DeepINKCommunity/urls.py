"""
Definition of urls for DeepINKCommunity.
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from accounts.views import StaffLoginView

urlpatterns = [
    path('admin/', admin.site.urls),

    path(
    'login/',
    StaffLoginView.as_view(),
    name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html'
        ),
        name='password_reset'
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    path(
        '',
        include('accounts.urls')
    ),

    path(
        '',
        include('dashboard.urls')
    ),

    path(
        '',
        include('app.urls')
        ),
]