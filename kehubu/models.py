# coding: utf-8
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from model_utils.models import TimeStampedModel, TimeFramedModel
from model_utils import Choices
from taggit.managers import TaggableManager
from django.utils import timezone
from django.core.files.base import ContentFile
from urllib.parse import urlparse
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

class Profile(models.Model):
    GENDER = Choices(('m', 'male', _('male')), ('f', 'female', _('female')), ('u', 'unknown', _('unknown')))
    ID_TYPE = Choices(('IdentityCard', _('Identity Card')), ('Passport', _('Passport')))
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        unique=True,
        related_name="kehubu_profile"
    )
    id_type = models.CharField(_('ID type'), choices=ID_TYPE, max_length=32, default=ID_TYPE.IdentityCard)
    id_number = models.CharField(_('ID number'), max_length=32)
    gender = models.CharField(_('gender'), choices=GENDER, default=GENDER.unknown, max_length=1)
    birthdate = models.DateField(_('birthdate'), null=True, blank=True)
    nickname = models.CharField(_('nickname'), max_length=24, blank=True)
    country = models.CharField(_('country'), max_length=32, blank=True)
    province = models.CharField(_('province'), max_length=32, blank=True)
    city = models.CharField(_('city'), max_length=32, blank=True)
    head_image = models.ImageField(_('head image'), upload_to='uploads/kehubu.Profile.head_image/%Y/%m/%d/', blank=True)

    def __str__(self):
        return str(self.user)

    def update_by_socialaccount(self, provider):
        if provider == "weixin":
            self.update_by_social_weixin()

    def update_by_social_weixin(self):
        account = self.user.socialaccount_set.get(provider='weixin')
        data = account.extra_data
        sex = data.get('sex')
        if sex == 1:
            gender = self.GENDER.male
        elif sex == 2:
            gender = self.GENDER.female
        else:
            gender = self.GENDER.unknown
        self.gender =  gender
        self.nickname = data.get('nickname', '')
        self.country = data.get('country', '')
        self.province = data.get('province', '')
        self.city = data.get('city', '')
        headimgurl = data.get('headimgurl', '')
        if headimgurl:
            try:
                response = requests.get(headimgurl, timeout=3)
            except requests.exceptions.ConnectTimeout:
                pass
            else:
                name = urlparse(headimgurl).path.split('/')[-1]
                if response.status_code == 200:
                    self.head_image.save(name, ContentFile(response.content), save=True)
        self.save()


class GroupQuerySet(models.QuerySet):
    def filter_member_user(self, user):
        user_group_ids = user.user_kehubu_member_set.values_list("group", flat=True)
        return self.filter(pk__in=user_group_ids)

    def filter_member_inviter(self, inviter):
        inviter_group_ids = inviter.inviter_kehubu_member_set.values_list("group", flat=True)
        return self.filter(pk__in=inviter_group_ids)


class Group(TimeStampedModel):
    VISIBLE = Choices(
        (0, 'PUBLIC', _('public')),
        (1, 'PRIVATE', _('private')),
        )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="creator_kehubu_group_set"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Member',
        through_fields=('group', 'user'),
        related_name="member_kehubu_group_set"
    )
    member_count = models.PositiveIntegerField(default=0, editable=False)
    name = models.CharField(_('name'), max_length=32)
    description = models.TextField(_('description'), blank=True)
    logo = models.ImageField(_('logo'), upload_to="uploads/kehubu.Group.logo/%Y/%m/%d/", blank=True)
    weighting = models.PositiveSmallIntegerField(_('weighting'), default=0)
    visible = models.PositiveSmallIntegerField(_('visible'), choices=VISIBLE, default=VISIBLE.PUBLIC)

    objects = GroupQuerySet.as_manager()

    class Meta:
        unique_together = ('creator', 'name')

    def __str__(self):
        return self.name

    @property
    def channel_name(self):
        return "kehubu.group.{}".format(self.pk)

    def update_member_count(self):
        self.member_count = self.group_kehubu_member_set.count()
        self.save(update_fields=['member_count'])

    def add_member(self, user, inviter=None):
        return Member.objects.get_or_create(group=self, user=user, defaults=dict(inviter=inviter))

    def add_creator_member(self):
        return self.add_member(self.creator)

    def message_channel(self, message):
        try:
            async_to_sync(channel_layer.group_send)(self.channel_name, message)
        except Exception as exc:
            print(exc)

    def has_member(self, user):
        return self.group_kehubu_member_set.filter(user=user).exists()

    def check_invitation(self, inviter, code):
        return GroupInvitation.timeframed.filter(group=self, inviter=inviter, code=code).exists()


def make_invitation_code():
    return get_random_string(6)

class GroupInvitation(TimeFramedModel):
    group = models.ForeignKey('group', on_delete=models.CASCADE)
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inviter_kehubu_invitation_code_set",
    )
    code = models.CharField(max_length=6, default=make_invitation_code, editable=False)

    def __str__(self):
        return self.code

    @property
    def link(self):
        group_join_url = reverse("group-join", kwargs=dict(pk=self.group_id))
        return "{}?inviter={}&invitation_code={}".format(group_join_url, self.inviter_id, self.code)

    @property
    def is_valid(self):
        if self.end is None:
            return True
        return self.end >= timezone.now()

    def clean(self):
        if self.start and self.end:
            if self.start > self.end:
                raise ValidationError({
                    'end': _('End must be greater than start.')})


class GroupMemberRank(TimeStampedModel):
    group = models.ForeignKey('group', on_delete=models.CASCADE)
    name = models.CharField(_('rank'), max_length=32)
    weighting = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ('group', 'name')

    def __str__(self):
        return self.name


class Member(TimeStampedModel):
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        related_name="group_kehubu_member_set"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_kehubu_member_set",
    )
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inviter_kehubu_member_set",
    )
    rank = models.ForeignKey(
        'GroupMemberRank',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
    )
    remark_name = models.CharField(_('remark name'), max_length=32, blank=True)
    tags =  TaggableManager(blank=True)
    description = models.TextField(_('description'), blank=True)
    is_starred = models.NullBooleanField(_('is starred'))
    is_blocked = models.NullBooleanField(_('is blocked'))

    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        return '{}:{}'.format(self.group, self.user)

    @property
    def is_invited(self):
        return self.inviter is not None


class MobileNumber(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="kehubu_mobilenumber_set",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    number = models.CharField(_('number'), max_length=13, unique=True)
    is_verified = models.BooleanField(_('is verified'), default=False)
    verification_code = models.CharField(_('verification code'), max_length=16)
    verification_code_expired = models.DateTimeField(
        _('verification code expired'),
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.number

    @property
    def is_verification_code_expired(self):
        if self.verification_code_expired:
            return timezone.now() > self.verification_code_expired
        return False
