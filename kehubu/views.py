from django.http.response import HttpResponseRedirect
from django.urls import reverse
from .serializers import (
    GroupSerializer, ProfileSerializer, MemberSerializer, JoinGroupSerializer,
    MemberInviterSerializer, MemberUserSerializer, GroupMemberRankSerializer,
)
from .models import (
    Group, Profile, Member, GroupMemberRank,
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
    permission_classes = [IsGroupCreator]
    filterset_fields = ('user', 'inviter', 'group')
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('user__kehubu_profile__nickname', 'inviter__kehubu_profile__nickname')

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
