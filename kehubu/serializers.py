import time
from django.utils.crypto import get_random_string
from .models import (
    Group, Profile, Member, GroupMemberRank, GroupInvitation, GroupAlbum,
    GroupAlbumImage, GroupChat, UserChat,
)
from django.contrib.auth.models import User
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from actstream.models import Action
from drf_extra_fields.fields import Base64ImageField
from .utils import get_wechat_client


class ActionSerializer(serializers.ModelSerializer):
    description = serializers.ReadOnlyField(source='__str__')
    actor = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()
    action_object = serializers.SerializerMethodField()
    actor_url = serializers.SerializerMethodField()
    target_url = serializers.SerializerMethodField()
    action_object_url = serializers.SerializerMethodField()

    class Meta:
        model = Action
        fields = "__all__"

    def get_object(self, obj, attr):
        attrval= getattr(obj, attr)
        if attrval:
            return dict(name=str(attrval), type=attrval.__class__.__name__)

    def get_actor(self, obj):
        return self.get_object(obj, 'actor')

    def get_target(self, obj):
        return self.get_object(obj, 'target')

    def get_action_object(self, obj):
        return self.get_object(obj, 'action_object')

    def get_actor_url(self, obj):
        if obj.actor:
            return obj.actor_url()

    def get_action_object_url(self, obj):
        if obj.action_object:
            return obj.action_object_url()

    def get_target_url(self, obj):
        if obj.target:
            return obj.target_url()


class ProfileOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ['user']


class UserOnlySerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source='get_full_name')
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined', 'full_name')


class UserSerializer(serializers.ModelSerializer):
    kehubu_profile = ProfileOnlySerializer(read_only=True)
    full_name = serializers.ReadOnlyField(source='get_full_name')
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'first_name', 'last_name', 'email', 'is_active', 'date_joined', 'kehubu_profile')


class GroupSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    album_count = serializers.ReadOnlyField()
    forum_stats = serializers.ReadOnlyField()

    class Meta:
        model = Group
        exclude = ["members"]
        read_only_fields = ['creator']

    def validate_name(self, value):
        user = self.context['request'].user
        if self.instance:
            other_group_set = user.creator_kehubu_group_set.exclude(pk=self.instance.pk)
        else:
            other_group_set = user.creator_kehubu_group_set
        if other_group_set.filter(name=value).exists():
            raise serializers.ValidationError(
                _('You cannot create same name group again.')
            )
        return value



class ProfileSerializer(serializers.ModelSerializer):
    user = UserOnlySerializer(read_only=True)
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ['user']


class GroupMemberRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMemberRank
        fields = "__all__"


class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    inviter = UserSerializer(read_only=True)
    class Meta:
        model = Member
        fields = "__all__"

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data['rank'] = GroupMemberRankSerializer(obj.rank).data
        return data


class JoinGroupSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Member
        fields = ['user', 'group', 'inviter', 'created', 'modified']
        read_only_fields = ['created', 'modified']

    def validate_group(self, value):
        user = self.context['request'].user
        if user.user_kehubu_member_set.filter(group=value).exists():
            raise serializers.ValidationError(
                _('You cannot join the same group again.')
            )
        return value

    def validate_inviter(self, value):
        group = self.context['group']
        if value is None:
            if group.visible == Group.VISIBLE.PRIVATE:
                raise serializers.ValidationError('You need an inviter to join in the group')
        else:
            if not group.has_member(value):
                raise serializers.ValidationError(
                    _('Only the member of the group can be your valid inviter.'))

            if self.context['request'].user == value:
                raise serializers.ValidationError('You cannot invite yourself.')

        return value

    def validate(self, data):
        group = data.get('group')
        if group.visible == group.VISIBLE.PRIVATE:
            inviter = data.get('inviter')
            invitation_code = self.context['invitation_code']
            if not group.check_invitation(inviter, invitation_code):
                raise serializers.ValidationError(
                    _('Your invitation code is not existing or expired.'))
        return data


class MemberUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    class Meta:
        model = Member
        fields = ["user", "created", "id", "group"]
        read_only_fields = ['group']
        depth = 1


class MemberInviterSerializer(serializers.ModelSerializer):
    inviter = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    class Meta:
        model = Member
        fields = ["inviter", "created", "id", "group"]
        read_only_fields = ['group']




class GroupPKField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        return Group.objects.filter_member_user(user)

class GroupInvitationSerializer(serializers.ModelSerializer):
    inviter = serializers.HiddenField(default=serializers.CurrentUserDefault())
    group = GroupPKField()
    is_valid = serializers.ReadOnlyField()
    link = serializers.SerializerMethodField()

    class Meta:
        model = GroupInvitation
        fields = "__all__"
        read_only_fields = ['inviter', 'code']

    def get_link(self, obj):
        return self.context['request'].build_absolute_uri(obj.link)

    def validate(self, data):
        start = data.get('start')
        end = data.get('end')

        if start and end:
            if start > end:
                raise serializers.ValidationError(
                    _('End must be greater than start.')
                )
        return data


class GroupAlbumPKField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        return GroupAlbum.objects.filter(group__creator=user)


class GroupAlbumImageSerializer(serializers.ModelSerializer):
    album = GroupAlbumPKField()
    thumb = serializers.SerializerMethodField()

    class Meta:
        model = GroupAlbumImage
        fields = "__all__"

    def get_queryset(self):
        user = self.context['request'].user
        return GroupAlbumImage.objects.all()

    def get_thumb(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(obj.thumb.url)


class GroupAlbumSerializer(serializers.ModelSerializer):
    groupalbumimage_set = GroupAlbumImageSerializer(many=True, read_only=True)
    group = GroupPKField()
    images = serializers.ListField(child=Base64ImageField(), write_only=True, required=False)

    class Meta:
        model = GroupAlbum
        fields = "__all__"

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        album = super().create(validated_data)
        for image in images:
            GroupAlbumImage.objects.create(album=album, image=image)
        return album

    def update(self, instance, validated_data):
        images = validated_data.pop("images", [])
        album = super().update(instance, validated_data)
        for image in images:
            GroupAlbumImage.objects.create(album=album, image=image)
        return instance

class GroupChatSerializer(serializers.ModelSerializer):
    group = GroupPKField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = GroupChat
        fields = "__all__"

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data['user'] = UserSerializer(obj.user).data
        return data


class WxConfigSerializer(serializers.Serializer):
    url = serializers.URLField()

    def validate_url(self, value):
        return value.split("#")[0]

    def save(self ):
        url = self.validated_data.get('url')
        request = self.context.get('request')
        nonceStr = get_random_string(length=16)
        timestamp =  int(time.time())
        wxclient = get_wechat_client(request)
        try:
            ticket = wxclient.jsapi.get_jsapi_ticket()
        except Exception as exc:
            raise serializers.ValidationError(str(exc))
        else:
            signature = wxclient.jsapi.get_jsapi_signature(nonceStr, ticket, timestamp, url)
        return dict(url=url, nonceStr=nonceStr, ticket=ticket, timestamp=timestamp,
                    signature=signature, appid=wxclient.appid)


class SameGroupUserPKField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return self.context['request'].user.kehubu_profile.group_users


class UserChatSerializer(serializers.ModelSerializer):
    receiver = SameGroupUserPKField()
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserChat
        fields = "__all__"

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data['receiver'] = UserSerializer(obj.receiver).data
        data['sender'] = UserSerializer(obj.sender).data
        return data
