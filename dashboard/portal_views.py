from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from app.models import (
    ContactInformation,
    Event,
    ImpactStory,
    NewsArticle,
    Opportunity,
    PartnerAcknowledgement,
    PublishStatus,
    SiteSection,
)
from .decorators import admin_required, dashboard_access_required, donations_access_required
from .forms import (
    AttendanceForm,
    BeneficiaryForm,
    ContactInformationForm,
    DocumentForm,
    DonatedItemForm,
    EmergingEntrepreneurForm,
    EnrolmentForm,
    EventForm,
    FollowUpForm,
    FundingForm,
    ImpactStoryForm,
    NewsArticleForm,
    OpportunityForm,
    OutreachDistributionForm,
    PartnerAcknowledgementForm,
    PartnerRecordForm,
    ProgrammeForm,
    ReferralForm,
    ServiceRequestForm,
    SiteSectionForm,
    StaffTaskForm,
    VolunteerRecordForm,
)
from .models import (
    Attendance,
    AuditLog,
    Beneficiary,
    Document,
    DonatedItem,
    DonorRecord,
    EmergingEntrepreneur,
    FollowUp,
    Funding,
    OutreachDistribution,
    PartnerRecord,
    Programme,
    ProgrammeEnrolment,
    Referral,
    RequestStatus,
    ServiceRequest,
    StaffTask,
    TaskStatus,
    VolunteerRecord,
)
from .utils import get_staff_users, log_audit


def _portal_context(request, active_nav, title):
    return {
        'role': request.staff_role,
        'active_nav': active_nav,
        'page_title': title,
    }


# --- Beneficiaries ---

@dashboard_access_required
def beneficiary_list(request):
    beneficiaries = Beneficiary.objects.filter(is_active=True)
    return render(
        request,
        'dashboard/list.html',
        {
            **_portal_context(request, 'beneficiaries', 'Beneficiaries'),
            'items': beneficiaries,
            'columns': ['full_name', 'category', 'phone', 'email'],
            'create_url_name': 'beneficiary_create',
            'detail_url_name': 'beneficiary_edit',
        },
    )


@dashboard_access_required
def beneficiary_create(request):
    if request.method == 'POST':
        form = BeneficiaryForm(request.POST)
        if form.is_valid():
            beneficiary = form.save(commit=False)
            beneficiary.registered_by = request.user
            beneficiary.save()
            log_audit(request.user, 'create', beneficiary, request=request)
            messages.success(request, 'Beneficiary registered successfully.')
            return redirect('beneficiary_list')
    else:
        form = BeneficiaryForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'beneficiaries', 'Register Beneficiary'),
            'form': form,
            'cancel_url_name': 'beneficiary_list',
        },
    )


@dashboard_access_required
def beneficiary_edit(request, pk):
    beneficiary = get_object_or_404(Beneficiary, pk=pk)
    if request.method == 'POST':
        form = BeneficiaryForm(request.POST, instance=beneficiary)
        if form.is_valid():
            form.save()
            log_audit(request.user, 'update', beneficiary, request=request)
            messages.success(request, 'Beneficiary updated successfully.')
            return redirect('beneficiary_list')
    else:
        form = BeneficiaryForm(instance=beneficiary)
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'beneficiaries', 'Edit Beneficiary'),
            'form': form,
            'cancel_url_name': 'beneficiary_list',
        },
    )


# --- Service Requests ---

@dashboard_access_required
def application_list(request):
    applications = ServiceRequest.objects.select_related(
        'assigned_to', 'beneficiary'
    )
    return render(
        request,
        'dashboard/applications.html',
        {
            **_portal_context(request, 'applications', 'Applications'),
            'applications': applications,
        },
    )


@dashboard_access_required
def application_detail(request, pk):
    application = get_object_or_404(
        ServiceRequest.objects.select_related('assigned_to', 'beneficiary'),
        pk=pk,
    )
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, instance=application)
        if form.is_valid():
            old_status = application.status
            application = form.save()
            if old_status != application.status:
                log_audit(
                    request.user,
                    'status_change',
                    application,
                    changes={'from': old_status, 'to': application.status},
                    request=request,
                )
            else:
                log_audit(request.user, 'update', application, request=request)
            messages.success(request, 'Application updated successfully.')
            return redirect('application_detail', pk=pk)
    else:
        form = ServiceRequestForm(instance=application)
    return render(
        request,
        'dashboard/application_detail.html',
        {
            **_portal_context(request, 'applications', application.reference_number),
            'application': application,
            'form': form,
            'follow_ups': application.follow_ups.all()[:10],
            'documents': application.documents.all(),
        },
    )


