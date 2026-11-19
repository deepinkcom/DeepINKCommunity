from django import forms

from dashboard.models import ServiceRequest
import phonenumbers
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


# Shared validation for every public website form.
REGION_NAMES = {'AW': 'Aruba', 'AF': 'Afghanistan', 'AO': 'Angola', 'AI': 'Anguilla', 'AX': 'Åland Islands', 'AL': 'Albania', 'AD': 'Andorra', 'AE': 'United Arab Emirates', 'AR': 'Argentina', 'AM': 'Armenia', 'AS': 'American Samoa', 'AQ': 'Antarctica', 'TF': 'French Southern Territories', 'AG': 'Antigua and Barbuda', 'AU': 'Australia', 'AT': 'Austria', 'AZ': 'Azerbaijan', 'BI': 'Burundi', 'BE': 'Belgium', 'BJ': 'Benin', 'BQ': 'Bonaire, Sint Eustatius and Saba', 'BF': 'Burkina Faso', 'BD': 'Bangladesh', 'BG': 'Bulgaria', 'BH': 'Bahrain', 'BS': 'Bahamas', 'BA': 'Bosnia and Herzegovina', 'BL': 'Saint Barthélemy', 'BY': 'Belarus', 'BZ': 'Belize', 'BM': 'Bermuda', 'BO': 'Bolivia', 'BR': 'Brazil', 'BB': 'Barbados', 'BN': 'Brunei Darussalam', 'BT': 'Bhutan', 'BV': 'Bouvet Island', 'BW': 'Botswana', 'CF': 'Central African Republic', 'CA': 'Canada', 'CC': 'Cocos (Keeling) Islands', 'CH': 'Switzerland', 'CL': 'Chile', 'CN': 'China', 'CI': "Côte d'Ivoire", 'CM': 'Cameroon', 'CD': 'Congo, The Democratic Republic of the', 'CG': 'Congo', 'CK': 'Cook Islands', 'CO': 'Colombia', 'KM': 'Comoros', 'CV': 'Cabo Verde', 'CR': 'Costa Rica', 'CU': 'Cuba', 'CW': 'Curaçao', 'CX': 'Christmas Island', 'KY': 'Cayman Islands', 'CY': 'Cyprus', 'CZ': 'Czechia', 'DE': 'Germany', 'DJ': 'Djibouti', 'DM': 'Dominica', 'DK': 'Denmark', 'DO': 'Dominican Republic', 'DZ': 'Algeria', 'EC': 'Ecuador', 'EG': 'Egypt', 'ER': 'Eritrea', 'EH': 'Western Sahara', 'ES': 'Spain', 'EE': 'Estonia', 'ET': 'Ethiopia', 'FI': 'Finland', 'FJ': 'Fiji', 'FK': 'Falkland Islands (Malvinas)', 'FR': 'France', 'FO': 'Faroe Islands', 'FM': 'Micronesia, Federated States of', 'GA': 'Gabon', 'GB': 'United Kingdom', 'GE': 'Georgia', 'GG': 'Guernsey', 'GH': 'Ghana', 'GI': 'Gibraltar', 'GN': 'Guinea', 'GP': 'Guadeloupe', 'GM': 'Gambia', 'GW': 'Guinea-Bissau', 'GQ': 'Equatorial Guinea', 'GR': 'Greece', 'GD': 'Grenada', 'GL': 'Greenland', 'GT': 'Guatemala', 'GF': 'French Guiana', 'GU': 'Guam', 'GY': 'Guyana', 'HK': 'Hong Kong', 'HM': 'Heard Island and McDonald Islands', 'HN': 'Honduras', 'HR': 'Croatia', 'HT': 'Haiti', 'HU': 'Hungary', 'ID': 'Indonesia', 'IM': 'Isle of Man', 'IN': 'India', 'IO': 'British Indian Ocean Territory', 'IE': 'Ireland', 'IR': 'Iran', 'IQ': 'Iraq', 'IS': 'Iceland', 'IL': 'Israel', 'IT': 'Italy', 'JM': 'Jamaica', 'JE': 'Jersey', 'JO': 'Jordan', 'JP': 'Japan', 'KZ': 'Kazakhstan', 'KE': 'Kenya', 'KG': 'Kyrgyzstan', 'KH': 'Cambodia', 'KI': 'Kiribati', 'KN': 'Saint Kitts and Nevis', 'KR': 'South Korea', 'KW': 'Kuwait', 'LA': "Lao People's Democratic Republic", 'LB': 'Lebanon', 'LR': 'Liberia', 'LY': 'Libya', 'LC': 'Saint Lucia', 'LI': 'Liechtenstein', 'LK': 'Sri Lanka', 'LS': 'Lesotho', 'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia', 'MO': 'Macao', 'MF': 'Saint Martin (French part)', 'MA': 'Morocco', 'MC': 'Monaco', 'MD': 'Moldova, Republic of', 'MG': 'Madagascar', 'MV': 'Maldives', 'MX': 'Mexico', 'MH': 'Marshall Islands', 'MK': 'North Macedonia', 'ML': 'Mali', 'MT': 'Malta', 'MM': 'Myanmar', 'ME': 'Montenegro', 'MN': 'Mongolia', 'MP': 'Northern Mariana Islands', 'MZ': 'Mozambique', 'MR': 'Mauritania', 'MS': 'Montserrat', 'MQ': 'Martinique', 'MU': 'Mauritius', 'MW': 'Malawi', 'MY': 'Malaysia', 'YT': 'Mayotte', 'NA': 'Namibia', 'NC': 'New Caledonia', 'NE': 'Niger', 'NF': 'Norfolk Island', 'NG': 'Nigeria', 'NI': 'Nicaragua', 'NU': 'Niue', 'NL': 'Netherlands', 'NO': 'Norway', 'NP': 'Nepal', 'NR': 'Nauru', 'NZ': 'New Zealand', 'OM': 'Oman', 'PK': 'Pakistan', 'PA': 'Panama', 'PN': 'Pitcairn', 'PE': 'Peru', 'PH': 'Philippines', 'PW': 'Palau', 'PG': 'Papua New Guinea', 'PL': 'Poland', 'PR': 'Puerto Rico', 'KP': 'North Korea', 'PT': 'Portugal', 'PY': 'Paraguay', 'PS': 'Palestine, State of', 'PF': 'French Polynesia', 'QA': 'Qatar', 'RE': 'Réunion', 'RO': 'Romania', 'RU': 'Russia', 'RW': 'Rwanda', 'SA': 'Saudi Arabia', 'SD': 'Sudan', 'SN': 'Senegal', 'SG': 'Singapore', 'GS': 'South Georgia and the South Sandwich Islands', 'SH': 'Saint Helena, Ascension and Tristan da Cunha', 'SJ': 'Svalbard and Jan Mayen', 'SB': 'Solomon Islands', 'SL': 'Sierra Leone', 'SV': 'El Salvador', 'SM': 'San Marino', 'SO': 'Somalia', 'PM': 'Saint Pierre and Miquelon', 'RS': 'Serbia', 'SS': 'South Sudan', 'ST': 'Sao Tome and Principe', 'SR': 'Suriname', 'SK': 'Slovakia', 'SI': 'Slovenia', 'SE': 'Sweden', 'SZ': 'Eswatini', 'SX': 'Sint Maarten (Dutch part)', 'SC': 'Seychelles', 'SY': 'Syria', 'TC': 'Turks and Caicos Islands', 'TD': 'Chad', 'TG': 'Togo', 'TH': 'Thailand', 'TJ': 'Tajikistan', 'TK': 'Tokelau', 'TM': 'Turkmenistan', 'TL': 'Timor-Leste', 'TO': 'Tonga', 'TT': 'Trinidad and Tobago', 'TN': 'Tunisia', 'TR': 'Türkiye', 'TV': 'Tuvalu', 'TW': 'Taiwan', 'TZ': 'Tanzania', 'UG': 'Uganda', 'UA': 'Ukraine', 'UM': 'United States Minor Outlying Islands', 'UY': 'Uruguay', 'US': 'United States', 'UZ': 'Uzbekistan', 'VA': 'Holy See (Vatican City State)', 'VC': 'Saint Vincent and the Grenadines', 'VE': 'Venezuela, Bolivarian Republic of', 'VG': 'Virgin Islands, British', 'VI': 'Virgin Islands, U.S.', 'VN': 'Vietnam', 'VU': 'Vanuatu', 'WF': 'Wallis and Futuna', 'WS': 'Samoa', 'YE': 'Yemen', 'ZA': 'South Africa', 'ZM': 'Zambia', 'ZW': 'Zimbabwe', 'XK': 'Kosovo', 'AC': 'Ascension Island', 'TA': 'Tristan da Cunha'}

