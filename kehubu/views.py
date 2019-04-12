from django.http.response import HttpResponseRedirect
from django.urls import reverse
from .serializers import (
    GroupSerializer, ProfileSerializer, MemberSerializer, JoinGroupSerializer,
    MemberInviterSerializer, MemberUserSerializer, GroupMemberRankSerializer,
    GroupInvitationSerializer, ActionSerializer, GroupAlbumSerializer,
    GroupAlbumImageSerializer,
)
from .models import (
    Group, Profile, Member, GroupMemberRank, GroupInvitation, GroupAlbum,
    GroupAlbumImage,
)
from rest_framework import (
        viewsets, generics, permissions, filters, exceptions, status,
)
from .permissions import (
    IsOwnerOrReadOnly, IsGroupCreatorOrReadOnly, IsGroupCreator,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from actstream.models import Action


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]
    owner_field = "creator"
    filterset_fields = ('creator', 'name', 'members', 'visible')
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('id', 'name', 'member_count', 'weighting', 'visible', 'created', 'modified')
    search_fields = ('name', )

    def perform_create(self, serializer):
        return serializer.save(creator=self.request.user)

    def get_queryset(self):
        if self.action == "join":
            return self.queryset
        return self.queryset.filter_member_user(self.request.user)

    @action(detail=True, permission_classes=[permissions.AllowAny])
    def join(self, request, pk=None):
        if not request.user.is_authenticated:
            weixin_login_url = reverse("weixin_login")
            group_join_url = reverse("group-join", kwargs=dict(pk=pk))
            redirect_url = "{}?process=login&next={}".format(weixin_login_url, group_join_url)
            return HttpResponseRedirect(redirect_url)

        group = self.get_object()
        if group.has_member(request.user):
            return HttpResponseRedirect("/")

        inviter = request.query_params.get('inviter')
        invitation_code = request.query_params.get('invitation_code')
        data = dict(group=group.pk, inviter=inviter)
        serializer = JoinGroupSerializer(data=data, context={
            'request': request, 'group': group, 'invitation_code': invitation_code})
        if serializer.is_valid():
            serializer.save()
            return HttpResponseRedirect("/")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JoinGroupView(generics.CreateAPIView):
    serializer_class = JoinGroupSerializer
    queryset = Member.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    owner_field = "user"

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user.kehubu_profile)
        return Response(serializer.data)


class MemberViewSet(viewsets.ModelViewSet):
    serializer_class = MemberSerializer
    queryset = Member.objects.all()
    permission_classes = [IsGroupCreatorOrReadOnly, permissions.IsAuthenticated]
    filterset_fields = ('user', 'inviter', 'group')
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('user__kehubu_profile__nickname', 'inviter__kehubu_profile__nickname')

    def get_queryset(self):
        user = self.request.user
        user_member_set = user.user_kehubu_member_set.all()
        group_set = user_member_set.values_list("group", flat=True)
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


class GroupInvitationViewSet(viewsets.ModelViewSet):
    serializer_class = GroupInvitationSerializer
    queryset = GroupInvitation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ('group', )
    search_fields = ('group', )

    def get_queryset(self):
        user = self.request.user
        valid = self.request.query_params.get('valid')
        if valid == '1':
            return GroupInvitation.timeframed.filter(inviter=user)
        return user.inviter_kehubu_invitation_code_set.all()


class ActivityListView(generics.ListAPIView):
    serializer_class = ActionSerializer
    queryset = Action.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ('actor_object_id', 'actor_content_type', 'action_object_object_id',
        'action_object_content_type', 'target_object_id', 'target_content_type')

    def get_queryset(self):
        # TODO: filter user related activity set
        return self.queryset


class GroupAlbumViewSet(viewsets.ModelViewSet):
    serializer_class = GroupAlbumSerializer
    queryset = GroupAlbum.objects.all()
    permission_classes = [IsGroupCreatorOrReadOnly, permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ('group', )
    search_fields = ('title', )

    def get_queryset(self):
        user = self.request.user
        user_member_set = user.user_kehubu_member_set.all()
        group_set = user_member_set.values_list("group", flat=True)
        return GroupAlbum.objects.filter(group__in=group_set)


class GroupAlbumImageViewSet(viewsets.ModelViewSet):
    serializer_class = GroupAlbumImageSerializer
    queryset = GroupAlbumImage.objects.all()
    permission_classes = [IsGroupCreatorOrReadOnly, permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ('album', 'album__group' )

    def get_queryset(self):
        user = self.request.user
        user_member_set = user.user_kehubu_member_set.all()
        group_set = user_member_set.values_list("group", flat=True)
        return GroupAlbumImage.objects.filter(album__group__in=group_set)