# --- Programmes ---

@dashboard_access_required
def programme_list(request):
    programmes = Programme.objects.select_related('coordinator')
    return render(
        request,
        'dashboard/list.html',
        {
            **_portal_context(request, 'programmes', 'Programmes'),
            'items': programmes,
            'columns': ['name', 'programme_type', 'start_date', 'is_active'],
            'create_url_name': 'programme_create',
            'detail_url_name': 'programme_edit',
        },
    )


@dashboard_access_required
def programme_create(request):
    if request.method == 'POST':
        form = ProgrammeForm(request.POST)
        if form.is_valid():
            programme = form.save()
            log_audit(request.user, 'create', programme, request=request)
            messages.success(request, 'Programme created successfully.')
            return redirect('programme_list')
    else:
        form = ProgrammeForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'programmes', 'Create Programme'),
            'form': form,
            'cancel_url_name': 'programme_list',
        },
    )


@dashboard_access_required
def programme_edit(request, pk):
    programme = get_object_or_404(Programme, pk=pk)
    if request.method == 'POST':
        form = ProgrammeForm(request.POST, instance=programme)
        if form.is_valid():
            form.save()
            log_audit(request.user, 'update', programme, request=request)
            messages.success(request, 'Programme updated successfully.')
            return redirect('programme_list')
    else:
        form = ProgrammeForm(instance=programme)
    enrolments = programme.enrolments.select_related('beneficiary')
    return render(
        request,
        'dashboard/programme_detail.html',
        {
            **_portal_context(request, 'programmes', programme.name),
            'programme': programme,
            'form': form,
            'enrolments': enrolments,
        },
    )


@dashboard_access_required
def enrolment_create(request):
    if request.method == 'POST':
        form = EnrolmentForm(request.POST)
        if form.is_valid():
            enrolment = form.save(commit=False)
            enrolment.enrolled_by = request.user
            enrolment.save()
            log_audit(request.user, 'create', enrolment, request=request)
            messages.success(request, 'Beneficiary enrolled successfully.')
            return redirect('programme_edit', pk=enrolment.programme_id)
    else:
        initial = {}
        if request.GET.get('programme'):
            initial['programme'] = request.GET['programme']
        form = EnrolmentForm(initial=initial)
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'programmes', 'Enrol Beneficiary'),
            'form': form,
            'cancel_url_name': 'programme_list',
        },
    )


@dashboard_access_required
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.save()
            log_audit(request.user, 'create', record, request=request)
            messages.success(request, 'Attendance recorded successfully.')
            return redirect('programme_list')
    else:
        form = AttendanceForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'programmes', 'Record Attendance'),
            'form': form,
            'cancel_url_name': 'programme_list',
        },
    )


# --- Volunteers ---

@dashboard_access_required
def volunteer_list(request):
    volunteers = VolunteerRecord.objects.all()
    return render(
        request,
        'dashboard/list.html',
        {
            **_portal_context(request, 'volunteers', 'Volunteers'),
            'items': volunteers,
            'columns': ['first_name', 'last_name', 'email', 'interest_area', 'is_active'],
            'create_url_name': 'volunteer_create',
            'detail_url_name': 'volunteer_edit',
        },
    )


@dashboard_access_required
def volunteer_create(request):
    if request.method == 'POST':
        form = VolunteerRecordForm(request.POST)
        if form.is_valid():
            volunteer = form.save()
            log_audit(request.user, 'create', volunteer, request=request)
            messages.success(request, 'Volunteer record created.')
            return redirect('volunteer_list')
    else:
        form = VolunteerRecordForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'volunteers', 'Add Volunteer'),
            'form': form,
            'cancel_url_name': 'volunteer_list',
        },
    )


@dashboard_access_required
def volunteer_edit(request, pk):
    volunteer = get_object_or_404(VolunteerRecord, pk=pk)
    if request.method == 'POST':
        form = VolunteerRecordForm(request.POST, instance=volunteer)
        if form.is_valid():
            form.save()
            log_audit(request.user, 'update', volunteer, request=request)
            messages.success(request, 'Volunteer record updated.')
            return redirect('volunteer_list')
    else:
        form = VolunteerRecordForm(instance=volunteer)
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'volunteers', 'Edit Volunteer'),
            'form': form,
            'cancel_url_name': 'volunteer_list',
        },
    )


