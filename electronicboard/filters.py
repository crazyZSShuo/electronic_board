import django_filters
from django.db.models import Q

from electronicboard.models import SchoolNews, Gallery, Honor, Notification,LessonAttendanceHistory


class NewsFilter(django_filters.rest_framework.FilterSet):
    school = django_filters.CharFilter(field_name='school__name', lookup_expr='contains')
    content = django_filters.CharFilter(field_name='title', lookup_expr='contains')

    class Meta:
        model = SchoolNews
        fields = ('school', 'content')


class GalleryFilter(django_filters.rest_framework.FilterSet):
    content = django_filters.CharFilter(field_name='name', lookup_expr='contains')
    school = django_filters.CharFilter(field_name='clazz__school__name', lookup_expr='contains')

    class Meta:
        model = Gallery
        fields = ('content', 'clazz__board__board_id', 'school')


class HonorFilter(django_filters.rest_framework.FilterSet):
    content = django_filters.CharFilter(field_name='title', lookup_expr='contains')
    school = django_filters.CharFilter(field_name='clazz__school__name', lookup_expr='contains')

    class Meta:
        model = Honor
        fields = ('clazz__board__board_id', 'content', 'school')


class NotificationFilter(django_filters.rest_framework.FilterSet):
    school = django_filters.CharFilter(method='filter_school')
    content = django_filters.CharFilter(method='filter_content')

    def filter_school(self, queryset, name, value):
        return queryset.filter(Q(clazz__school__name__contains=value) | Q(school__name__contains=value))

    def filter_content(self, queryset, name, value):
        return queryset.filter(Q(content__contains=value) | Q(title__contains=value))

    class Meta:
        model = Notification
        fields = ('clazz__board__board_id', 'content', 'school')


class LessonHistoryAttFilter(django_filters.rest_framework.FilterSet):
    content = django_filters.CharFilter(method='filter_content')

    def filter_content(self, queryset, name, value):
        return queryset.filter(Q(clazz__school__name__contains=value) | Q(clazz__canonical_name__contains=value))

    class Meta:
        model = LessonAttendanceHistory
        fields = ('date', 'content')
