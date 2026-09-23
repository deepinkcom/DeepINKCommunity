from django.urls import path

from . import portal_views, views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),

    path('dashboard/beneficiaries/', portal_views.beneficiary_list, name='beneficiary_list'),
    path('dashboard/beneficiaries/create/', portal_views.beneficiary_create, name='beneficiary_create'),
    path('dashboard/beneficiaries/<int:pk>/edit/', portal_views.beneficiary_edit, name='beneficiary_edit'),

    path('dashboard/applications/', portal_views.application_list, name='application_list'),
    path('dashboard/applications/<int:pk>/', portal_views.application_detail, name='application_detail'),

    path('dashboard/programmes/', portal_views.programme_list, name='programme_list'),
    path('dashboard/programmes/create/', portal_views.programme_create, name='programme_create'),
    path('dashboard/programmes/<int:pk>/edit/', portal_views.programme_edit, name='programme_edit'),
    path('dashboard/enrolments/create/', portal_views.enrolment_create, name='enrolment_create'),
    path('dashboard/attendance/create/', portal_views.attendance_create, name='attendance_create'),

    path('dashboard/volunteers/', portal_views.volunteer_list, name='volunteer_list'),
    path('dashboard/volunteers/create/', portal_views.volunteer_create, name='volunteer_create'),
    path('dashboard/volunteers/<int:pk>/edit/', portal_views.volunteer_edit, name='volunteer_edit'),

    path('dashboard/events/', portal_views.event_list, name='event_list'),
    path('dashboard/events/create/', portal_views.event_create, name='event_create'),

    path('dashboard/referrals/', portal_views.referral_list, name='referral_list'),
    path('dashboard/referrals/create/', portal_views.referral_create, name='referral_create'),
    path('dashboard/referrals/<int:pk>/edit/', portal_views.referral_edit, name='referral_edit'),

    path('dashboard/partners/', portal_views.partner_list, name='partner_list'),
    path('dashboard/partners/create/', portal_views.partner_create, name='partner_create'),
    path('dashboard/partners/<int:pk>/edit/', portal_views.partner_edit, name='partner_edit'),

    path('dashboard/entrepreneurs/', portal_views.entrepreneur_list, name='entrepreneur_list'),
    path('dashboard/entrepreneurs/create/', portal_views.entrepreneur_create, name='entrepreneur_create'),
    path('dashboard/entrepreneurs/<int:pk>/edit/', portal_views.entrepreneur_edit, name='entrepreneur_edit'),

    path('dashboard/donations/', portal_views.donation_list, name='donation_list'),
    path('dashboard/donations/items/create/', portal_views.donated_item_create, name='donated_item_create'),
    path('dashboard/donations/funding/create/', portal_views.funding_create, name='funding_create'),
    path('dashboard/donations/distributions/create/', portal_views.distribution_create, name='distribution_create'),

    path('dashboard/tasks/', portal_views.task_list, name='task_list'),
    path('dashboard/tasks/create/', portal_views.task_create, name='task_create'),
    path('dashboard/follow-ups/create/', portal_views.follow_up_create, name='follow_up_create'),

    path('dashboard/documents/', portal_views.document_list, name='document_list'),
    path('dashboard/documents/create/', portal_views.document_create, name='document_create'),

    path('dashboard/content/', portal_views.content_home, name='content_home'),
    path('dashboard/content/sections/<int:pk>/edit/', portal_views.content_section_edit, name='content_section_edit'),
    path('dashboard/content/news/', portal_views.news_list, name='news_list'),
    path('dashboard/content/news/create/', portal_views.news_create, name='news_create'),
    path('dashboard/content/news/<int:pk>/approve/', portal_views.news_approve, name='news_approve'),
    path('dashboard/content/impact-stories/', portal_views.impact_story_list, name='impact_story_list'),
    path('dashboard/content/impact-stories/create/', portal_views.impact_story_create, name='impact_story_create'),
    path('dashboard/content/impact-stories/<int:pk>/approve/', portal_views.impact_story_approve, name='impact_story_approve'),
    path('dashboard/content/opportunities/', portal_views.opportunity_list_admin, name='opportunity_list_admin'),
    path('dashboard/content/opportunities/create/', portal_views.opportunity_create, name='opportunity_create'),
    path('dashboard/content/contact/', portal_views.contact_info_edit, name='contact_info_edit'),

    path('dashboard/reports/', portal_views.reports_home, name='reports_home'),
    path('dashboard/reports/export/<str:report_type>/', portal_views.report_export, name='report_export'),

    path('dashboard/audit-log/', portal_views.audit_log_list, name='audit_log_list'),
]