# --- Events ---

@dashboard_access_required
def event_list(request):
    events = Event.objects.order_by('-start_date')
    return render(
        request,
        'dashboard/events.html',
        {
            **_portal_context(request, 'events', 'Events & Activities'),
            'events': events,
        },
    )


@dashboard_access_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            log_audit(request.user, 'create', event, request=request)
            messages.success(request, 'Event created successfully.')
            return redirect('event_list')
    else:
        form = EventForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'events', 'Create Event'),
            'form': form,
            'cancel_url_name': 'event_list',
        },
    )


# --- Donations ---

@donations_access_required
def donation_list(request):
    items = DonatedItem.objects.all()[:50]
    funding = Funding.objects.all()[:50]
    distributions = OutreachDistribution.objects.all()[:50]
    return render(
        request,
        'dashboard/donations.html',
        {
            **_portal_context(request, 'donations', 'Donations & Distributions'),
            'donated_items': items,
            'funding_records': funding,
            'distributions': distributions,
        },
    )


@donations_access_required
def donated_item_create(request):
    if request.method == 'POST':
        form = DonatedItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.recorded_by = request.user
            item.save()
            log_audit(request.user, 'create', item, request=request)
            messages.success(request, 'Donated item recorded.')
            return redirect('donation_list')
    else:
        form = DonatedItemForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'donations', 'Record Donated Item'),
            'form': form,
            'cancel_url_name': 'donation_list',
        },
    )


@donations_access_required
def funding_create(request):
    if request.method == 'POST':
        form = FundingForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.save()
            log_audit(request.user, 'create', record, request=request)
            messages.success(request, 'Funding recorded.')
            return redirect('donation_list')
    else:
        form = FundingForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'donations', 'Record Funding'),
            'form': form,
            'cancel_url_name': 'donation_list',
        },
    )


@donations_access_required
def distribution_create(request):
    if request.method == 'POST':
        form = OutreachDistributionForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.save()
            log_audit(request.user, 'create', record, request=request)
            messages.success(request, 'Distribution recorded.')
            return redirect('donation_list')
    else:
        form = OutreachDistributionForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'donations', 'Record Distribution'),
            'form': form,
            'cancel_url_name': 'donation_list',
        },
    )


# --- Tasks ---

@dashboard_access_required
def task_list(request):
    if request.staff_role == 'Staff':
        tasks = StaffTask.objects.filter(assigned_to=request.user)
    else:
        tasks = StaffTask.objects.select_related('assigned_to')
    overdue_count = sum(1 for t in tasks if t.is_overdue)
    return render(
        request,
        'dashboard/tasks.html',
        {
            **_portal_context(request, 'tasks', 'Staff Tasks'),
            'tasks': tasks,
            'overdue_count': overdue_count,
        },
    )


@dashboard_access_required
def task_create(request):
    if request.method == 'POST':
        form = StaffTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            log_audit(request.user, 'create', task, request=request)
            messages.success(request, 'Task assigned successfully.')
            return redirect('task_list')
    else:
        form = StaffTaskForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'tasks', 'Assign Task'),
            'form': form,
            'cancel_url_name': 'task_list',
        },
    )


@dashboard_access_required
def follow_up_create(request):
    if request.method == 'POST':
        form = FollowUpForm(request.POST)
        if form.is_valid():
            follow_up = form.save(commit=False)
            follow_up.recorded_by = request.user
            follow_up.save()
            log_audit(request.user, 'create', follow_up, request=request)
            messages.success(request, 'Follow-up recorded.')
            if follow_up.service_request_id:
                return redirect(
                    'application_detail',
                    pk=follow_up.service_request_id,
                )
            return redirect('task_list')
    else:
        initial = {}
        if request.GET.get('request'):
            initial['service_request'] = request.GET['request']
        form = FollowUpForm(initial=initial)
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'tasks', 'Record Follow-up'),
            'form': form,
            'cancel_url_name': 'task_list',
        },
    )


# --- Documents ---

@dashboard_access_required
def document_list(request):
    documents = Document.objects.select_related('uploaded_by')
    return render(
        request,
        'dashboard/list.html',
        {
            **_portal_context(request, 'documents', 'Documents'),
            'items': documents,
            'columns': ['title', 'category', 'uploaded_at'],
            'create_url_name': 'document_create',
            'detail_url_name': None,
        },
    )


