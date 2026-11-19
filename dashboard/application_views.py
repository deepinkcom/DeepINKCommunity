from accounts.username_sequence import next_staff_username
from hashlib import sha256
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from accounts.models import StaffProfile
from .decorators import dashboard_access_required
from .models import RequestStatus, ServiceRequest, VolunteerRecord
from .utils import log_audit

FINAL = (RequestStatus.APPROVED, RequestStatus.REJECTED, RequestStatus.CLOSED)


def can_decide(user):
    return (user.groups.filter(name='Administrator').exists()
            and user.has_perm('accounts.manage_staff_accounts'))


def send_invitation(request, user):
    token = default_token_generator.make_token(user)
    path = reverse('password_reset_confirm', kwargs={
        'uidb64': urlsafe_base64_encode(force_bytes(user.pk)), 'token': token})
    base = settings.STAFF_PORTAL_URL.rstrip('/')
    if not base.startswith(('https://', 'http://127.0.0.1:', 'http://localhost:')):
        raise ValueError('Configure a trusted HTTPS staff portal URL.')
    if not settings.DEBUG and not base.startswith('https://'):
        raise ValueError('Production staff portal must use HTTPS.')
    context = {'first_name': user.first_name, 'username': user.username,
               'setup_url': base + path,
               'login_url': base + reverse('login')}
    email = EmailMultiAlternatives(
        'Welcome to Deep INK | Activate your staff account',
        render_to_string('dashboard/email/staff_welcome.txt', context),
        settings.DEFAULT_FROM_EMAIL, [user.email])
    email.attach_alternative(render_to_string('dashboard/email/staff_welcome.html', context), 'text/html')
    if email.send(fail_silently=False) != 1:
        raise RuntimeError('Email was not accepted by the mail backend.')


def deliver(request, user):
    try:
        send_invitation(request, user)
    except Exception:
        # Never log the token or message contents.
        messages.warning(request, 'Account created, but email could not be sent. Check SMTP settings and use Resend invitation.')
    else:
        if settings.EMAIL_BACKEND.endswith('console.EmailBackend'):
            messages.info(request, 'Invitation printed in the development terminal. No real email was sent.')
        else:
            messages.success(request, 'Welcome invitation accepted by the mail server.')


@dashboard_access_required
def application_list(request):
    return render(request, 'dashboard/applications.html', {
        'role': request.staff_role, 'active_nav': 'applications',
        'page_title': 'Applications',
        'can_delete_applications': can_delete_application(request.user),
        'applications': ServiceRequest.objects.select_related('assigned_to', 'beneficiary'),
    })


