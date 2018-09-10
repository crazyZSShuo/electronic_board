from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import mixins, viewsets, decorators, permissions, renderers, parsers
from rest_framework.views import APIView
from rest_framework.response import Response

from common.mixins import APIResponseMixin, APIResponse

from django.db.models import Q

from electronicboard.filters import NewsFilter, GalleryFilter, HonorFilter, NotificationFilter, LessonHistoryAttFilter
from electronicboard.models import GalleryImageItem, Gallery, Notification, Honor, SchoolNews, Lesson, \
    LessonAttendanceStudent, LessonAttendanceHistory, HonorImageItem
from electronicboard.permissions import NewsViewSetPermissions, NotificationViewSetPermissions, \
    GalleryViewSetPermissions, HonorViewSetPermissions, LessonHistoryAttViewSetPermissions
from electronicboard.serializers import ClassNotificationSerializer, \
    ClassHonorSerializer, SchoolNewsSerializer, LessonSerializer, \
    ClassInfoSerializer, GalleryImageItemSerializer, \
    ClassHonorDetailSerializer, ClassGallerySerializer, ClassIndexSerializer, LessonAttendanceSerializer, \
    HistoryAttendanceQuerySerializer, LessonAttendanceHistoryItemSerializer, TeacherDetailSerializer, \
    TeacherListSerializer, LessonHistorySerializer, GallerySerializer, HonorSerializer, \
    HonorDetailSerializer, NotificationSerializer, NewsSerializer, GalleryCreateSerializer, HonorCreateSerializer, \
    NotificationCreateSerializer, NewsCreateSerializer, GalleryDetailSerializer, GalleryUpdateSerializer, \
    GalleryImageItemCreateSerializer, HonorImageItemCreateSerializer

from electronicboard.permissions import ElectronicBoardAdminOnly
from user.models import Teacher


class TeacherViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                     APIResponseMixin):
    queryset = Teacher.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = (ElectronicBoardAdminOnly,)
    lookup_field = 'teacher_id'

    def get_serializer_class(self):
        if self.action in ['list']:
            return TeacherListSerializer
        elif self.action in ['retrieve', 'destroy', 'update', 'partial_update', 'create']:
            return TeacherDetailSerializer
        return super().get_serializer_class()


class ClassInfoAPIView(APIView):
    permission_classes = (ElectronicBoardAdminOnly,)

    def get(self, request):
        return APIResponse(data=ClassInfoSerializer(instance=request.user.board.clazz).data)


class ClassIndexAPIView(APIView):
    permission_classes = (ElectronicBoardAdminOnly,)

    def get(self, request):
        notification = Notification.objects.filter(
            Q(school=self.request.user.board.clazz.school) |
            Q(clazz=self.request.user.board.clazz)).first()
        honor = Honor.objects.filter(Q(clazz=self.request.user.board.clazz)).first()
        news = SchoolNews.objects.filter(Q(school=self.request.user.board.clazz.school)).first()
        context = {
            'request': request,
            'view': self,
        }

        return APIResponse(data=ClassIndexSerializer(instance={
            'notification': notification,
            'honor': honor,
            'news': news,
        }, context=context).data)


class LessonFormViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, APIResponseMixin):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (ElectronicBoardAdminOnly,)
    pagination_class = LimitOffsetPagination
    lookup_field = 'lesson_id'

    def get_serializer_class(self):
        if self.action == 'upload_attendances':
            return LessonAttendanceSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        q = Q(clazz=self.request.user.board.clazz)
        return Lesson.objects.filter(q).order_by('-created_time').all()

    @decorators.detail_route(methods=['POST', ], )
    def upload_attendances(self, request, lesson_id):
        return APIResponse()

    @decorators.detail_route(methods=['GET', ], )
    def history_attendances(self, request, lesson_id):
        serializer = HistoryAttendanceQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        date = serializer.validated_data['date']
        items = LessonAttendanceStudent.objects.filter(history__date=date, history__lesson=self.get_object())
        return APIResponse(data=LessonAttendanceHistoryItemSerializer(instance=items, many=True).data)


class ClassNotificationViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, APIResponseMixin):
    permission_classes = (ElectronicBoardAdminOnly,)
    serializer_class = ClassNotificationSerializer
    pagination_class = LimitOffsetPagination
    filter_fields = ('type',)

    def get_queryset(self):
        q = Q(school=self.request.user.board.clazz.school) | Q(clazz=self.request.user.board.clazz)
        return Notification.objects.filter(q).order_by('-created_time').all()


class ClassGalleryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, \
                          mixins.UpdateModelMixin,mixins.DestroyModelMixin,APIResponseMixin):
    queryset = Gallery.objects.all()
    serializer_class = ClassGallerySerializer
    permission_classes = (ElectronicBoardAdminOnly,)

    @decorators.list_route(methods=['GET', ], )
    def imgs(self, request):
        data = GalleryImageItem.objects.filter(
            gallery__clazz=request.user.board.clazz,
            gallery__is_show=True
        ).all()
        return APIResponse(data=GalleryImageItemSerializer(instance=data, many=True).data)


class ClassHonorViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, APIResponseMixin):
    serializer_class = ClassHonorSerializer
    permission_classes = (ElectronicBoardAdminOnly,)
    pagination_class = LimitOffsetPagination
    lookup_field = 'honor_id'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClassHonorDetailSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        # q = Q(clazz=self.request.user.board.clazz)
        return Honor.objects.filter().order_by('-created_time')


class SchoolNewsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, APIResponseMixin):
    serializer_class = SchoolNewsSerializer
    permission_class = (ElectronicBoardAdminOnly,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        q = Q(school=self.request.user.board.clazz.school)
        return SchoolNews.objects.filter(q).order_by('-created_time')


class SchoolNewsRichContentView(APIView):
    permission_classes = (permissions.AllowAny,)
    renderer_classes = (renderers.StaticHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        news_id = request.query_params.get('news_id', -1)
        news = SchoolNews.objects.get(news_id=news_id)
        return Response(data='<html><body>{}</body></html>'.format(news.rich_content))


class GalleryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,mixins.UpdateModelMixin, mixins.DestroyModelMixin, APIResponseMixin):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    lookup_field = 'gallery_id'
    permission_classes = (GalleryViewSetPermissions,)
    filterset_class = GalleryFilter
    search_fields = ('clazz__school__province', 'clazz__school__city', 'clazz__school__district')

    def get_serializer_class(self):
        if self.action == 'create':
            return GalleryCreateSerializer
        if self.action == 'retrieve':
            return GalleryDetailSerializer
        if self.action == 'update':
            return GalleryUpdateSerializer
        return super().get_serializer_class()


class GalleryImageItemViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                              APIResponseMixin):
    queryset = GalleryImageItem.objects.all()
    serializer_class = GalleryImageItemCreateSerializer
    permission_classes = (GalleryViewSetPermissions,)
    parser_classes = (parsers.JSONParser, parsers.MultiPartParser)
    lookup_field = 'item_id'


class HonorViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin, mixins.CreateModelMixin, APIResponseMixin):
    serializer_class = HonorSerializer
    pagination_class = LimitOffsetPagination
    lookup_field = 'honor_id'
    permission_classes = (HonorViewSetPermissions,)
    filterset_class = HonorFilter
    search_fields = ('clazz__school__province', 'clazz__school__city', 'clazz__school__district')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HonorDetailSerializer

        if self.action == 'create':
            return HonorCreateSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        # q = Q(clazz__in=self.request.user.teacher.classes.all())
        return Honor.objects.filter().order_by('-created_time')


class HonorImageItemViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                              APIResponseMixin):
    queryset = HonorImageItem.objects.all()
    serializer_class = HonorImageItemCreateSerializer
    permission_classes = (HonorViewSetPermissions,)
    parser_classes = (parsers.JSONParser, parsers.MultiPartParser)
    lookup_field = 'item_id'


class NotificationViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                          mixins.DestroyModelMixin,APIResponseMixin):
    queryset = Notification.objects.all()
    permission_classes = (NotificationViewSetPermissions,)
    serializer_class = NotificationSerializer
    pagination_class = LimitOffsetPagination
    filterset_class = NotificationFilter
    search_fields = ('school__province', 'school__city', 'school__district', 'clazz__school__province',\
                     'clazz__school__city', 'clazz__school__district')

    lookup_field = 'notification_id'

    def get_queryset(self):
        if self.request.user.is_system_admin:
            return super().get_queryset()
        if self.request.user.is_school_admin or self.request.user.is_school_vic_admin:
            return super().get_queryset().filter(school=self.request.user.teacher.school)

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer

        return super().get_serializer_class()

    # def get_queryset(self):
    #     # q = Q(school=self.request.user.teacher.school) | Q(clazz=self.request.user.teacher.classes)
    #     return Notification.objects.filter().order_by('-created_time').all()


class NewsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,mixins.CreateModelMixin, mixins.DestroyModelMixin,\
                  APIResponseMixin):
    queryset = SchoolNews.objects.all()
    serializer_class = NewsSerializer
    permission_classes = (NewsViewSetPermissions,)
    pagination_class = LimitOffsetPagination
    lookup_field = 'news_id'

    filterset_class = NewsFilter
    search_fields = ('school__province', 'school__city', 'school__district')

    def get_queryset(self):
        if self.request.user.is_system_admin:
            return super().get_queryset()
        if self.request.user.is_school_admin or self.request.user.is_school_vic_admin:
            return super().get_queryset().filter(school=self.request.user.teacher.school)

    # def get_queryset(self):
    #     # q = Q(school=self.request.user.teacher.school)
    #     return SchoolNews.objects.filter().order_by('-created_time')

    def get_serializer_class(self):
        if self.action == 'create':
            return NewsCreateSerializer

        return super().get_serializer_class()


class LessonHistoryAttViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, APIResponseMixin):
    serializer_class = LessonHistorySerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (LessonHistoryAttViewSetPermissions,)
    filterset_class = LessonHistoryAttFilter
    search_fields = ('clazz__school__province', 'clazz__school__city', 'clazz__school__district')
    queryset = LessonAttendanceHistory.objects.all()

    def get_queryset(self):
        self.get_object()
        if self.request.user.is_system_admin:
            return super().get_queryset()
        if self.request.user.is_school_admin or self.request.user.is_school_vic_admin:
            return super().get_queryset().filter(clazz__school=self.request.user.teacher.school)
        if self.request.user.is_electronicboard_admin:
            return super().get_queryset().filter(clazz__in=self.request.user.teacher.classes.all())
        return LessonAttendanceHistory.objects.none()
