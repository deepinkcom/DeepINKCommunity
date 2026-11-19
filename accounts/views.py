from django.db import IntegrityError
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import StaffCreationForm, StaffEditForm
from .models import StaffProfile

class StaffLoginView(LoginView):

    template_name = 'accounts/login.html'

    def form_valid(self, form):
        """
        Store a short-lived pending login after the password is valid.

        The user is only fully logged in after completing the
        authenticator-code step.
        """

        user = form.get_user()
        remember_me = bool(
            self.request.POST.get('remember_me')
        )

        # Change the session key after successful password validation.
        self.request.session.cycle_key()

        self.request.session['pre_2fa_user_id'] = user.id
        self.request.session['pre_2fa_started_at'] = (
            timezone.now().timestamp()
        )
        self.request.session['pre_2fa_remember_me'] = remember_me
        self.request.session['pre_2fa_next'] = self.get_success_url()

        return redirect('two_factor_verify')


def is_administrator(user):

    return (
        user.is_authenticated
        and user.groups.filter(
            name='Administrator'
        ).exists()
    )

def is_manager(user):

    return (
        user.is_authenticated
        and user.groups.filter(
            name='Manager'
        ).exists()
    )


def is_staff_member(user):

    return (
        user.is_authenticated
        and user.groups.filter(
            name='Staff'
        ).exists()
    )

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.views.decorators.http import require_POST


def administrator_required(view):
    from functools import wraps
    @login_required
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_active or not (request.user.is_superuser or is_administrator(request.user)):
            raise PermissionDenied('Administrator access required.')
        return view(request, *args, **kwargs)
    return wrapped


def staff_context(title, **kwargs):
    return dict(page_title=title, active_nav='staff', role='Administrator', **kwargs)


def lock_users():
    # Serialize account-management writes on databases supporting row locks.
    list(User.objects.select_for_update().order_by('pk').values_list('pk', flat=True))


def another_admin_exists(user):
    return User.objects.filter(is_active=True, groups__name='Administrator').exclude(pk=user.pk).exclude(staff_profile__is_active_staff=False).exists()


@administrator_required
def staff_accounts(request):
    users = User.objects.select_related('staff_profile').prefetch_related('groups').order_by('first_name', 'last_name', 'username')
    rows = []
    for user in users:
        profile = getattr(user, 'staff_profile', None)
        rows.append({'account': user, 'job_title': profile.job_title if profile else '',
                     'active': user.is_active and (profile is None or profile.is_active_staff),
                     'roles': ', '.join(g.name for g in user.groups.all()) or ('Superuser' if user.is_superuser else 'No role')})
    return render(request, 'accounts/staff_accounts.html', staff_context('Staff Accounts', rows=rows))


@administrator_required
def create_staff_account(request):
    form = StaffCreationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            form.add_error(None, 'Account creation conflict. Please check the email and try again.')
        else:
            messages.success(request, 'Staff account created successfully.')
            return redirect('staff_accounts')
    return render(request, 'accounts/create_staff_account.html', staff_context('Create Staff Account', form=form))


@administrator_required
def edit_staff_account(request, user_id):
    with transaction.atomic():
        if request.method == 'POST':
            lock_users()
        user = get_object_or_404(User, pk=user_id)
        profile = getattr(user, 'staff_profile', None)
        if profile is None:
            profile = StaffProfile(user=user, is_active_staff=user.is_active)
        form = StaffEditForm(request.POST if request.method == 'POST' else None, instance=user, staff_profile=profile)
        if request.method == 'POST' and form.is_valid():
            if user.groups.filter(name='Administrator').exists() and form.cleaned_data['role'].name != 'Administrator' and (user.pk == request.user.pk or not another_admin_exists(user)):
                form.add_error('role', 'You cannot remove your own Administrator role or the last active Administrator role.')
            else:
                form.save()
                messages.success(request, 'Staff account updated.')
                return redirect('staff_accounts')
    return render(request, 'accounts/edit_staff_account.html', staff_context('Edit Staff Account', form=form, staff_user=user))


@administrator_required
@require_POST
def toggle_staff_status(request, user_id):
    with transaction.atomic():
        lock_users()
        user = get_object_or_404(User, pk=user_id)
        profile = getattr(user, 'staff_profile', None)
        active = user.is_active and (profile is None or profile.is_active_staff)
        if user.pk == request.user.pk:
            messages.error(request, 'You cannot deactivate your own account.')
            return redirect('staff_accounts')
        if active and user.groups.filter(name='Administrator').exists() and not another_admin_exists(user):
            messages.error(request, 'The last active Administrator cannot be deactivated.')
            return redirect('staff_accounts')
        user.is_active = not active
        user.save(update_fields=['is_active'])
        if profile is not None:
            profile.is_active_staff = user.is_active
            profile.save(update_fields=['is_active_staff'])
        messages.success(request, 'Account activated.' if user.is_active else 'Account deactivated.')
    return redirect('staff_accounts')

@administrator_required
@require_POST
def delete_staff_account(request, user_id):
    from django.db import IntegrityError
    from django.db.models import ProtectedError, RestrictedError
    from .username_sequence import lock_staff_sequence, remember_staff_username
    try:
        with transaction.atomic():
            sequence = lock_staff_sequence()
            lock_users()
            user = get_object_or_404(User, pk=user_id)
            if user.pk == request.user.pk:
                messages.error(request, 'You cannot delete your own account.')
                return redirect('staff_accounts')
            if user.is_superuser or user.groups.filter(name='Administrator').exists():
                remaining = User.objects.filter(is_active=True).exclude(pk=user.pk).exclude(staff_profile__is_active_staff=False)
                from django.db.models import Q
                if not remaining.filter(Q(is_superuser=True) | Q(groups__name='Administrator')).exists():
                    messages.error(request, 'The last active administrator cannot be deleted.')
                    return redirect('staff_accounts')
            if user.tasks.exists():
                messages.error(request, 'Reassign this user’s tasks before deleting the account.')
                return redirect('staff_accounts')
            remember_staff_username(sequence, user.username)
            username = user.username
            user.delete()
        messages.success(request, f'Account {username} permanently deleted.')
    except (ProtectedError, RestrictedError, IntegrityError):
        messages.error(request, 'This account has linked records that prevent deletion. Deactivate it instead.')
    return redirect('staff_accounts')
