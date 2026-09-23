from django.conf import settings
from django.db import models
from django.utils import timezone


class BeneficiaryCategory(models.TextChoices):
    YOUTH = 'youth', 'Youth'
    WOMAN = 'woman', 'Woman'
    MAN = 'man', 'Man'
    CHILD = 'child', 'Child'
    ENTREPRENEUR = 'entrepreneur', 'Emerging Entrepreneur'
    FAMILY = 'family', 'Family'
    OTHER = 'other', 'Other'


class RequestStatus(models.TextChoices):
    SUBMITTED = 'submitted', 'Submitted'
    UNDER_REVIEW = 'under_review', 'Under Review'
    ASSIGNED = 'assigned', 'Assigned'
    IN_PROGRESS = 'in_progress', 'In Progress'
    REFERRED = 'referred', 'Referred'
    CLOSED = 'closed', 'Closed'
    REJECTED = 'rejected', 'Rejected'


class Beneficiary(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    category = models.CharField(
        max_length=30,
        choices=BeneficiaryCategory.choices,
        default=BeneficiaryCategory.OTHER,
    )
    support_needs = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_beneficiaries',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name_plural = 'Beneficiaries'
        permissions = [
            ('manage_beneficiaries', 'Can manage beneficiaries'),
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class ServiceRequest(models.Model):
    REQUEST_TYPES = [
        ('education', 'Education Support'),
        ('business', 'Business Support'),
        ('social', 'Social Support'),
        ('referral', 'Referral Services'),
        ('volunteer', 'Volunteer'),
        ('partnership', 'Partnership'),
        ('donor', 'Donor'),
        ('general', 'General Enquiry'),
    ]

    EDUCATION_DETAILS = [
        ('university_application', 'University/College Application'),
        ('career_guidance', 'Career Guidance'),
        ('alternative_opportunities', 'Alternative Opportunities'),
        ('other_education', 'Other Education Support'),
    ]

    reference_number = models.CharField(max_length=20, unique=True, editable=False)
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPES)
    education_detail = models.CharField(
        max_length=40,
        choices=EDUCATION_DETAILS,
        blank=True,
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    message = models.TextField()
    extra_data = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.SUBMITTED,
    )
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_requests',
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests',
    )
    consent_given = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='closed_requests',
    )
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-submitted_at']
        permissions = [
            ('manage_service_requests', 'Can manage service requests'),
        ]

    def __str__(self):
        return f'{self.reference_number} - {self.get_request_type_display()}'

    def save(self, *args, **kwargs):
        if not self.reference_number:
            from django.utils.crypto import get_random_string
            self.reference_number = f'SR-{get_random_string(8).upper()}'
        if self.status == RequestStatus.CLOSED and not self.closed_at:
            self.closed_at = timezone.now()
        super().save(*args, **kwargs)


class Programme(models.Model):
    PROGRAMME_TYPES = [
        ('education_youth', 'Education and Youth Support'),
        ('business_capacity', 'Business Support and Capacity Building'),
        ('women_youth_empowerment', 'Women and Youth Empowerment'),
        ('men_gbvf', 'Men and GBVF Awareness'),
        ('community_outreach', 'Community Outreach and Social Support'),
        ('workshop', 'Workshop'),
        ('wellness', 'Wellness Activity'),
        ('outreach_campaign', 'Outreach Campaign'),
        ('dialogue', 'Community Dialogue'),
    ]

    name = models.CharField(max_length=200)
    programme_type = models.CharField(max_length=40, choices=PROGRAMME_TYPES)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinated_programmes',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        permissions = [
            ('manage_programmes', 'Can manage programmes'),
        ]

    def __str__(self):
        return self.name


class ProgrammeEnrolment(models.Model):
    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name='enrolments',
    )
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='enrolments',
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    enrolled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['programme', 'beneficiary']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f'{self.beneficiary} - {self.programme}'


class Attendance(models.Model):
    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    session_date = models.DateField()
    attended = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-session_date']
        verbose_name_plural = 'Attendance records'

    def __str__(self):
        return f'{self.beneficiary} - {self.session_date}'


class ReferralPartnerType(models.TextChoices):
    SCHOOL = 'school', 'School'
    GOVERNMENT = 'government', 'Government Structure'
    HEALTH = 'health', 'Health Provider'
    NGO = 'ngo', 'NGO'
    OTHER = 'other', 'Other Partner'


class Referral(models.Model):
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='referrals',
    )
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals',
    )
    partner_type = models.CharField(max_length=30, choices=ReferralPartnerType.choices)
    partner_name = models.CharField(max_length=200)
    partner_contact = models.CharField(max_length=200, blank=True)
    reason = models.TextField()
    referral_date = models.DateField(default=timezone.now)
    follow_up_date = models.DateField(null=True, blank=True)
    outcome = models.TextField(blank=True)
    referred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals_made',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-referral_date']
        permissions = [
            ('manage_referrals', 'Can manage referrals'),
        ]

    def __str__(self):
        return f'{self.beneficiary} → {self.partner_name}'


