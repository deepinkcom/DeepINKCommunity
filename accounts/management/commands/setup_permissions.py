from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):

    help = 'Assigns Deep INK staff permissions to roles.'

    def handle(self, *args, **options):

        administrator = Group.objects.get(
            name='Administrator'
        )

        permission = Permission.objects.get(
            codename='manage_staff_accounts',
            content_type__app_label='accounts'
        )

        administrator.permissions.add(permission)

        self.stdout.write(
            self.style.SUCCESS(
                'Administrator permission configured successfully.'
            )
        )