@dashboard_access_required
def document_create(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            log_audit(request.user, 'create', document, request=request)
            messages.success(request, 'Document uploaded successfully.')
            return redirect('document_list')
    else:
        form = DocumentForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'documents', 'Upload Document'),
            'form': form,
            'cancel_url_name': 'document_list',
            'multipart': True,
        },
    )


# --- Referrals ---

@dashboard_access_required
def referral_list(request):
    referrals = Referral.objects.select_related('beneficiary', 'referred_by')
    return render(
        request,
        'dashboard/list.html',
        {
            **_portal_context(request, 'referrals', 'Referrals'),
            'items': referrals,
            'columns': ['beneficiary', 'partner_name', 'partner_type', 'referral_date'],
            'create_url_name': 'referral_create',
            'detail_url_name': 'referral_edit',
        },
    )


@dashboard_access_required
def referral_create(request):
    if request.method == 'POST':
        form = ReferralForm(request.POST)
        if form.is_valid():
            referral = form.save(commit=False)
            referral.referred_by = request.user
            referral.save()
            log_audit(request.user, 'create', referral, request=request)
            messages.success(request, 'Referral recorded successfully.')
            return redirect('referral_list')
    else:
        form = ReferralForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'referrals', 'Create Referral'),
            'form': form,
            'cancel_url_name': 'referral_list',
        },
    )


@dashboard_access_required
def referral_edit(request, pk):
    referral = get_object_or_404(Referral, pk=pk)
    if request.method == 'POST':
        form = ReferralForm(request.POST, instance=referral)
        if form.is_valid():
            form.save()
            log_audit(request.user, 'update', referral, request=request)
            messages.success(request, 'Referral updated successfully.')
            return redirect('referral_list')
    else:
        form = ReferralForm(instance=referral)
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'referrals', 'Edit Referral'),
            'form': form,
            'cancel_url_name': 'referral_list',
        },
    )


# --- Partners & Entrepreneurs ---

@dashboard_access_required
def partner_list(request):
    partners = PartnerRecord.objects.all()
    return render(
        request,
        'dashboard/list.html',
        {
            **_portal_context(request, 'partners', 'Partners'),
            'items': partners,
            'columns': ['organisation_name', 'contact_person', 'email', 'is_active'],
            'create_url_name': 'partner_create',
            'detail_url_name': 'partner_edit',
        },
    )


@dashboard_access_required
def partner_create(request):
    if request.method == 'POST':
        form = PartnerRecordForm(request.POST)
        if form.is_valid():
            partner = form.save()
            log_audit(request.user, 'create', partner, request=request)
            messages.success(request, 'Partner record created.')
            return redirect('partner_list')
    else:
        form = PartnerRecordForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'partners', 'Add Partner'),
            'form': form,
            'cancel_url_name': 'partner_list',
        },
    )


@dashboard_access_required
def partner_edit(request, pk):
    partner = get_object_or_404(PartnerRecord, pk=pk)
    if request.method == 'POST':
        form = PartnerRecordForm(request.POST, instance=partner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Partner record updated.')
            return redirect('partner_list')
    else:
        form = PartnerRecordForm(instance=partner)
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'partners', 'Edit Partner'),
            'form': form,
            'cancel_url_name': 'partner_list',
        },
    )


@dashboard_access_required
def entrepreneur_list(request):
    entrepreneurs = EmergingEntrepreneur.objects.all()
    return render(
        request,
        'dashboard/list.html',
        {
            **_portal_context(request, 'entrepreneurs', 'Emerging Entrepreneurs'),
            'items': entrepreneurs,
            'columns': ['business_name', 'first_name', 'last_name', 'business_type'],
            'create_url_name': 'entrepreneur_create',
            'detail_url_name': 'entrepreneur_edit',
        },
    )


@dashboard_access_required
def entrepreneur_create(request):
    if request.method == 'POST':
        form = EmergingEntrepreneurForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrepreneur record created.')
            return redirect('entrepreneur_list')
    else:
        form = EmergingEntrepreneurForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'entrepreneurs', 'Add Entrepreneur'),
            'form': form,
            'cancel_url_name': 'entrepreneur_list',
        },
    )


@dashboard_access_required
def entrepreneur_edit(request, pk):
    entrepreneur = get_object_or_404(EmergingEntrepreneur, pk=pk)
    if request.method == 'POST':
        form = EmergingEntrepreneurForm(request.POST, instance=entrepreneur)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrepreneur record updated.')
            return redirect('entrepreneur_list')
    else:
        form = EmergingEntrepreneurForm(instance=entrepreneur)
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'entrepreneurs', 'Edit Entrepreneur'),
            'form': form,
            'cancel_url_name': 'entrepreneur_list',
        },
    )


