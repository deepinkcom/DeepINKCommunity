from django.db import models
from django.contrib.auth.models import User


class StaffProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True
    )

    job_title = models.CharField(
        max_length=100,
        blank=True
    )

    is_active_staff = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        permissions = [
            (
                'manage_staff_accounts',
                'Can manage staff accounts'
            ),
        ]

    def __str__(self):
        return self.user.get_full_name() or self.user.username