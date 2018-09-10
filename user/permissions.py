# coding=utf-8

from rest_framework import permissions


class TeacherViewSetPermissions(permissions.IsAuthenticated):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.user.is_system_admin:
            return True

        if request.user.is_school_admin and view.action in ['create', 'update', 'list', 'delete']:
            return True

        if request.user.is_school_vic_admin and view.action in  ['update', 'list']:
            return True

        if request.user.is_electronicboard_admin and view.action in ['update', 'list']:
            return True

        return False

    def has_object_permission(self, request, view, teacher):
        if request.user.is_system_admin:
            return True

        if request.user.is_school_admin:
            return True

        if request.user.is_school_vic_admin or request.user.is_electronicboard_admin:
            if request.user.teacher == teacher:
                return True

        return False


class StudentViewPermissions(permissions.IsAuthenticated):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.user.is_system_admin:
            return True

        if request.user.is_school_admin and view.action in  ['create', 'update', 'list', 'delete']:
            return True

        if request.user.is_school_vic_admin and view.action in  ['create', 'update', 'list', 'delete']:
            return True

        if request.user.is_electronicboard_admin and view.action in ['create', 'update', 'list', 'delete']:
            return True

        return False

    def has_object_permission(self, request, view, student):
        if request.user.is_system_admin or request.user.is_school_admin:
            return True

        if request.user.is_school_vic_admin or request.user.is_electronicboard_admin:
            return True

        return False


class BoardIndexViewSetPermissions(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_system_admin:
            return True

        if request.user.is_school_admin and view.action in ['create', 'update', 'list', 'delete']:
            return True

        if request.user.is_school_vic_admin and view.action in ['create', 'update', 'list', 'delete']:
            return True

        if request.user.is_electronicboard_admin and view.action == 'list':
            return True

        return False

    def has_object_permission(self, request, view, board):
        if request.user.is_system_admin:
            return True



        return False


class WebAccess(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and (request.user.is_teacher or request.user.is_system_admin)
