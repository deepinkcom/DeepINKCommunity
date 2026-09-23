from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import ServiceRequest, StaffTask, TaskStatus
from .utils import log_audit


@receiver(pre_save, sender=ServiceRequest)
def track_service_request_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = ServiceRequest.objects.get(pk=instance.pk)
            if old.status != instance.status:
                instance._status_changed = {
                    'from': old.status,
                    'to': instance.status,
                }
        except ServiceRequest.DoesNotExist:
            pass


@receiver(post_save, sender=ServiceRequest)
def audit_service_request(sender, instance, created, **kwargs):
    if created:
        log_audit(None, 'create', instance)
    elif hasattr(instance, '_status_changed'):
        log_audit(
            None,
            'status_change',
            instance,
            changes=instance._status_changed,
        )


@receiver(post_save, sender=StaffTask)
def update_overdue_tasks(sender, instance, **kwargs):
    if instance.is_overdue and instance.status == TaskStatus.PENDING:
        StaffTask.objects.filter(pk=instance.pk).update(
            status=TaskStatus.OVERDUE
        )
