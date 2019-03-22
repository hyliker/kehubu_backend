from django.contrib import admin
from . import models

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'nickname', 'id_type', 'id_number', 'gender', 'birthdate', 'country', 'province', 'city')
    list_filter = ('id_type', 'gender', 'birthdate', 'country', 'province', 'city')
    search_fields = ('id_number', 'nickname', 'user__username')

@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'name', 'weighting', 'logo')
    list_filter = ('created', 'modified')
    search_fields = ('name', )


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