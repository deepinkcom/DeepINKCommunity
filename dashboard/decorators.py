from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .utils import can_manage_donations, get_user_role, is_administrator


def dashboard_access_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        role = get_user_role(request.user)
        if not role:
            raise PermissionDenied(
                'You do not have permission to access the dashboard.'
            )
        request.staff_role = role
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @dashboard_access_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_administrator(request.user):
            raise PermissionDenied(
                'Administrator access is required for this action.'
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def donations_access_required(view_func):
    @dashboard_access_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not can_manage_donations(request.user):
            raise PermissionDenied(
                'Manager or Administrator access is required.'
            )
        return view_func(request, *args, **kwargs)
    return wrapper
