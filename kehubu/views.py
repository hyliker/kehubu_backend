from django.http.response import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .serializers import (
    GroupSerializer, ProfileSerializer, MemberSerializer, JoinGroupSerializer,
    MemberInviterSerializer, MemberUserSerializer, GroupMemberRankSerializer,
    GroupInvitationSerializer, ActionSerializer, GroupAlbumSerializer,
    GroupAlbumImageSerializer, GroupChatSerializer, WxConfigSerializer,
    UserChatSerializer,
)
from .models import (
    Group, Profile, Member, GroupMemberRank, GroupInvitation, GroupAlbum,
    GroupAlbumImage, GroupChat, UserChat,
)
from rest_framework import (
        viewsets, generics, permissions, filters, exceptions, status, views,
)
from .permissions import (
    IsOwnerOrReadOnly, IsGroupCreatorOrReadOnly, IsGroupCreator,
    IsGroupAlbumCreatorOrReadOnly,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from actstream.models import Action
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q


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
            redirect_url = "{}?process=login&next={}".format(weixin_login_url, request.get_full_path())
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
    filterset_fields = ('user', 'nickname', )
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('id', 'nickname', 'birthdate', 'created', 'modified')
    search_fields = ('nickname', 'user__username', 'user__first_name', 'user__last_name')

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user.kehubu_profile)
        return Response(serializer.data)

    def get_queryset(self):
        group_user_ids = self.request.user.kehubu_profile.group_user_ids
        return Profile.objects.filter(user__in=group_user_ids)


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

    def perform_destroy(self, instance):
        if instance.user == self.request.user:
            raise exceptions.APIException('Not allow to delete this item')
        instance.delete()


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
        #FIXME: only return the group related actions for now
        group_set = self.request.user.kehubu_profile.group_set
        group_ids = list(group_set.values_list("pk", flat=True))
        ctype = ContentType.objects.get_for_model(Group)
        return self.queryset.filter(
            Q(
                actor_content_type=ctype,
                actor_object_id__in=group_ids,
            ) | Q(
                target_content_type=ctype,
                target_object_id__in=group_ids,
            ) | Q(
                action_object_content_type=ctype,
                action_object_object_id__in=group_ids,
            ))


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
    permission_classes = [IsGroupAlbumCreatorOrReadOnly, permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ('album', 'album__group' )

    def get_queryset(self):
        user = self.request.user
        user_member_set = user.user_kehubu_member_set.all()
        group_set = user_member_set.values_list("group", flat=True)
        return GroupAlbumImage.objects.filter(album__group__in=group_set)


class GroupChatViewSet(viewsets.ModelViewSet):
    serializer_class = GroupChatSerializer
    queryset = GroupChat.objects.all()
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]
    owner_field = "user"
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ('group', 'user')
    ordering_fields = ('id', 'created', 'modified')

    def get_queryset(self):
        group_set = self.request.user.kehubu_profile.group_set
        return GroupChat.objects.filter(group__in=group_set)


class WxConfigAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WxConfigSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            wxconfig = serializer.save()
            return Response(wxconfig)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class UserChatViewSet(viewsets.ModelViewSet):
    serializer_class = UserChatSerializer
    queryset = UserChat.objects.all()
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]
    owner_field = "sender"
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ('receiver', 'sender')
    ordering_fields = ('id', 'created', 'modified')

    def get_queryset(self):
        user = self.request.user
        qs = UserChat.objects.filter(Q(sender=user) | Q(receiver=user))
        chat_user = self.request.query_params.get('chat_user', None)
        if chat_user:
            try:
                chat_user = int(chat_user)
            except ValueError:
                raise exceptions.APIException("Invalid chat_user param")
            qs = qs.filter(Q(sender=chat_user) | Q(receiver=chat_user))
        return qs
