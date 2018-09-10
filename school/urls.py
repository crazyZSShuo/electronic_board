# coding=utf-8
from rest_framework import routers
from school.views import ClassViewSet, SchoolViewSet

router = routers.SimpleRouter()
router.register('school', SchoolViewSet, 'school')
router.register('class', ClassViewSet, 'class')

urlpatterns = [
]


urlpatterns += router.urls
