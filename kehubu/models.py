# coding: utf-8
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from model_utils import Choices
from taggit.managers import TaggableManager
from django.utils import timezone


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


class Group(TimeStampedModel):
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
    name = models.CharField(_('name'), max_length=32)
    description = models.TextField(_('description'))
    logo = models.ImageField(_('logo'), upload_to="uploads/kehubu.Group.logo/%Y/%m/%d/", blank=True)
    weighting = models.PositiveSmallIntegerField(_('weighting'), default=0)

    class Meta:
        unique_together = ('creator', 'name')

    def __str__(self):
        return self.name


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
    remark_name = models.CharField(_('remark name'), max_length=32)
    tags =  TaggableManager()
    description = models.TextField(_('description'))
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