from rest_framework import permissions

class CategoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        if request.method == 'POST':
            group = request.data.get('group')
            if not request.user.creator_kehubu_group_set.filter(pk=group).exists():
                return False
            return True
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user == obj.group.creator
