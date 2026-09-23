from django.utils import timezone

from app.models import Event, PublishStatus
from .decorators import dashboard_access_required
from .models import Beneficiary, Programme, ServiceRequest
from django.shortcuts import render


@dashboard_access_required
def dashboard(request):
    upcoming_events = Event.objects.filter(
        status=PublishStatus.PUBLISHED,
        start_date__gte=timezone.now(),
    ).count()

    recent_applications = ServiceRequest.objects.select_related(
        'assigned_to'
    ).order_by('-submitted_at')[:5]

    return render(
        request,
        'dashboard/dashboard.html',
        {
            'role': request.staff_role,
            'beneficiary_count': Beneficiary.objects.filter(is_active=True).count(),
            'application_count': ServiceRequest.objects.count(),
            'programme_count': Programme.objects.filter(is_active=True).count(),
            'event_count': upcoming_events,
            'recent_applications': recent_applications,
        },
    )
