from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .forms import StaffCreationForm, StaffEditForm
from .models import StaffProfile

class StaffLoginView(LoginView):

    template_name = 'accounts/login.html'

    def form_valid(self, form):

        remember_me = self.request.POST.get('remember_me')

        if remember_me:
            # Keep the session active for 14 days
            self.request.session.set_expiry(
                60 * 60 * 24 * 14
            )
        else:
            # Session expires when the browser is closed
            self.request.session.set_expiry(0)

        return super().form_valid(form)


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

@login_required
@permission_required(
    'accounts.manage_staff_accounts',
    raise_exception=True
)
def create_staff_account(request):

    if request.method == 'POST':

        form = StaffCreationForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('staff_accounts')

    else:

        form = StaffCreationForm()

    return render(
        request,
        'accounts/create_staff_account.html',
        {
            'form': form
        }
    )

@login_required
@permission_required(
    'accounts.manage_staff_accounts',
    raise_exception=True
)
def staff_accounts(request):

    staff_profiles = StaffProfile.objects.select_related(
        'user'
    ).prefetch_related(
        'user__groups'
    )

    return render(
        request,
        'accounts/staff_accounts.html',
        {
            'staff_profiles': staff_profiles
        }
    )

@login_required
@permission_required(
    'accounts.manage_staff_accounts',
    raise_exception=True
)
def edit_staff_account(request, user_id):

    user = get_object_or_404(User, id=user_id)

    staff_profile = get_object_or_404(StaffProfile, user=user)

    if request.method == 'POST':

        form = StaffEditForm(
            request.POST,
            instance=user,
            staff_profile=staff_profile
        )

        if form.is_valid():

            form.save()

            return redirect('staff_accounts')

    else:

        form = StaffEditForm(
            instance=user,
            staff_profile=staff_profile
        )

    return render(
        request,
        'accounts/edit_staff_account.html',
        {
            'form': form,
            'staff_user': user,
        }
    )

@login_required
@permission_required(
    'accounts.manage_staff_accounts',
    raise_exception=True
)
def toggle_staff_status(request, user_id):

    if request.method != 'POST':
        return redirect('staff_accounts')

    user = get_object_or_404(User, id=user_id)

    staff_profile = get_object_or_404(StaffProfile, user=user)

    # Prevent an Administrator from disabling themselves
    if user.id == request.user.id:

        messages.error(
            request,
            'You cannot deactivate your own staff account.'
        )

        return redirect('staff_accounts')

    # Determine the current administrator status
    is_admin = user.groups.filter(
        name='Administrator'
    ).exists()

    # If deactivating an Administrator,
    # make sure another active Administrator remains
    if (
        is_admin
        and user.is_active
        and staff_profile.is_active_staff
    ):

        active_admin_count = User.objects.filter(
            is_active=True,
            groups__name='Administrator',
            staff_profile__is_active_staff=True
        ).exclude(
            id=user.id
        ).distinct().count()

        if active_admin_count == 0:

            messages.error(
                request,
                'The last active Administrator cannot be deactivated.'
            )

            return redirect('staff_accounts')

    # Toggle both account and staff profile status
    new_status = not (
        user.is_active
        and staff_profile.is_active_staff
    )

    user.is_active = new_status
    user.save(update_fields=['is_active'])

    staff_profile.is_active_staff = new_status
    staff_profile.save(
        update_fields=['is_active_staff']
    )

    if new_status:

        messages.success(
            request,
            f'{user.get_full_name() or user.username} has been activated.'
        )

    else:

        messages.success(
            request,
            f'{user.get_full_name() or user.username} has been deactivated.'
        )

    return redirect('staff_accounts')