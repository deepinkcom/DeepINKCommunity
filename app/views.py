from datetime import datetime

from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect, render

from app.models import (
    ContactInformation,
    Event,
    ImpactStory,
    NewsArticle,
    Opportunity,
    PartnerAcknowledgement,
    ProgrammeCategory,
    PublishStatus,
    SiteSection,
)
from .forms import ContactEnquiryForm, SupportApplicationForm, VolunteerApplicationForm


def _published(queryset):
    return queryset.filter(status=PublishStatus.PUBLISHED)


def _site_sections():
    sections = {}
    for section in SiteSection.objects.filter(status=PublishStatus.PUBLISHED):
        sections[section.key] = section
    return sections


def home(request):
    """Display the public homepage."""
    assert isinstance(request, HttpRequest)

    return render(
        request,
        'app/index.html',
        {
            'title': 'Home',
            'year': datetime.now().year,
            'active_page': 'home',
            'upcoming_events': _published(Event.objects.filter(
                start_date__gte=datetime.now(),
            ))[:3],
            'latest_news': _published(NewsArticle.objects.all())[:3],
            'opportunities': _published(Opportunity.objects.all())[:3],
            'impact_stories': _published(ImpactStory.objects.all())[:2],
        },
    )


def about(request):
    """Display the About Us page."""
    assert isinstance(request, HttpRequest)

    return render(
        request,
        'app/about.html',
        {
            'title': 'About Us',
            'year': datetime.now().year,
            'active_page': 'about',
            'sections': _site_sections(),
        },
    )


def programmes(request):
    """Display the programmes page."""
    assert isinstance(request, HttpRequest)

    return render(
        request,
        'app/programmes.html',
        {
            'title': 'Our Programmes',
            'year': datetime.now().year,
            'active_page': 'programmes',
            'programme_categories': ProgrammeCategory.objects.filter(
                status=PublishStatus.PUBLISHED,
            ),
        },
    )


def get_involved(request):
    """Display the Get Involved page and handle support/volunteer forms."""
    assert isinstance(request, HttpRequest)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'support':
            form = SupportApplicationForm(request.POST)
            if form.is_valid():
                application = form.save()
                messages.success(
                    request,
                    f'Your support application has been submitted. '
                    f'Reference: {application.reference_number}',
                )
                return redirect('get_involved')
            volunteer_form = VolunteerApplicationForm()
        elif form_type == 'volunteer':
            volunteer_form = VolunteerApplicationForm(request.POST)
            if volunteer_form.is_valid():
                application = volunteer_form.save()
                messages.success(
                    request,
                    f'Your volunteer application has been submitted. '
                    f'Reference: {application.reference_number}',
                )
                return redirect('get_involved')
            form = SupportApplicationForm()
        else:
            form = SupportApplicationForm()
            volunteer_form = VolunteerApplicationForm()
    else:
        form = SupportApplicationForm()
        volunteer_form = VolunteerApplicationForm()

    return render(
        request,
        'app/get_involved.html',
        {
            'title': 'Get Involved',
            'year': datetime.now().year,
            'active_page': 'get_involved',
            'support_form': form,
            'volunteer_form': volunteer_form,
        },
    )


def contact(request):
    """Display the Contact page and handle enquiries."""
    assert isinstance(request, HttpRequest)

    contact_info = ContactInformation.objects.filter(is_active=True).first()

    if request.method == 'POST':
        form = ContactEnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save()
            messages.success(
                request,
                f'Thank you. Your message has been received. '
                f'Reference: {enquiry.reference_number}',
            )
            return redirect('contact')
    else:
        form = ContactEnquiryForm()

    return render(
        request,
        'app/contact.html',
        {
            'title': 'Contact',
            'year': datetime.now().year,
            'active_page': 'contact',
            'contact_form': form,
            'contact_info': contact_info,
            'partners': _published(PartnerAcknowledgement.objects.all())[:6],
        },
    )
