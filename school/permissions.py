from rest_framework import permissions


class SchoolViewSetPermissions(permissions.IsAuthenticated):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.user.is_system_admin:
            return True

        if request.user.is_school_admin and view.action in ['update', 'retrieve']:
            return True

        if request.user.is_school_vic_admin and view.action in ['retrieve']:
            return True

        return False

    def has_object_permission(self, request, view, school):
        if request.user.is_system_admin:
            return True

        if request.user.is_school_admin or request.user.is_school_vic_admin:
            if request.user.teacher.school == school: # 必须要求当前学校为老师所在学校
                return True

        return False
