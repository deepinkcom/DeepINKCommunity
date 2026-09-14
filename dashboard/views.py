from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render


@login_required
def dashboard(request):

    user = request.user

    if user.groups.filter(name='Administrator').exists():
        role = 'Administrator'

    elif user.groups.filter(name='Manager').exists():
        role = 'Manager'

    elif user.groups.filter(name='Staff').exists():
        role = 'Staff'

    else:
        raise PermissionDenied(
            'You do not have permission to access the dashboard.'
        )

    return render(
        request,
        'dashboard/dashboard.html',
        {
            'role': role,
        }
    )