from django.contrib import admin
from .models import StaffProfile


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'job_title',
        'phone_number',
        'is_active_staff',
        'created_at',
    )

    list_filter = (
        'is_active_staff',
    )

    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'job_title',
    )