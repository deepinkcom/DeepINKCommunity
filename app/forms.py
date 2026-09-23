from django import forms

from dashboard.models import ServiceRequest, VolunteerRecord


class SupportApplicationForm(forms.Form):
    firstName = forms.CharField(max_length=100, label='First name')
    lastName = forms.CharField(max_length=100, label='Last name')
    email = forms.EmailField()
    phone = forms.CharField(max_length=30)
    supportType = forms.ChoiceField(
        choices=[
            ('education', 'Education support'),
            ('youth', 'Youth development'),
            ('entrepreneurship', 'Entrepreneurship support'),
            ('community', 'Community support'),
            ('referral', 'Referral assistance'),
            ('other', 'Other'),
        ],
        label='Type of support',
    )
    message = forms.CharField(widget=forms.Textarea)
    consent = forms.BooleanField(required=True)

    def save(self):
        support_type = self.cleaned_data['supportType']
        request_type_map = {
            'education': 'education',
            'youth': 'education',
            'entrepreneurship': 'business',
            'community': 'social',
            'referral': 'referral',
            'other': 'general',
        }
        education_detail = ''
        if support_type == 'education':
            education_detail = 'other_education'
        elif support_type == 'youth':
            education_detail = 'career_guidance'

        return ServiceRequest.objects.create(
            request_type=request_type_map.get(support_type, 'general'),
            education_detail=education_detail,
            first_name=self.cleaned_data['firstName'],
            last_name=self.cleaned_data['lastName'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data['phone'],
            message=self.cleaned_data['message'],
            consent_given=True,
            extra_data={'support_type': support_type},
        )


class VolunteerApplicationForm(forms.Form):
    firstName = forms.CharField(max_length=100)
    lastName = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=30)
    interest = forms.CharField(max_length=100)
    availability = forms.CharField(max_length=100)
    skills = forms.CharField(widget=forms.Textarea)
    motivation = forms.CharField(widget=forms.Textarea)
    consent = forms.BooleanField(required=True)

    def save(self):
        service_request = ServiceRequest.objects.create(
            request_type='volunteer',
            first_name=self.cleaned_data['firstName'],
            last_name=self.cleaned_data['lastName'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data['phone'],
            message=self.cleaned_data['motivation'],
            consent_given=True,
            extra_data={
                'interest': self.cleaned_data['interest'],
                'availability': self.cleaned_data['availability'],
                'skills': self.cleaned_data['skills'],
            },
        )
        VolunteerRecord.objects.create(
            first_name=self.cleaned_data['firstName'],
            last_name=self.cleaned_data['lastName'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data['phone'],
            interest_area=self.cleaned_data['interest'],
            availability=self.cleaned_data['availability'],
            skills=self.cleaned_data['skills'],
            motivation=self.cleaned_data['motivation'],
            service_request=service_request,
        )
        return service_request


class ContactEnquiryForm(forms.Form):
    SUBJECT_MAP = {
        'general': 'general',
        'programme': 'general',
        'support': 'social',
        'volunteer': 'volunteer',
        'partnership': 'partnership',
        'donor': 'donor',
        'other': 'general',
    }

    firstName = forms.CharField(max_length=100)
    lastName = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=30, required=False)
    subject = forms.ChoiceField(
        choices=[
            ('general', 'General enquiry'),
            ('programme', 'Programme enquiry'),
            ('support', 'Support enquiry'),
            ('volunteer', 'Volunteering'),
            ('partnership', 'Partnership'),
            ('donor', 'Donor enquiry'),
            ('other', 'Other'),
        ],
    )
    message = forms.CharField(widget=forms.Textarea)
    consent = forms.BooleanField(required=True)

    def save(self):
        subject = self.cleaned_data['subject']
        request_type = self.SUBJECT_MAP.get(subject, 'general')
        service_request = ServiceRequest.objects.create(
            request_type=request_type,
            first_name=self.cleaned_data['firstName'],
            last_name=self.cleaned_data['lastName'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data.get('phone', ''),
            message=self.cleaned_data['message'],
            consent_given=True,
            extra_data={'subject': subject},
        )
        if request_type == 'partnership':
            from dashboard.models import PartnerRecord
            PartnerRecord.objects.create(
                organisation_name=f'{self.cleaned_data["firstName"]} {self.cleaned_data["lastName"]}',
                contact_person=f'{self.cleaned_data["firstName"]} {self.cleaned_data["lastName"]}',
                email=self.cleaned_data['email'],
                phone=self.cleaned_data.get('phone', ''),
                description=self.cleaned_data['message'],
                service_request=service_request,
            )
        elif request_type == 'donor':
            from dashboard.models import DonorRecord
            DonorRecord.objects.create(
                name=f'{self.cleaned_data["firstName"]} {self.cleaned_data["lastName"]}',
                email=self.cleaned_data['email'],
                phone=self.cleaned_data.get('phone', ''),
                notes=self.cleaned_data['message'],
                service_request=service_request,
            )
        return service_request
