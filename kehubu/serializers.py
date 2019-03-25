from .models import Group, Profile, Member
from django.contrib.auth.models import User
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"
        read_only_fields = ['creator']

    def validate_name(self, value):
        user = self.context['request'].user
        if user.creator_kehubu_group_set.filter(name=value).exists():
            raise serializers.ValidationError(
                _('You cannot create same name group again.')
            )
        return value


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
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
        if self.context['request'].user == value:
            raise serializers.ValidationError('Invalid inviter')
        return value


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