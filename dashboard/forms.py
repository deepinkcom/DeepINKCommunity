from django import forms
from django.contrib.auth.models import User

from app.models import (
    ContactInformation,
    Event,
    ImpactStory,
    NewsArticle,
    Opportunity,
    PartnerAcknowledgement,
    SiteSection,
)
from .models import (
    Attendance,
    Beneficiary,
    Document,
    DonatedItem,
    EmergingEntrepreneur,
    FollowUp,
    Funding,
    OutreachDistribution,
    PartnerRecord,
    Programme,
    ProgrammeEnrolment,
    Referral,
    ServiceRequest,
    StaffTask,
    VolunteerRecord,
)
from .utils import get_staff_users


class BeneficiaryForm(forms.ModelForm):
    class Meta:
        model = Beneficiary
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'phone', 'email', 'address', 'category', 'support_needs', 'notes',
        ]


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = [
            'request_type', 'education_detail', 'first_name', 'last_name',
            'email', 'phone', 'message', 'status', 'beneficiary',
            'assigned_to', 'resolution_notes',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = get_staff_users()


class ProgrammeForm(forms.ModelForm):
    class Meta:
        model = Programme
        fields = [
            'name', 'programme_type', 'description',
            'start_date', 'end_date', 'location', 'coordinator', 'is_active',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['coordinator'].queryset = get_staff_users()


class EnrolmentForm(forms.ModelForm):
    class Meta:
        model = ProgrammeEnrolment
        fields = ['programme', 'beneficiary', 'notes', 'is_active']


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['programme', 'beneficiary', 'session_date', 'attended', 'notes']


class ReferralForm(forms.ModelForm):
    class Meta:
        model = Referral
        fields = [
            'beneficiary', 'service_request', 'partner_type', 'partner_name',
            'partner_contact', 'reason', 'referral_date', 'follow_up_date', 'outcome',
        ]


class VolunteerRecordForm(forms.ModelForm):
    class Meta:
        model = VolunteerRecord
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'interest_area',
            'availability', 'skills', 'motivation', 'is_active', 'notes',
        ]


class PartnerRecordForm(forms.ModelForm):
    class Meta:
        model = PartnerRecord
        fields = [
            'organisation_name', 'contact_person', 'email', 'phone',
            'partnership_type', 'description', 'is_active',
        ]


class EmergingEntrepreneurForm(forms.ModelForm):
    class Meta:
        model = EmergingEntrepreneur
        fields = [
            'beneficiary', 'business_name', 'business_type', 'support_needed',
            'first_name', 'last_name', 'email', 'phone', 'is_active',
        ]


class DonatedItemForm(forms.ModelForm):
    class Meta:
        model = DonatedItem
        fields = [
            'item_type', 'description', 'quantity', 'donor',
            'donor_name', 'received_date', 'notes',
        ]


class FundingForm(forms.ModelForm):
    class Meta:
        model = Funding
        fields = [
            'funding_type', 'source', 'amount', 'currency',
            'received_date', 'purpose', 'donor', 'notes',
        ]


class OutreachDistributionForm(forms.ModelForm):
    class Meta:
        model = OutreachDistribution
        fields = [
            'distribution_type', 'programme', 'beneficiary',
            'description', 'quantity', 'distribution_date', 'notes',
        ]


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            'title', 'category', 'file', 'beneficiary',
            'programme', 'service_request', 'notes',
        ]


class StaffTaskForm(forms.ModelForm):
    class Meta:
        model = StaffTask
        fields = [
            'title', 'description', 'assigned_to', 'service_request',
            'beneficiary', 'due_date', 'status',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = get_staff_users()


class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = [
            'service_request', 'beneficiary', 'task',
            'notes', 'follow_up_date', 'next_follow_up_date',
        ]
        widgets = {
            'follow_up_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }


class SiteSectionForm(forms.ModelForm):
    class Meta:
        model = SiteSection
        fields = ['key', 'title', 'content', 'status']


class NewsArticleForm(forms.ModelForm):
    class Meta:
        model = NewsArticle
        fields = ['title', 'summary', 'body', 'image', 'status', 'published_at']


class ImpactStoryForm(forms.ModelForm):
    class Meta:
        model = ImpactStory
        fields = [
            'title', 'summary', 'body', 'beneficiary_name',
            'programme_name', 'image', 'status', 'published_at',
        ]


class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = [
            'title', 'summary', 'body', 'opportunity_type',
            'deadline', 'location', 'external_link', 'status', 'published_at',
        ]


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'summary', 'body', 'event_type', 'start_date',
            'end_date', 'location', 'registration_link',
            'is_registration_required', 'status', 'published_at',
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class PartnerAcknowledgementForm(forms.ModelForm):
    class Meta:
        model = PartnerAcknowledgement
        fields = [
            'title', 'organisation_name', 'summary', 'body',
            'logo', 'website_url', 'status', 'published_at',
        ]


class ContactInformationForm(forms.ModelForm):
    class Meta:
        model = ContactInformation
        fields = [
            'address', 'phone', 'email', 'operating_hours',
            'map_embed_url', 'is_active',
        ]
