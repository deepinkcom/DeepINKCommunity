from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
class Command(BaseCommand):

    help = 'Assigns Deep INK staff permissions to roles.'

    ADMIN_ONLY = [
        ('accounts', 'manage_staff_accounts'),
        ('app', 'manage_website_content'),
        ('dashboard', 'view_audit_log'),
    ]

    MANAGER_PERMISSIONS = [
        ('dashboard', 'manage_beneficiaries'),
        ('dashboard', 'manage_service_requests'),
        ('dashboard', 'manage_programmes'),
        ('dashboard', 'manage_referrals'),
        ('dashboard', 'manage_volunteers'),
        ('dashboard', 'manage_partners'),
        ('dashboard', 'manage_donors'),
        ('dashboard', 'manage_entrepreneurs'),
        ('dashboard', 'manage_donations'),
        ('dashboard', 'manage_documents'),
        ('dashboard', 'manage_tasks'),
    ]

    STAFF_PERMISSIONS = [
        ('dashboard', 'manage_beneficiaries'),
        ('dashboard', 'manage_service_requests'),
        ('dashboard', 'manage_programmes'),
        ('dashboard', 'manage_referrals'),
        ('dashboard', 'manage_volunteers'),
        ('dashboard', 'manage_documents'),
        ('dashboard', 'manage_tasks'),
    ]

    def _get_permission(self, app_label, codename):
        return Permission.objects.filter(
            codename=codename,
            content_type__app_label=app_label,
        ).first()

    def _assign(self, group, permission_specs):
        for app_label, codename in permission_specs:
            try:
                permission = self._get_permission(app_label, codename)
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'Permission {app_label}.{codename} not found — '
                        'run migrations first.'
                    )
                )

    def handle(self, *args, **options):
        administrator = Group.objects.get(name='Administrator')
        manager = Group.objects.get(name='Manager')
        staff = Group.objects.get(name='Staff')

        self._assign(administrator, self.ADMIN_ONLY)
        self._assign(administrator, self.MANAGER_PERMISSIONS)
        self._assign(manager, self.MANAGER_PERMISSIONS)
        self._assign(staff, self.STAFF_PERMISSIONS)

        self.stdout.write(
            self.style.SUCCESS(
                'Role permissions configured successfully.'
            )
        )
