from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from electronicboard import views
from electronicboard.views import ClassInfoAPIView, ClassIndexAPIView, SchoolNewsRichContentView

router = DefaultRouter()

router.register(r'electronic_board/class_course_table', views.LessonFormViewSet, base_name='class_course_table')
router.register(r'electronic_board/notification', views.ClassNotificationViewSet, base_name='notification')
router.register(r'electronic_board/gallery', views.ClassGalleryViewSet, base_name='gallery')
router.register(r'electronic_board/honor', views.ClassHonorViewSet, base_name='honor')
router.register(r'electronic_board/school_news', views.SchoolNewsViewSet, base_name='school_news')
router.register(r'electronic_board/teacher', views.TeacherViewSet, base_name="teacher")
router.register(r'gallery', views.GalleryViewSet, base_name='gallery')
router.register(r'honor', views.HonorViewSet, base_name='honor')
router.register(r'notification', views.NotificationViewSet, base_name='Notification')
router.register(r'news', views.NewsViewSet, base_name='News')
router.register(r'history', views.LessonHistoryAttViewSet, base_name='history')


router.register(r'gallery_image_item', views.GalleryImageItemViewSet, base_name='gallery_image_item')
router.register(r'honor_image_item', views.HonorImageItemViewSet, base_name='honor_image_item')


urlpatterns = [
    url(r'^electronic_board/class_info/$', ClassInfoAPIView.as_view(), name='electronic_board_class_info'),
    url(r'^electronic_board/index/$', ClassIndexAPIView.as_view(), name='electronic_board_index'),
    url(r'^electronic_board/rich_context/$', SchoolNewsRichContentView.as_view(), name='electronic_board_index'),

]

urlpatterns += router.urls
