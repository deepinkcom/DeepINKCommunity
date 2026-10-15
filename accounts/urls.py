from django.urls import path

from . import views
from .two_factor_views import (
    two_factor_recovery_codes,
    two_factor_setup,
    two_factor_verify,
)


urlpatterns = [
    path(
        'two-factor/setup/',
        two_factor_setup,
        name='two_factor_setup',
    ),

    path(
        'two-factor/verify/',
        two_factor_verify,
        name='two_factor_verify',
    ),

    path(
        'two-factor/recovery-codes/',
        two_factor_recovery_codes,
        name='two_factor_recovery_codes',
    ),

    path(
        'staff/',
        views.staff_accounts,
        name='staff_accounts',
    ),

    path(
        'staff/create/',
        views.create_staff_account,
        name='create_staff_account',
    ),

    path(
        'staff/<int:user_id>/edit/',
        views.edit_staff_account,
        name='edit_staff_account',
    ),

    path(
        'staff/<int:user_id>/toggle-status/',
        views.toggle_staff_status,
        name='toggle_staff_status',
    ),
]