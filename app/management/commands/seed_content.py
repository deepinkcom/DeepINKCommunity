from django.core.management.base import BaseCommand

from app.models import ContactInformation, ProgrammeCategory, PublishStatus, SiteSection


DEFAULT_SECTIONS = [
    {
        'key': 'background',
        'title': 'Our Story',
        'content': (
            'Deep INK Community Centre is dedicated to empowering individuals '
            'and strengthening communities through education, youth development, '
            'entrepreneurship support, and social outreach.'
        ),
    },
    {
        'key': 'vision',
        'title': 'Our Vision',
        'content': (
            'A thriving community where every person has access to education, '
            'opportunity, and the support needed to reclaim their future.'
        ),
    },
    {
        'key': 'mission',
        'title': 'Our Mission',
        'content': (
            'To provide holistic support through programmes that address '
            'education, business development, empowerment, GBVF awareness, '
            'and community outreach.'
        ),
    },
    {
        'key': 'core_values',
        'title': 'Core Values',
        'content': (
            'Compassion, Inclusivity, Integrity, Empowerment, and Collaboration '
            'guide everything we do at Deep INK Community Centre.'
        ),
    },
    {
        'key': 'reclaim_theme',
        'title': 'Reclaim Your Future',
        'content': (
            'Reclaim Your Future is Deep INK\'s guiding theme — helping youth, '
            'women, men, and entrepreneurs take ownership of their path forward '
            'through education, skills, and community support.'
        ),
    },
]

DEFAULT_PROGRAMMES = [
    {
        'category': 'education_youth',
        'title': 'Education and Youth Support',
        'summary': (
            'University and college application assistance, career guidance, '
            'and alternative learning opportunities for young people.'
        ),
        'icon': 'bi-book',
        'display_order': 1,
    },
    {
        'category': 'business_capacity',
        'title': 'Business Support and Capacity Building',
        'summary': (
            'Support for emerging entrepreneurs including business planning, '
            'capacity building, and access to resources.'
        ),
        'icon': 'bi-briefcase',
        'display_order': 2,
    },
    {
        'category': 'women_youth_empowerment',
        'title': 'Women and Youth Empowerment',
        'summary': (
            'Programmes that build confidence, skills, and leadership '
            'among women and young people in our community.'
        ),
        'icon': 'bi-person-hearts',
        'display_order': 3,
    },
    {
        'category': 'men_gbvf',
        'title': 'Men and GBVF Awareness',
        'summary': (
            'Dialogues and awareness campaigns addressing gender-based violence '
            'and promoting positive masculinity.'
        ),
        'icon': 'bi-shield-check',
        'display_order': 4,
    },
    {
        'category': 'community_outreach',
        'title': 'Community Outreach and Social Support',
        'summary': (
            'Outreach activities, social support, and referral services '
            'connecting community members with essential resources.'
        ),
        'icon': 'bi-heart',
        'display_order': 5,
    },
]


class Command(BaseCommand):
    help = 'Seeds default website content and programme categories.'

    def handle(self, *args, **options):
        for section in DEFAULT_SECTIONS:
            SiteSection.objects.update_or_create(
                key=section['key'],
                defaults={
                    'title': section['title'],
                    'content': section['content'],
                    'status': PublishStatus.PUBLISHED,
                },
            )

        for programme in DEFAULT_PROGRAMMES:
            ProgrammeCategory.objects.update_or_create(
                category=programme['category'],
                defaults={
                    'title': programme['title'],
                    'summary': programme['summary'],
                    'icon': programme['icon'],
                    'display_order': programme['display_order'],
                    'status': PublishStatus.PUBLISHED,
                },
            )

        ContactInformation.objects.get_or_create(
            is_active=True,
            defaults={
                'address': 'Address to be confirmed',
                'phone': 'Phone number to be confirmed',
                'email': 'info@deepink.org.za',
                'operating_hours': 'Operating days and hours to be confirmed.',
            },
        )

        self.stdout.write(
            self.style.SUCCESS('Default content seeded successfully.')
        )
