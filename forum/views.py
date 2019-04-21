from rest_framework import (
        viewsets, generics, permissions, filters, exceptions, status,
)
from .models import Category, Topic, Post, Attachment
from .serializers import (
    CategorySerializer, TopicSerializer, PostSerializer, AttachmentSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from kehubu.permissions import (IsGroupCreatorOrReadOnly, IsOwnerOrReadOnly)
from .permissions import CategoryPermission


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [CategoryPermission]
    filterset_fields = ('group', 'name', 'parent', 'level')
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('id', 'name', 'group', 'priority', 'created', 'modified')
    search_fields = ('name', )

    def get_queryset(self):
        group_ids = self.request.user.kehubu_profile.group_ids
        return self.queryset.filter(group__in=group_ids)


class TopicViewSet(viewsets.ModelViewSet):
    serializer_class = TopicSerializer
    queryset = Topic.objects.all()
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]
    owner_field = "creator"
    filterset_fields = ('category', 'creator', 'category__group')
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('id', 'category', 'creator', 'created', 'modified')
    search_fields = ('title', )

    def get_queryset(self):
        group_ids = self.request.user.kehubu_profile.group_ids
        return self.queryset.filter(category__group__in=group_ids)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]
    owner_field = "creator"
    filterset_fields = ('topic', 'creator', 'topic__category', 'topic__category__group')
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('id', 'topic', 'creator', 'created', 'modified')
    search_fields = ('content', )

    def get_queryset(self):
        group_ids = self.request.user.kehubu_profile.group_ids
        return self.queryset.filter(topic__category__group__in=group_ids)

class AttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = AttachmentSerializer
    queryset = Attachment.objects.all()
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]
    owner_field = "creator"
    filterset_fields = ('group', 'creator', )
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('id', 'group', 'creator', 'created', 'modified')
    search_fields = ('file', )

    def get_queryset(self):
        group_ids = self.request.user.kehubu_profile.group_ids
        return self.queryset.filter(group__in=group_ids)