# --- Website Content (Administrator) ---

@admin_required
def content_home(request):
    sections = SiteSection.objects.all()
    pending_news = NewsArticle.objects.filter(status=PublishStatus.PENDING).count()
    pending_stories = ImpactStory.objects.filter(status=PublishStatus.PENDING).count()
    return render(
        request,
        'dashboard/content_home.html',
        {
            **_portal_context(request, 'content', 'Website Content'),
            'sections': sections,
            'pending_news': pending_news,
            'pending_stories': pending_stories,
        },
    )


@admin_required
def content_section_edit(request, pk):
    section = get_object_or_404(SiteSection, pk=pk)
    if request.method == 'POST':
        form = SiteSectionForm(request.POST, instance=section)
        if form.is_valid():
            section = form.save(commit=False)
            section.updated_by = request.user
            section.save()
            log_audit(request.user, 'update', section, request=request)
            messages.success(request, 'Section updated successfully.')
            return redirect('content_home')
    else:
        form = SiteSectionForm(instance=section)
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'content', f'Edit {section.title}'),
            'form': form,
            'cancel_url_name': 'content_home',
        },
    )


@admin_required
def news_list(request):
    articles = NewsArticle.objects.all()
    return render(
        request,
        'dashboard/content_list.html',
        {
            **_portal_context(request, 'content', 'News Articles'),
            'items': articles,
            'content_type': 'news',
        },
    )


@admin_required
def news_create(request):
    if request.method == 'POST':
        form = NewsArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.created_by = request.user
            article.save()
            log_audit(request.user, 'create', article, request=request)
            messages.success(request, 'News article saved.')
            return redirect('news_list')
    else:
        form = NewsArticleForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'content', 'Create News Article'),
            'form': form,
            'cancel_url_name': 'news_list',
            'multipart': True,
        },
    )


@admin_required
def news_approve(request, pk):
    article = get_object_or_404(NewsArticle, pk=pk)
    article.status = PublishStatus.PUBLISHED
    article.approved_by = request.user
    if not article.published_at:
        article.published_at = timezone.now()
    article.save()
    log_audit(request.user, 'approve', article, request=request)
    messages.success(request, 'News article published.')
    return redirect('news_list')


@admin_required
def impact_story_list(request):
    stories = ImpactStory.objects.all()
    return render(
        request,
        'dashboard/content_list.html',
        {
            **_portal_context(request, 'content', 'Impact Stories'),
            'items': stories,
            'content_type': 'impact',
        },
    )


@admin_required
def impact_story_create(request):
    if request.method == 'POST':
        form = ImpactStoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.created_by = request.user
            story.save()
            log_audit(request.user, 'create', story, request=request)
            messages.success(request, 'Impact story saved.')
            return redirect('impact_story_list')
    else:
        form = ImpactStoryForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'content', 'Create Impact Story'),
            'form': form,
            'cancel_url_name': 'impact_story_list',
            'multipart': True,
        },
    )


@admin_required
def impact_story_approve(request, pk):
    story = get_object_or_404(ImpactStory, pk=pk)
    story.status = PublishStatus.PUBLISHED
    story.approved_by = request.user
    if not story.published_at:
        story.published_at = timezone.now()
    story.save()
    log_audit(request.user, 'approve', story, request=request)
    messages.success(request, 'Impact story published.')
    return redirect('impact_story_list')


@admin_required
def opportunity_list_admin(request):
    opportunities = Opportunity.objects.all()
    return render(
        request,
        'dashboard/content_list.html',
        {
            **_portal_context(request, 'content', 'Opportunities'),
            'items': opportunities,
            'content_type': 'opportunity',
        },
    )


@admin_required
def opportunity_create(request):
    if request.method == 'POST':
        form = OpportunityForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()
            messages.success(request, 'Opportunity saved.')
            return redirect('opportunity_list_admin')
    else:
        form = OpportunityForm()
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'content', 'Create Opportunity'),
            'form': form,
            'cancel_url_name': 'opportunity_list_admin',
        },
    )


