from django.conf import settings
from django.db import models
from django.utils.text import slugify


class PublishStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PENDING = 'pending', 'Pending approval'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'


class SiteSection(models.Model):
    """Editable website sections: background, vision, mission, etc."""

    SECTION_KEYS = [
        ('background', 'Background'),
        ('vision', 'Vision'),
        ('mission', 'Mission'),
        ('core_values', 'Core Values'),
        ('reclaim_theme', 'Reclaim Your Future Theme'),
    ]

    key = models.CharField(max_length=50, choices=SECTION_KEYS, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.PUBLISHED,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_site_sections',
    )

    class Meta:
        ordering = ['key']
        permissions = [
            ('manage_website_content', 'Can manage website content'),
        ]

    def __str__(self):
        return self.get_key_display()


class ProgrammeCategory(models.Model):
    """Centre programme categories displayed on the public site."""

    CATEGORY_CHOICES = [
        ('education_youth', 'Education and Youth Support'),
        ('business_capacity', 'Business Support and Capacity Building'),
        ('women_youth_empowerment', 'Women and Youth Empowerment'),
        ('men_gbvf', 'Men and GBVF Awareness'),
        ('community_outreach', 'Community Outreach and Social Support'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    summary = models.TextField()
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.PUBLISHED,
    )

    class Meta:
        ordering = ['display_order', 'title']
        verbose_name_plural = 'Programme categories'

    def __str__(self):
        return self.title


class PublishedContent(models.Model):
    """Base fields for publishable website content."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    summary = models.TextField(blank=True)
    body = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_approved',
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        super().save(*args, **kwargs)


class NewsArticle(PublishedContent):
    image = models.ImageField(upload_to='news/', blank=True, null=True)

    class Meta:
        ordering = ['-published_at', '-created_at']


class ImpactStory(PublishedContent):
    beneficiary_name = models.CharField(max_length=150, blank=True)
    programme_name = models.CharField(max_length=150, blank=True)
    image = models.ImageField(upload_to='impact/', blank=True, null=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name_plural = 'Impact stories'


class Gallery(PublishedContent):
    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name_plural = 'Galleries'


class GalleryImage(models.Model):
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='galleries/')
    caption = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']


class PartnerAcknowledgement(PublishedContent):
    organisation_name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='partners/', blank=True, null=True)
    website_url = models.URLField(blank=True)

    class Meta:
        ordering = ['organisation_name']


class Opportunity(PublishedContent):
    OPPORTUNITY_TYPES = [
        ('education', 'Education'),
        ('employment', 'Employment'),
        ('funding', 'Funding'),
        ('volunteer', 'Volunteer'),
        ('other', 'Other'),
    ]

    opportunity_type = models.CharField(max_length=30, choices=OPPORTUNITY_TYPES)
    deadline = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    external_link = models.URLField(blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name_plural = 'Opportunities'


class Event(PublishedContent):
    EVENT_TYPES = [
        ('event', 'Event'),
        ('dialogue', 'Community Dialogue'),
        ('campaign', 'Awareness Campaign'),
        ('outreach', 'Outreach Activity'),
        ('workshop', 'Workshop'),
        ('wellness', 'Wellness Activity'),
    ]

    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, default='event')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    registration_link = models.URLField(blank=True)
    is_registration_required = models.BooleanField(default=False)

    class Meta:
        ordering = ['start_date']


class ContactInformation(models.Model):
    """Official contact channels for the public website."""

    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    operating_hours = models.TextField(blank=True)
    map_embed_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Contact information'

    def __str__(self):
        return self.email or 'Contact information'
