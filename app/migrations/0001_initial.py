import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField(blank=True)),
                ('phone', models.CharField(blank=True, max_length=30)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('operating_hours', models.TextField(blank=True)),
                ('map_embed_url', models.URLField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Contact information',
            },
        ),
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=220, unique=True)),
                ('summary', models.TextField(blank=True)),
                ('body', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending approval'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gallery_approved', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gallery_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Galleries',
                'ordering': ['-published_at', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ImpactStory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=220, unique=True)),
                ('summary', models.TextField(blank=True)),
                ('body', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending approval'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('beneficiary_name', models.CharField(blank=True, max_length=150)),
                ('programme_name', models.CharField(blank=True, max_length=150)),
                ('image', models.ImageField(blank=True, null=True, upload_to='impact/')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='impactstory_approved', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='impactstory_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Impact stories',
                'ordering': ['-published_at', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='NewsArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=220, unique=True)),
                ('summary', models.TextField(blank=True)),
                ('body', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending approval'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='news/')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='newsarticle_approved', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='newsarticle_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-published_at', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProgrammeCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('education_youth', 'Education and Youth Support'), ('business_capacity', 'Business Support and Capacity Building'), ('women_youth_empowerment', 'Women and Youth Empowerment'), ('men_gbvf', 'Men and GBVF Awareness'), ('community_outreach', 'Community Outreach and Social Support')], max_length=50, unique=True)),
                ('title', models.CharField(max_length=200)),
                ('summary', models.TextField()),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, max_length=50)),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending approval'), ('published', 'Published'), ('archived', 'Archived')], default='published', max_length=20)),
            ],
            options={
                'verbose_name_plural': 'Programme categories',
                'ordering': ['display_order', 'title'],
            },
        ),
        migrations.CreateModel(
            name='SiteSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(choices=[('background', 'Background'), ('vision', 'Vision'), ('mission', 'Mission'), ('core_values', 'Core Values'), ('reclaim_theme', 'Reclaim Your Future Theme')], max_length=50, unique=True)),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending approval'), ('published', 'Published'), ('archived', 'Archived')], default='published', max_length=20)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_site_sections', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['key'],
                'permissions': [('manage_website_content', 'Can manage website content')],
            },
        ),
        migrations.CreateModel(
            name='PartnerAcknowledgement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=220, unique=True)),
                ('summary', models.TextField(blank=True)),
                ('body', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending approval'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organisation_name', models.CharField(max_length=200)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='partners/')),
                ('website_url', models.URLField(blank=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='partneracknowledgement_approved', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='partneracknowledgement_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['organisation_name'],
            },
        ),
        migrations.CreateModel(
            name='Opportunity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=220, unique=True)),
                ('summary', models.TextField(blank=True)),
                ('body', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending approval'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('opportunity_type', models.CharField(choices=[('education', 'Education'), ('employment', 'Employment'), ('funding', 'Funding'), ('volunteer', 'Volunteer'), ('other', 'Other')], max_length=30)),
                ('deadline', models.DateField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=200)),
                ('external_link', models.URLField(blank=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='opportunity_approved', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='opportunity_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Opportunities',
                'ordering': ['-published_at', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='GalleryImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='galleries/')),
                ('caption', models.CharField(blank=True, max_length=200)),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('gallery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='app.gallery')),
            ],
            options={
                'ordering': ['display_order'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=220, unique=True)),
                ('summary', models.TextField(blank=True)),
                ('body', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending approval'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('event_type', models.CharField(choices=[('event', 'Event'), ('dialogue', 'Community Dialogue'), ('campaign', 'Awareness Campaign'), ('outreach', 'Outreach Activity'), ('workshop', 'Workshop'), ('wellness', 'Wellness Activity')], default='event', max_length=30)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=200)),
                ('registration_link', models.URLField(blank=True)),
                ('is_registration_required', models.BooleanField(default=False)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_approved', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['start_date'],
            },
        ),
    ]
