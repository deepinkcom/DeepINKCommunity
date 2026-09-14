from django.urls import path
from . import views


urlpatterns = [

    path(
        'staff/',
        views.staff_accounts,
        name='staff_accounts'
    ),

    path(
        'staff/create/',
        views.create_staff_account,
        name='create_staff_account'
    ),

    path(
    'staff/<int:user_id>/edit/',
    views.edit_staff_account,
    name='edit_staff_account'
    ),

    path(
    'staff/<int:user_id>/toggle-status/',
    views.toggle_staff_status,
    name='toggle_staff_status'
    ),

]