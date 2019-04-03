from django.dispatch import receiver
from django.db.models import signals
from .models import Member, Group, Profile
from django.conf import settings


@receiver(signals.post_save, sender=Member)
def member_post_save(sender, instance, created, **kwargs):
    if created:
        group = instance.group
        group.update_member_count()


@receiver(signals.post_delete, sender=Member)
def member_post_delete(sender, instance, **kwargs):
    group = instance.group
    group.update_member_count()


@receiver(signals.post_save, sender=Group)
def group_post_save(sender, instance, created, **kwargs):
    if created:
        instance.add_creator_member()


@receiver(signals.post_save, sender=settings.AUTH_USER_MODEL)
def user_model_post_save(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