class VolunteerRecord(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    interest_area = models.CharField(max_length=100, blank=True)
    availability = models.CharField(max_length=100, blank=True)
    skills = models.TextField(blank=True)
    motivation = models.TextField(blank=True)
    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='volunteer_record',
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        permissions = [
            ('manage_volunteers', 'Can manage volunteer records'),
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class PartnerRecord(models.Model):
    organisation_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    partnership_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partner_record',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ('manage_partners', 'Can manage partner records'),
        ]

    def __str__(self):
        return self.organisation_name


class DonorRecord(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    donor_type = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donor_record',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ('manage_donors', 'Can manage donor records'),
        ]

    def __str__(self):
        return self.name


class EmergingEntrepreneur(models.Model):
    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='entrepreneur_profile',
        null=True,
        blank=True,
    )
    business_name = models.CharField(max_length=200, blank=True)
    business_type = models.CharField(max_length=100, blank=True)
    support_needed = models.TextField(blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ('manage_entrepreneurs', 'Can manage emerging entrepreneur records'),
        ]

    def __str__(self):
        return self.business_name or f'{self.first_name} {self.last_name}'


class DonatedItem(models.Model):
    ITEM_TYPES = [
        ('clothing', 'Clothing'),
        ('food', 'Food'),
        ('equipment', 'Equipment'),
        ('stationery', 'Stationery'),
        ('other', 'Other'),
    ]

    item_type = models.CharField(max_length=30, choices=ITEM_TYPES)
    description = models.CharField(max_length=300)
    quantity = models.PositiveIntegerField(default=1)
    donor = models.ForeignKey(
        DonorRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donated_items',
    )
    donor_name = models.CharField(max_length=200, blank=True)
    received_date = models.DateField(default=timezone.now)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)

    class Meta:
        permissions = [
            ('manage_donations', 'Can manage donations and distributions'),
        ]

    def __str__(self):
        return f'{self.description} ({self.quantity})'


class Funding(models.Model):
    FUNDING_TYPES = [
        ('grant', 'Grant'),
        ('donation', 'Donation'),
        ('sponsorship', 'Sponsorship'),
        ('other', 'Other'),
    ]

    funding_type = models.CharField(max_length=30, choices=FUNDING_TYPES)
    source = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='ZAR')
    received_date = models.DateField(default=timezone.now)
    purpose = models.TextField(blank=True)
    donor = models.ForeignKey(
        DonorRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='funding_records',
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)

    class Meta:
        permissions = [
            ('manage_donations', 'Can manage donations and distributions'),
        ]

    def __str__(self):
        return f'{self.source} - {self.amount} {self.currency}'


class OutreachDistribution(models.Model):
    DISTRIBUTION_TYPES = [
        ('clothing', 'Clothing'),
        ('winter_support', 'Winter Support'),
        ('food', 'Food Parcels'),
        ('hygiene', 'Hygiene Packs'),
        ('other', 'Other'),
    ]

    distribution_type = models.CharField(max_length=30, choices=DISTRIBUTION_TYPES)
    programme = models.ForeignKey(
        Programme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='distributions',
    )
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='distributions_received',
    )
    description = models.CharField(max_length=300)
    quantity = models.PositiveIntegerField(default=1)
    distribution_date = models.DateField(default=timezone.now)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)

    class Meta:
        permissions = [
            ('manage_donations', 'Can manage donations and distributions'),
        ]

    def __str__(self):
        return f'{self.get_distribution_type_display()} - {self.distribution_date}'


class DocumentCategory(models.TextChoices):
    CONSENT = 'consent', 'Consent Form'
    SUPPORTING = 'supporting', 'Supporting Document'
    EVIDENCE = 'evidence', 'Programme Evidence'
    OTHER = 'other', 'Other'


class Document(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=DocumentCategory.choices)
    file = models.FileField(upload_to='documents/%Y/%m/')
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
    )
    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
    )
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        permissions = [
            ('manage_documents', 'Can manage documents'),
        ]

    def __str__(self):
        return self.title


class TaskStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    OVERDUE = 'overdue', 'Overdue'
    CANCELLED = 'cancelled', 'Cancelled'


class StaffTask(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assigned',
    )
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
    )
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['due_date', '-created_at']
        permissions = [
            ('manage_tasks', 'Can manage staff tasks'),
        ]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.due_date and self.status not in (
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
        ):
            return self.due_date < timezone.now().date()
        return False


class FollowUp(models.Model):
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='follow_ups',
    )
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='follow_ups',
    )
    task = models.ForeignKey(
        StaffTask,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='follow_ups',
    )
    notes = models.TextField()
    follow_up_date = models.DateTimeField(default=timezone.now)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    next_follow_up_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-follow_up_date']

    def __str__(self):
        return f'Follow-up on {self.follow_up_date:%Y-%m-%d}'


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('status_change', 'Status Changed'),
        ('assign', 'Assigned'),
        ('publish', 'Published'),
        ('approve', 'Approved'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50)
    object_repr = models.CharField(max_length=300)
    changes = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        permissions = [
            ('view_audit_log', 'Can view audit log'),
        ]

    def __str__(self):
        return f'{self.action} {self.model_name} #{self.object_id}'
