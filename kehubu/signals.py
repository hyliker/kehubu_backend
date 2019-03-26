from django.dispatch import receiver
from django.db.models import signals
from .models import Member


@receiver(signals.post_save, sender=Member)
def member_post_save(sender, instance, created, **kwargs):
    if created:
        group = instance.group
        group.update_member_count()


@receiver(signals.post_delete, sender=Member)
def member_post_delete(sender, instance, **kwargs):
    group = instance.group
    group.update_member_count()