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
            'username',
            'email',
            'phone_number',
            'job_title',
            'role',
            'password1',
            'password2',
        )

    def save(self, commit=True):

        user = super().save(commit=False)

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:

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

        if self.staff_profile:
            self.fields['phone_number'].initial = self.staff_profile.phone_number
            self.fields['job_title'].initial = self.staff_profile.job_title

            current_role = self.instance.groups.first()

            if current_role:
                self.fields['role'].initial = current_role

    def clean(self):
        cleaned_data = super().clean()

        role = cleaned_data.get('role')

        if role and self.instance.pk:
            current_is_admin = self.instance.groups.filter(
                name='Administrator'
            ).exists()

            changing_from_admin = (
                current_is_admin and role.name != 'Administrator'
            )

            if changing_from_admin:
                active_admin_count = User.objects.filter(
                    is_active=True,
                    groups__name='Administrator',
                    staff_profile__is_active_staff=True
                ).exclude(
                    id=self.instance.id
                ).distinct().count()

                if active_admin_count == 0:
                    self.add_error(
                        'role',
                        'The last active Administrator cannot be changed to another role.'
                    )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)

        if self.staff_profile:
            self.staff_profile.phone_number = self.cleaned_data['phone_number']
            self.staff_profile.job_title = self.cleaned_data['job_title']

            if commit:
                self.staff_profile.save()

        role = self.cleaned_data['role']

        user.groups.clear()
        user.groups.add(role)

        return user