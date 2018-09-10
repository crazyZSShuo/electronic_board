from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import action

from common.mixins import APIResponseMixin, TinyListModelMixin
from common.response import APIResponse
from school.filters import SchoolFilter
from school.permissions import SchoolViewSetPermissions
from school.serializers import ClassSerializer, SchoolSerializer, TinySchoolSerializer, TinyClassSerializer, \
    SchoolUpdateSerializer, CascaderSchoolSerializer, CascaderClassSerializer, CascaderBoardSerializer
from school.models import School, Class


class SchoolViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, TinyListModelMixin,
                    mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, APIResponseMixin):
    lookup_field = 'school_id'
    serializer_class = SchoolSerializer
    permission_classes = (SchoolViewSetPermissions,)
    queryset = School.objects.all()
    filterset_class = SchoolFilter
    search_fields = ('province', 'city', 'district')

    def get_queryset(self):
        if self.request.user.is_system_admin:
            return super().get_queryset()
        if self.request.user.is_school_admin or self.request.user.is_school_vic_admin:
            return super().get_queryset().filter(school_id=self.request.user.teacher.school.school_id)
        return School.objects.none() # 返回一个空数组

    def get_serializer_class(self):
        if self.action == 'tiny_list':
            return TinySchoolSerializer
        if self.action == 'cascader_school':
            return CascaderSchoolSerializer
        if self.action == 'cascader_class':
            return CascaderClassSerializer
        if self.action == 'cascader_board':
            return CascaderBoardSerializer
        if self.action == 'update':
            return SchoolUpdateSerializer
        return super().get_serializer_class()

    @action(methods=['GET',], detail=False, url_path='cascader_school', url_name='cascader_school')
    def cascader_school(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(data=serializer.data)

    @action(methods=['GET',], detail=False, url_path='cascader_class', url_name='cascader_class')
    def cascader_class(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().exclude(classes=None))
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(data=serializer.data)

    @action(methods=['GET',], detail=False, url_path='cascader_board', url_name='cascader_board')
    def cascader_board(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().exclude(classes__board=None))
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(data=serializer.data)


class ClassViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin,
                   TinyListModelMixin, APIResponseMixin):
    lookup_field = 'class_id'
    serializer_class = ClassSerializer
    queryset = Class.objects.all()
    filter_fields = ('school__school_id',)

    def get_serializer_class(self):
        if self.action == 'tiny_list':
            return TinyClassSerializer
        return super().get_serializer_class()