@admin_required
def contact_info_edit(request):
    contact = ContactInformation.objects.filter(is_active=True).first()
    if not contact:
        contact = ContactInformation.objects.create()
    if request.method == 'POST':
        form = ContactInformationForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact information updated.')
            return redirect('content_home')
    else:
        form = ContactInformationForm(instance=contact)
    return render(
        request,
        'dashboard/form.html',
        {
            **_portal_context(request, 'content', 'Contact Information'),
            'form': form,
            'cancel_url_name': 'content_home',
        },
    )


# --- Reports ---

@donations_access_required
def reports_home(request):
    stats = {
        'beneficiaries': Beneficiary.objects.filter(is_active=True).count(),
        'programmes': Programme.objects.filter(is_active=True).count(),
        'referrals': Referral.objects.count(),
        'attendance': Attendance.objects.filter(attended=True).count(),
        'partners': PartnerRecord.objects.filter(is_active=True).count(),
        'impact_stories': ImpactStory.objects.filter(
            status=PublishStatus.PUBLISHED
        ).count(),
        'open_requests': ServiceRequest.objects.exclude(
            status__in=[RequestStatus.CLOSED, RequestStatus.REJECTED]
        ).count(),
        'volunteers': VolunteerRecord.objects.filter(is_active=True).count(),
    }
    return render(
        request,
        'dashboard/reports.html',
        {
            **_portal_context(request, 'reports', 'Reports'),
            'stats': stats,
        },
    )


@donations_access_required
def report_export(request, report_type):
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report_type}.csv"'
    writer = csv.writer(response)

    if report_type == 'beneficiaries':
        writer.writerow([
            'First Name', 'Last Name', 'Category', 'Phone', 'Email', 'Registered',
        ])
        for b in Beneficiary.objects.all():
            writer.writerow([
                b.first_name, b.last_name, b.get_category_display(),
                b.phone, b.email, b.created_at.strftime('%Y-%m-%d'),
            ])
    elif report_type == 'programmes':
        writer.writerow(['Name', 'Type', 'Start', 'End', 'Active'])
        for p in Programme.objects.all():
            writer.writerow([
                p.name, p.get_programme_type_display(),
                p.start_date, p.end_date, p.is_active,
            ])
    elif report_type == 'referrals':
        writer.writerow([
            'Beneficiary', 'Partner', 'Type', 'Date', 'Outcome',
        ])
        for r in Referral.objects.select_related('beneficiary'):
            writer.writerow([
                r.beneficiary.full_name, r.partner_name,
                r.get_partner_type_display(), r.referral_date, r.outcome,
            ])
    elif report_type == 'attendance':
        writer.writerow(['Programme', 'Beneficiary', 'Date', 'Attended'])
        for a in Attendance.objects.select_related('programme', 'beneficiary'):
            writer.writerow([
                a.programme.name, a.beneficiary.full_name,
                a.session_date, a.attended,
            ])
    elif report_type == 'partnerships':
        writer.writerow(['Organisation', 'Contact', 'Email', 'Active'])
        for p in PartnerRecord.objects.all():
            writer.writerow([
                p.organisation_name, p.contact_person, p.email, p.is_active,
            ])
    elif report_type == 'outreach':
        writer.writerow(['Type', 'Description', 'Quantity', 'Date'])
        for d in OutreachDistribution.objects.all():
            writer.writerow([
                d.get_distribution_type_display(), d.description,
                d.quantity, d.distribution_date,
            ])
    elif report_type == 'impact':
        writer.writerow(['Title', 'Beneficiary', 'Programme', 'Published'])
        for s in ImpactStory.objects.filter(status=PublishStatus.PUBLISHED):
            writer.writerow([
                s.title, s.beneficiary_name, s.programme_name,
                s.published_at.strftime('%Y-%m-%d') if s.published_at else '',
            ])
    elif report_type == 'applications':
        writer.writerow([
            'Reference', 'Type', 'Name', 'Status', 'Assigned To', 'Submitted',
        ])
        for a in ServiceRequest.objects.select_related('assigned_to'):
            writer.writerow([
                a.reference_number, a.get_request_type_display(),
                f'{a.first_name} {a.last_name}', a.get_status_display(),
                a.assigned_to.get_full_name() if a.assigned_to else '',
                a.submitted_at.strftime('%Y-%m-%d'),
            ])
    else:
        writer.writerow(['No data'])

    return response


# --- Audit Log ---

@admin_required
def audit_log_list(request):
    logs = AuditLog.objects.select_related('user')[:200]
    return render(
        request,
        'dashboard/audit_log.html',
        {
            **_portal_context(request, 'audit', 'Audit Trail'),
            'logs': logs,
        },
    )
