import django_filters
from django.db.models import Q

from school.models import School



class SchoolFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.CharFilter(lookup_expr='contains')


    class Meta:
        model = School
        fields = ('name', )