def region_label(region):
    return f"{REGION_NAMES.get(region, region)} (+{phonenumbers.country_code_for_region(region)})"

COUNTRY_CHOICES = [('ZA', region_label('ZA'))] + sorted(
    [(r, region_label(r)) for r in phonenumbers.SUPPORTED_REGIONS if r != 'ZA'],
    key=lambda pair: pair[1].casefold(),
)

class PublicContactForm(forms.Form):
    country_code = forms.ChoiceField(choices=COUNTRY_CHOICES, initial='ZA', label='Country calling code')
    phone = forms.CharField(
        max_length=10, min_length=10, strip=False,
        validators=[RegexValidator(r'\A[0-9]{10}\Z', 'Enter exactly 10 digits, without spaces or symbols.')],
        widget=forms.TextInput(attrs={'type':'tel','inputmode':'numeric','pattern':'[0-9]{10}', 'maxlength':'10','minlength':'10','autocomplete':'tel-national','placeholder':'0821234567'}),
    )
    email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs={'autocomplete':'email','placeholder':'name@example.com'}))

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('auto_id', self.__class__.__name__.lower() + '_%s')
        super().__init__(*args, **kwargs)
        if 'firstName' in self.fields:
            self.fields['firstName'].widget.attrs['autocomplete'] = 'given-name'
            self.fields['lastName'].widget.attrs['autocomplete'] = 'family-name'
        if not self.fields['phone'].required:
            self.fields['country_code'].required = False

    def clean(self):
        data = super().clean()
        phone = data.get('phone')
        region = data.get('country_code')
        if phone:
            if not region:
                self.add_error('country_code', 'Select a country calling code.')
            else:
                try:
                    number = phonenumbers.parse(phone, region)
                    if (number.country_code != phonenumbers.country_code_for_region(region)
                            or not phonenumbers.is_possible_number(number)):
                        raise ValueError('Invalid number length for selected country')
                    data['phone'] = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
                except (phonenumbers.NumberParseException, ValueError):
                    self.add_error('phone', 'Enter a valid 10-digit national number for the selected country.')
        return data


