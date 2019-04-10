from django.dispatch import receiver
from django.db.models import signals
from allauth.socialaccount.signals import (
    social_account_added, social_account_updated
)
from .models import Member, Group, Profile
from django.conf import settings
from .serializers import MemberSerializer
from actstream import action



@receiver(signals.post_save, sender=Member)
def member_post_save(sender, instance, created, **kwargs):
    if created:
        group = instance.group
        group.update_member_count()
        serializer = MemberSerializer(instance)
        group.message_channel(dict(type='kehubu.member.add', member=serializer.data))
        action.send(instance.user, verb='joined', target=group)


@receiver(signals.post_delete, sender=Member)
def member_post_delete(sender, instance, **kwargs):
    group = instance.group
    group.update_member_count()
    serializer = MemberSerializer(instance)
    group.message_channel(dict(type='kehubu.member.delete', member=serializer.data))


@receiver(signals.post_save, sender=Group)
def group_post_save(sender, instance, created, **kwargs):
    if created:
        instance.add_creator_member()


@receiver(signals.post_save, sender=settings.AUTH_USER_MODEL)
def user_model_post_save(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(social_account_added)
def on_social_account_added(request, sociallogin, **kwargs):
    provider = sociallogin.account.provider
    sociallogin.user.kehubu_profile.update_by_socialaccount(provider)

@receiver(social_account_updated)
def on_social_account_updated(request, sociallogin, **kwargs):
    provider = sociallogin.account.provider
    sociallogin.user.kehubu_profile.update_by_socialaccount(provider)
