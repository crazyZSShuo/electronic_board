import django_filters
from user.models import Board, Teacher, Student
from django.db.models import Q


class BoardFilter(django_filters.rest_framework.FilterSet):
    info = django_filters.CharFilter(method='filter_info')
    school = django_filters.CharFilter(field_name='clazz__school__name', lookup_expr='contains')

    def filter_info(self, queryset, name, value):
        return queryset.filter(Q(install_addr__contains=value)
                             | Q(clazz__index_of_grade__contains=value)
                             | Q(mobile__contains=value )
                             )

    class Meta:
        model = Board
        fields = ('school', 'info',)


class TeacherFilter(django_filters.rest_framework.FilterSet):
    info = django_filters.CharFilter(method='filter_info')
    school = django_filters.CharFilter(field_name='school__name', lookup_expr='contains')

    def filter_info(self, queryset, name, value):
        return queryset.filter(Q(name__contains=value) | Q(mobile__contains=value))

    class Meta:
        model = Teacher
        fields = ('school', 'info', 'school__school_id')


class StudentFilter(django_filters.rest_framework.FilterSet):
    school = django_filters.CharFilter(field_name='clazz__school__name', lookup_expr='contains')
    name = django_filters.CharFilter(field_name='name', lookup_expr='contains')

    class Meta:
        model = Student
        fields = ('school', 'name')



