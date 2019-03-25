from rest_framework import permissions


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsOwner(permissions.BasePermission):
    owner_field = 'owner'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if hasattr(view, "owner_field"):
            owner = getattr(obj, view.owner_field)
        else:
            owner = getattr(obj, self.owner_field)
        return owner == request.user

class IsGroupCreator(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return request.user == obj.group.creator


class IsOwnerOrReadOnly(permissions.BasePermission):
    owner_field = 'owner'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(view, "owner_field"):
            owner = getattr(obj, view.owner_field)
        else:
            owner = getattr(obj, self.owner_field)
        return owner == request.user


class IsGroupCreatorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user == obj.group.creator