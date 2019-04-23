from django.contrib import admin
from . import models

admin.site.site_header = 'kehubu administration'
admin.site.site_title = 'kehubu site admin'

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'nickname', 'id_type', 'id_number', 'gender', 'birthdate', 'country', 'province', 'city')
    list_filter = ('id_type', 'gender', 'birthdate', 'country', 'province', 'city')
    search_fields = ('id_number', 'nickname', 'user__username')

@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'name', 'visible', 'member_count', 'weighting', 'logo', 'notice_updated')
    list_filter = ('created', 'modified', 'visible')
    search_fields = ('name', )


@admin.register(models.GroupInvitation)
class GroupInvitationAdmin(admin.ModelAdmin):
    list_display = ('group', 'inviter', 'code', 'start', 'end', 'is_valid')
    list_filter = ('start', 'end')
    search_fields = ('group__name', 'inviter__username', 'code')


@admin.register(models.Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'inviter', 'remark_name', 'is_starred', 'is_blocked')
    list_filter = ('created', 'modified', 'is_starred', 'is_blocked')
    search_fields = ('group__name', )


@admin.register(models.MobileNumber)
class MobileMemberAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'number', 'is_verified', 'verification_code', 'verification_code_expired',
        'is_verification_code_expired', 'created', 'modified')
    list_filter = ('is_verified', )
    search_fields = ('number', )


@admin.register(models.GroupMemberRank)
class GroupMemberRankAdmin(admin.ModelAdmin):
    list_display = ('group', 'name', 'weighting', 'created')
    search_fields = ('name', )
    list_filter = ('created', 'modified')


class GroupAlbumImageInline(admin.TabularInline):
    model = models.GroupAlbumImage


@admin.register(models.GroupAlbum)
class GroupAlbumAdmin(admin.ModelAdmin):
    list_display = ('group', 'title', 'created')
    search_fields = ('title', )
    list_filter = ('created', 'modified')
    inlines = [GroupAlbumImageInline]


@admin.register(models.GroupAlbumImage)
class GroupAlbumImageAdmin(admin.ModelAdmin):
    list_display = ('album', 'image', 'created')
    list_filter = ('created', 'modified')
    search_fields = ('album__title', )


@admin.register(models.GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'message_summary', 'created', 'modified')
    list_filter = ('created', 'modified')
    search_fields = ('message', )


@admin.register(models.UserChat)
class UserChatAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message_summary', 'created', 'modified')
    list_filter = ('created', 'modified')
    search_fields = ('message', )
