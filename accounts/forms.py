from django.db import IntegrityError
from .username_sequence import next_staff_username
from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm

from .models import StaffProfile


class StaffCreationForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='First Name'
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Last Name'
    )

    email = forms.EmailField(
        required=True,
        label='Email Address'
    )

    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label='Phone Number'
    )

    job_title = forms.CharField(
        max_length=100,
        required=True,
        label='Job Title'
    )

    role = forms.ModelChoiceField(
        queryset=Group.objects.filter(
            name__in=[
                'Administrator',
                'Manager',
                'Staff'
            ]
        ),
        required=True,
        empty_label='Select a role',
        label='Staff Role'
    )

    class Meta:
        model = User

        fields = (
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'job_title',
            'role',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_staff_fields(self)

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):

        user = super().save(commit=False)

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:

            user.username = next_staff_username()
            if User.objects.filter(email__iexact=user.email).exists():
                raise IntegrityError("An account already uses this email.")
            user.save()

            role = self.cleaned_data['role']
            user.groups.add(role)

            StaffProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data[
                    'phone_number'
                ],
                job_title=self.cleaned_data[
                    'job_title'
                ]
            )

        return user


class StaffEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, label='First Name')
    last_name = forms.CharField(max_length=150, required=True, label='Last Name')
    email = forms.EmailField(required=True, label='Email Address')
    phone_number = forms.CharField(max_length=20, required=False, label='Phone Number')
    job_title = forms.CharField(max_length=100, required=True, label='Job Title')

    role = forms.ModelChoiceField(
        queryset=Group.objects.filter(
            name__in=['Administrator', 'Manager', 'Staff']
        ),
        required=True,
        empty_label='Select a role',
        label='Staff Role'
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        self.staff_profile = kwargs.pop('staff_profile', None)
        super().__init__(*args, **kwargs)
        style_staff_fields(self)

        if self.staff_profile is not None:
            self.fields['phone_number'].initial = self.staff_profile.phone_number
            self.fields['job_title'].initial = self.staff_profile.job_title

            current_role = self.instance.groups.first()

            if current_role:
                self.fields['role'].initial = current_role

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)

        if self.staff_profile is not None:
            self.staff_profile.phone_number = self.cleaned_data['phone_number']
            self.staff_profile.job_title = self.cleaned_data['job_title']

            if commit:
                self.staff_profile.save()

        role = self.cleaned_data['role']

        user.groups.clear()
        user.groups.add(role)

        return user

def style_staff_fields(form):
    for name, field in form.fields.items():
        field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
        if name == 'phone_number':
            field.widget.attrs.update({'inputmode': 'tel', 'placeholder': '0821234567'})

