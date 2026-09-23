from django.contrib import admin

from .models import (
    ContactInformation,
    Event,
    Gallery,
    GalleryImage,
    ImpactStory,
    NewsArticle,
    Opportunity,
    PartnerAcknowledgement,
    ProgrammeCategory,
    SiteSection,
)


@admin.register(SiteSection)
class SiteSectionAdmin(admin.ModelAdmin):
    list_display = ['key', 'title', 'status', 'updated_at']


@admin.register(ProgrammeCategory)
class ProgrammeCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'display_order', 'status']


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'published_at']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ImpactStory)
class ImpactStoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'published_at']


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'opportunity_type', 'status', 'deadline']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_date', 'status']


@admin.register(PartnerAcknowledgement)
class PartnerAcknowledgementAdmin(admin.ModelAdmin):
    list_display = ['organisation_name', 'status']


@admin.register(ContactInformation)
class ContactInformationAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone', 'is_active']


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    inlines = [GalleryImageInline]
    list_display = ['title', 'status']
