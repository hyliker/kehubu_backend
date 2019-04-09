from .models import Group, Profile, Member, GroupMemberRank
from django.contrib.auth.models import User
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class ProfileOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ['user']


class UserOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined')


class UserSerializer(serializers.ModelSerializer):
    kehubu_profile = ProfileOnlySerializer(read_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined', 'kehubu_profile')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"
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



class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    inviter = UserSerializer(read_only=True)
    class Meta:
        model = Member
        fields = "__all__"

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


class GroupMemberRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMemberRank
        fields = "__all__"
