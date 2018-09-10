from rest_framework import permissions


class NewsViewSetPermissions(permissions.IsAuthenticated):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.user.is_system_admin:
            return True

        if request.user.is_school_admin and view.action in  ['create', 'update', 'list', 'delete']:
            return True

        if request.user.is_school_vic_admin and view.action in  ['create', 'update', 'list', 'delete']:
            return True

        return False

    # def has_object_permission(self, request, view, obj):
    #     pass


class NotificationViewSetPermissions(permissions.IsAuthenticated):
    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.user.is_system_admin:
            return True

        if request.user.is_school_admin and view.action in  ['create', 'update', 'list', 'delete']:
            return True

        if request.user.is_school_vic_admin and view.action in  ['create', 'update', 'list', 'delete']:
            return True

        return False


class ElectronicBoardAdminOnly(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_electronicboard


class GalleryViewSetPermissions(permissions.IsAuthenticated):
    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.user.is_system_admin:
            return True

        if request.user.is_school_admin and view.action in  ['create', 'update', 'list', 'delete']:
            return True

        if request.user.is_school_vic_admin and view.action in  ['create', 'update', 'list', 'delete']:
            return True

        return False


class HonorViewSetPermissions(permissions.IsAuthenticated):
    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.user.is_system_admin:
            return True

        if request.user.is_school_admin and view.action in  ['create', 'update', 'list', 'delete']:
            return True

        if request.user.is_school_vic_admin and view.action in  ['create', 'update', 'list', 'delete']:
            return True

        return False


class LessonHistoryAttViewSetPermissions(permissions.IsAuthenticated):
    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.user.is_system_admin:
            return True

        if request.user.is_school_admin and view.action in  ['create', 'update', 'list', 'delete']:
            return True

        if request.user.is_school_vic_admin and view.action in  ['create', 'update', 'list', 'delete']:
            return True

        return False

    def has_object_permission(self, request, view, obj):

        return True
