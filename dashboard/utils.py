from django.contrib.auth.models import User

from .models import AuditLog


def get_user_role(user):
    if not user.is_authenticated:
        return None
    if user.groups.filter(name='Administrator').exists():
        return 'Administrator'
    if user.groups.filter(name='Manager').exists():
        return 'Manager'
    if user.groups.filter(name='Staff').exists():
        return 'Staff'
    return None


def require_dashboard_access(user):
    return get_user_role(user) is not None


def is_administrator(user):
    return user.is_authenticated and user.groups.filter(
        name='Administrator'
    ).exists()


def is_manager(user):
    return user.is_authenticated and user.groups.filter(
        name='Manager'
    ).exists()


def can_manage_donations(user):
    return is_administrator(user) or is_manager(user)


def get_staff_users():
    return User.objects.filter(
        is_active=True,
        groups__name__in=['Administrator', 'Manager', 'Staff'],
    ).distinct().order_by('first_name', 'username')


def log_audit(user, action, instance, changes=None, request=None):
    ip_address = None
    if request:
        ip_address = request.META.get('REMOTE_ADDR')

    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=str(instance.pk),
        object_repr=str(instance)[:300],
        changes=changes or {},
        ip_address=ip_address,
    )