@dashboard_access_required
def application_detail(request, pk):
    allowed = can_decide(request.user)
    if request.method == 'POST':
        if not allowed:
            raise PermissionDenied('Administrator approval is required.')
        action = request.POST.get('action')
        invitation_user = None
        try:
            with transaction.atomic():
                application = get_object_or_404(ServiceRequest.objects.select_for_update(), pk=pk)
                if action == 'resend':
                    user = application.approved_staff
                    if (application.status != RequestStatus.APPROVED or not user
                            or not user.is_active or user.has_usable_password()
                            or not user.groups.filter(name='Staff').exists()):
                        raise ValidationError('No pending staff invitation for this application.')
                    invitation_user = user
                elif action in ('approve', 'decline'):
                    if application.status in FINAL:
                        raise ValidationError('This application has already been decided.')
                    old_status = application.status
                    notes = request.POST.get('resolution_notes', '').strip()
                    if action == 'decline' and not notes:
                        raise ValidationError('Enter a reason for declining the application.')
                    if action == 'approve' and application.request_type == 'volunteer':
                        email = application.email.strip()
                        validate_email(email)
                        if User.objects.filter(email__iexact=email).exists():
                            raise ValidationError('An account already uses this email. Review Staff Accounts manually; no account was changed.')
                        group = Group.objects.filter(name='Staff').first()
                        if not group or not group.permissions.exists():
                            raise ValidationError('Staff role permissions are not configured.')
                        if len(application.phone) > 20:
                            raise ValidationError('Applicant phone exceeds the staff profile limit; review the record first.')
                        username = next_staff_username()
                        if User.objects.filter(email__iexact=email).exists():
                            raise ValidationError('An account already uses this email.')
                        # Username allocated from the shared staff sequence.
                        user = User.objects.create_user(username=username, email=email,
                            first_name=application.first_name, last_name=application.last_name,
                            password=None, is_staff=False, is_superuser=False)
                        user.groups.add(group)
                        StaffProfile.objects.create(user=user, phone_number=application.phone,
                                                    job_title='Volunteer', is_active_staff=True)
                        application.approved_staff = user
                        invitation_user = user
                        details = application.extra_data or {}
                        volunteer, created = VolunteerRecord.objects.get_or_create(
                            service_request=application,
                            defaults={
                                'first_name': application.first_name,
                                'last_name': application.last_name,
                                'email': application.email,
                                'phone': application.phone,
                                'interest_area': details.get('interest', ''),
                                'availability': details.get('availability', ''),
                                'skills': details.get('skills', ''),
                                'motivation': application.message,
                                'is_active': True,
                            },
                        )
                        if created:
                            log_audit(request.user, 'create', volunteer, request=request)
                    application.status = RequestStatus.APPROVED if action == 'approve' else RequestStatus.REJECTED
                    application.closed_by = request.user
                    application.closed_at = timezone.now()
                    application.resolution_notes = notes
                    application.save()
                    log_audit(request.user, 'status_change', application,
                              changes={'from': old_status, 'to': application.status}, request=request)
                    messages.success(request, 'Application approved.' if action == 'approve' else 'Application declined.')
                else:
                    raise ValidationError('Unknown application action.')
        except (ValidationError, IntegrityError) as exc:
            messages.error(request, ' '.join(exc.messages) if isinstance(exc, ValidationError) else 'Account or application conflict. No changes saved; please retry.')
        else:
            if invitation_user:
                deliver(request, invitation_user)
        return redirect('application_detail', pk=pk)

    application = get_object_or_404(ServiceRequest.objects.select_related('assigned_to', 'beneficiary', 'approved_staff', 'closed_by'), pk=pk)
    user = application.approved_staff
    return render(request, 'dashboard/application_detail.html', {
        'role': request.staff_role, 'active_nav': 'applications', 'page_title': application.reference_number,
        'application': application, 'can_decide': allowed and application.status not in FINAL,
        'can_resend': allowed and application.status == RequestStatus.APPROVED and user and user.is_active and not user.has_usable_password(),
        'follow_ups': application.follow_ups.all()[:10], 'documents': application.documents.all(),
    })

from django.views.decorators.http import require_POST
from django.db.models.deletion import ProtectedError, RestrictedError


def can_delete_application(user):
    return user.is_authenticated and user.is_active and user.groups.filter(name='Administrator').exists()


@dashboard_access_required
@require_POST
def application_delete(request, pk):
    if not can_delete_application(request.user):
        raise PermissionDenied('Only administrators can delete applications.')
    try:
        with transaction.atomic():
            application = get_object_or_404(ServiceRequest.objects.select_for_update(), pk=pk)
            if any(getattr(application, relation).exists() for relation in ('documents', 'follow_ups', 'tasks', 'referrals')):
                messages.error(request, 'This application has linked documents, follow-ups, tasks or referrals. Resolve those links before deleting it.')
                return redirect('application_list')
            if hasattr(application, 'partner_record') or hasattr(application, 'donor_record'):
                messages.error(request, 'This application has a linked partner or donor record. Resolve that link first.')
                return redirect('application_list')
            volunteer = getattr(application, 'volunteer_record', None)
            if volunteer is not None and application.status != RequestStatus.APPROVED:
                # A legacy pending volunteer would otherwise become visible when its FK is cleared.
                messages.error(request, 'This application has an unapproved legacy volunteer record. Review that record before deleting the application.')
                return redirect('application_list')
            reference = application.reference_number
            log_audit(request.user, 'delete', application, changes={'reference': reference}, request=request)
            # Approved staff is a forward FK: deleting the application does not delete the user.
            # VolunteerRecord.service_request uses SET_NULL, preserving approved volunteers.
            application.delete()
        messages.success(request, f'Application {reference} permanently deleted.')
    except (ProtectedError, RestrictedError, IntegrityError):
        messages.error(request, 'Linked records prevent deletion. No changes were saved.')
    return redirect('application_list')
