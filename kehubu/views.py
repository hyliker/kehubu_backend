from .serializers import (
    GroupSerializer, ProfileSerializer, MemberSerializer, JoinGroupSerializer,
    MemberInviterSerializer, MemberUserSerializer, GroupMemberRankSerializer,
)
from .models import (
    Group, Profile, Member, GroupMemberRank,
)
from rest_framework import (
    viewsets, generics, permissions
)
from .permissions import (
    IsOwnerOrReadOnly, IsGroupCreatorOrReadOnly, IsGroupCreator,
)

class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    owner_field = "creator"
    filterset_fields = ('creator', 'name', 'members')

    def perform_create(self, serializer):
        return serializer.save(creator=self.request.user)


class JoinGroupView(generics.CreateAPIView):
    serializer_class = JoinGroupSerializer
    queryset = Member.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    owner_field = "user"


class MemberViewSet(viewsets.ModelViewSet):
    serializer_class = MemberSerializer
    queryset = Member.objects.all()
    permission_classes = [IsGroupCreator]
    filterset_fields = ('user', 'inviter', 'group')

    def get_queryset(self):
        user = self.request.user
        group_set = user.creator_kehubu_group_set.all()
        return Member.objects.filter(group__in=group_set)


class MemberInviterViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MemberInviterSerializer
    queryset = Member.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ('user', 'inviter', 'group')

    def get_queryset(self):
        user = self.request.user
        return user.user_kehubu_member_set.all()


class MemberUserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MemberUserSerializer
    queryset = Member.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ('user', 'user', 'group')

    def get_queryset(self):
        user = self.request.user
        return user.inviter_kehubu_member_set.all()


class GroupMemberRankViewSet(viewsets.ModelViewSet):
    serializer_class = GroupMemberRankSerializer
    queryset = GroupMemberRank.objects.all()
    permission_classes = [IsGroupCreator]
    filterset_fields = ('group', )

    def get_queryset(self):
        user = self.request.user
        group_set = user.creator_kehubu_group_set.all()
        return GroupMemberRank.objects.filter(group__in=group_set)