# coding=utf-8

from django.conf.urls import url
from rest_framework import routers

from .views import StudentView, WebLoginView, TeacherViewSet, WebLogoutView, BoardView, BoardIndexViewSet, \
    UserProfileView

router = routers.SimpleRouter()
router.register(r'teacher', TeacherViewSet, base_name='teacher')
router.register(r'student', StudentView, base_name="student")
router.register(r'board', BoardIndexViewSet, base_name="board")

urlpatterns = [
    url(r'^user/board_login/',BoardView.as_view(),name='board_login'),
    url(r'^user/web_login/$', WebLoginView.as_view(), name='web_login'),
    url(r'^user/web_logout/$', WebLogoutView.as_view(), name='web_logout'),
    url(r'^user/profile/$', UserProfileView.as_view(), name='profile'),
]

urlpatterns += router.urls
