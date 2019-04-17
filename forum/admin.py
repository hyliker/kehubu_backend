from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Category, Topic, Post, Attachment


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'group')
    list_filter = ('created', 'modified')
    search_fields = ('name', )


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('creator', 'category', 'title', 'created', 'modified')
    list_filter = ('created', 'modified')
    search_fields = ('title', )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('creator', 'topic', 'summary', 'created', 'modified')
    list_filter = ('created', 'modified')
    search_fields = ('content', )


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('group', 'creator', 'file', 'mimetype', 'created')
    list_filter = ('created', 'modified')
    search_fields = ('file', )