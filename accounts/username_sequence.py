import re
from django.contrib.auth.models import Group, User
from django.db import connection
from .models import StaffUsernameSequence


def lock_staff_sequence():
    if not connection.in_atomic_block:
        raise RuntimeError('Username allocation requires an atomic transaction.')
    Group.objects.select_for_update().get(name='Staff')
    sequence, _ = StaffUsernameSequence.objects.select_for_update().get_or_create(pk=1)
    return sequence


def remember_staff_username(sequence, username):
    match = re.fullmatch(r'DIC([0-9]+)', username, re.IGNORECASE)
    if match and int(match.group(1)) > sequence.last_number:
        sequence.last_number = int(match.group(1))
        sequence.save(update_fields=['last_number'])


def next_staff_username():
    sequence = lock_staff_sequence()
    highest = sequence.last_number
    for username in User.objects.filter(username__istartswith='DIC').values_list('username', flat=True):
        match = re.fullmatch(r'DIC([0-9]+)', username, re.IGNORECASE)
        if match:
            highest = max(highest, int(match.group(1)))
    sequence.last_number = highest + 1
    sequence.save(update_fields=['last_number'])
    return f'DIC{sequence.last_number:02d}'
