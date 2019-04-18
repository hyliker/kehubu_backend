from .models import (
    Category, Topic, Post, Attachment,
)
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import Base64FileField
from kehubu.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"



class TopicSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    class Meta:
        model = Topic
        fields = "__all__"

    def validate(self, attrs):
        attrs['creator'] = self.context['request'].user
        return attrs


class PostSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    class Meta:
        model = Post
        fields = "__all__"

    def validate(self, attrs):
        attrs['creator'] = self.context['request'].user
        return attrs


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = "__all__"