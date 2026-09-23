from django.contrib import admin

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
    ServiceRequest,
    StaffTask,
    VolunteerRecord,
)


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'category', 'phone', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'phone']


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = [
        'reference_number', 'request_type', 'first_name',
        'last_name', 'status', 'assigned_to', 'submitted_at',
    ]
    list_filter = ['request_type', 'status']
    search_fields = ['reference_number', 'first_name', 'last_name', 'email']


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ['name', 'programme_type', 'start_date', 'is_active']
    list_filter = ['programme_type', 'is_active']


@admin.register(ProgrammeEnrolment)
class ProgrammeEnrolmentAdmin(admin.ModelAdmin):
    list_display = ['beneficiary', 'programme', 'enrolled_at', 'is_active']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['beneficiary', 'programme', 'session_date', 'attended']


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['beneficiary', 'partner_name', 'partner_type', 'referral_date']


@admin.register(VolunteerRecord)
class VolunteerRecordAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'interest_area', 'is_active']


@admin.register(PartnerRecord)
class PartnerRecordAdmin(admin.ModelAdmin):
    list_display = ['organisation_name', 'contact_person', 'email', 'is_active']


@admin.register(DonorRecord)
class DonorRecordAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'donor_type', 'is_active']


@admin.register(EmergingEntrepreneur)
class EmergingEntrepreneurAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'first_name', 'last_name', 'is_active']


@admin.register(DonatedItem)
class DonatedItemAdmin(admin.ModelAdmin):
    list_display = ['description', 'item_type', 'quantity', 'received_date']


@admin.register(Funding)
class FundingAdmin(admin.ModelAdmin):
    list_display = ['source', 'amount', 'currency', 'funding_type', 'received_date']


@admin.register(OutreachDistribution)
class OutreachDistributionAdmin(admin.ModelAdmin):
    list_display = ['description', 'distribution_type', 'quantity', 'distribution_date']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'uploaded_by', 'uploaded_at']


@admin.register(StaffTask)
class StaffTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_to', 'due_date', 'status']
    list_filter = ['status']


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ['follow_up_date', 'recorded_by', 'service_request', 'beneficiary']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'model_name', 'object_repr']
    list_filter = ['action', 'model_name']
    readonly_fields = [
        'user', 'action', 'model_name', 'object_id',
        'object_repr', 'changes', 'timestamp', 'ip_address',
    ]