class SupportApplicationForm(PublicContactForm):
    firstName = forms.CharField(max_length=100, label='First name')
    lastName = forms.CharField(max_length=100, label='Last name')
    supportType = forms.ChoiceField(
        choices=[
            ('', 'Select an option'),
            ('education', 'Education support'),
            ('youth', 'Youth development'),
            ('entrepreneurship', 'Entrepreneurship support'),
            ('community', 'Community support'),
            ('referral', 'Referral assistance'),
            ('other', 'Other'),
        ],
        label='Type of support',
    )
    message = forms.CharField(max_length=5000, widget=forms.Textarea(attrs={'rows': 4}))
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


class VolunteerApplicationForm(PublicContactForm):
    firstName = forms.CharField(max_length=100)
    lastName = forms.CharField(max_length=100)
    interest = forms.ChoiceField(choices=[('', 'Select an option'), ('education', 'Education'), ('youth', 'Youth development'), ('events', 'Events'), ('outreach', 'Community outreach'), ('administration', 'Administration'), ('other', 'Other')])
    availability = forms.ChoiceField(choices=[('', 'Select an option'), ('weekdays', 'Weekdays'), ('weekends', 'Weekends'), ('events', 'Special events only'), ('flexible', 'Flexible')])
    skills = forms.CharField(max_length=5000, widget=forms.Textarea(attrs={'rows': 4}))
    motivation = forms.CharField(max_length=5000, widget=forms.Textarea(attrs={'rows': 4}))
    consent = forms.BooleanField(required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        # Do not submit another active volunteer application for the same email.
        if ServiceRequest.objects.filter(request_type='volunteer', email__iexact=email).exclude(status__in=['rejected', 'closed']).exists():
            raise ValidationError('An application already exists for this email address. Contact the centre for assistance.')
        return email

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
        return service_request


class ContactEnquiryForm(PublicContactForm):
    SUBJECT_MAP = {
        'general': 'general',
        'programme': 'general',
        'support': 'social',
        'volunteer': 'general',  # Enquiry only; use Get Involved for a volunteer application.
        'partnership': 'partnership',
        'donor': 'donor',
        'other': 'general',
    }

    firstName = forms.CharField(max_length=100)
    lastName = forms.CharField(max_length=100)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False
        self.fields['country_code'].required = False
    subject = forms.ChoiceField(
        choices=[
            ('', 'Select a subject'),
            ('general', 'General enquiry'),
            ('programme', 'Programme enquiry'),
            ('support', 'Support enquiry'),
            ('volunteer', 'Volunteering'),
            ('partnership', 'Partnership'),
            ('donor', 'Donor enquiry'),
            ('other', 'Other'),
        ],
    )
    message = forms.CharField(max_length=5000, widget=forms.Textarea(attrs={'rows': 4}))
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
