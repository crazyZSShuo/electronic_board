from django.db import models
from django.utils.timezone import now
from django.contrib.auth.admin import User

from common.utils import get_unique_id
from ckeditor_uploader.fields import RichTextUploadingField

from school.models import School, Class
from user.models import Student, Teacher, UserProfile


class Gallery(models.Model):
    """班级相册"""
    gallery_id = models.CharField(default=get_unique_id, max_length=16, unique=True, verbose_name='ID')
    clazz = models.ForeignKey(to=Class, on_delete=models.CASCADE, verbose_name='班级')
    name = models.CharField(max_length=32, verbose_name='相册名称')
    is_show = models.BooleanField(default=True, verbose_name='电子班牌是否显示')
    teacher = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE, verbose_name='上传者')
    created_time = models.DateTimeField(default=now, verbose_name='上传时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '班级相册'
        verbose_name_plural = verbose_name


class GalleryImageItem(models.Model):
    """相册照片"""
    item_id = models.CharField(default=get_unique_id, max_length=16, unique=True, verbose_name='ID')
    gallery = models.ForeignKey(to=Gallery, related_name='images', on_delete=models.CASCADE, verbose_name='相册')
    image = models.ImageField(verbose_name='图片')
    created_time = models.DateTimeField(default=now, verbose_name='上传时间')

    class Meta:
        verbose_name = '相册照片'
        verbose_name_plural = verbose_name


class Honor(models.Model):
    """班级荣誉"""
    honor_id = models.CharField(default=get_unique_id, max_length=16, unique=True, verbose_name='ID')
    clazz = models.ForeignKey(to=Class, on_delete=models.CASCADE, verbose_name='班级')
    title = models.CharField(max_length=128, unique=True, verbose_name='荣誉主题')
    get_time = models.DateField(verbose_name='荣誉获得时间')
    desc = models.TextField(verbose_name='荣誉描述')
    teacher = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE, verbose_name='上传者')
    created_time = models.DateTimeField(default=now, verbose_name='上传时间')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '班级荣誉'
        verbose_name_plural = verbose_name


class HonorImageItem(models.Model):
    """荣誉照片"""
    item_id = models.CharField(default=get_unique_id, max_length=16, unique=True, verbose_name='ID')
    honor = models.ForeignKey(to=Honor, related_name='images', on_delete=models.CASCADE, verbose_name='荣誉')
    image = models.ImageField(verbose_name='图片')
    is_show = models.BooleanField(default=False, verbose_name='是否展示')
    created_time = models.DateTimeField(default=now, verbose_name='上传时间')

    class Meta:
        verbose_name = '荣誉照片'
        verbose_name_plural = verbose_name


class Notification(models.Model):
    """通知"""
    INFO_TYPE = (
        ('class', '班级'),
        ('school', '学校'),
    )
    notification_id = models.CharField(default=get_unique_id, max_length=16, unique=True, verbose_name='ID')
    school = models.ForeignKey(to=School, on_delete=models.CASCADE, null=True, blank=True, verbose_name='学校')
    clazz = models.ForeignKey(to=Class, on_delete=models.CASCADE, null=True, blank=True, verbose_name='班级')
    type = models.CharField(choices=INFO_TYPE, default='class', max_length=16, verbose_name='通知类型')
    title = models.CharField(max_length=64, verbose_name='主题')
    image = models.ImageField(null=True, blank=True, verbose_name='上传图片')
    content = models.TextField(verbose_name='内容')
    is_show = models.BooleanField(default=False, verbose_name='是否展示')
    teacher = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE, verbose_name='发布人')
    created_time = models.DateTimeField(default=now, verbose_name='上传时间')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '通知'
        verbose_name_plural = verbose_name


class SchoolNews(models.Model):
    """学校新闻"""
    news_id = models.CharField(default=get_unique_id, max_length=16, unique=True, verbose_name='ID')
    school = models.ForeignKey(to=School, related_name='newses', on_delete=models.CASCADE, verbose_name='学校')
    content = models.TextField(default='', verbose_name='内容')
    title = models.CharField(max_length=128, unique=True, verbose_name='新闻标题')
    rich_content = RichTextUploadingField(null=True, blank=True, verbose_name='富文本内容')
    teacher = models.ForeignKey(to=UserProfile, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='发布人')
    created_time = models.DateTimeField(default=now, verbose_name='时间')
    is_show = models.BooleanField(default=False, verbose_name='是否展示')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '新闻'
        verbose_name_plural = verbose_name


class Lesson(models.Model):
    """课程"""
    lesson_id = models.CharField(default=get_unique_id, max_length=16, unique=True, verbose_name='ID')
    clazz = models.ForeignKey(to=Class, verbose_name='班级', on_delete=models.CASCADE)
    teacher = models.ForeignKey(to=Teacher, on_delete=models.CASCADE, verbose_name='任课老师')
    name = models.CharField(max_length=16, default='', verbose_name='课程名称')
    is_attendance = models.BooleanField(default=False, verbose_name='是否走班考勤')
    day_of_week = models.IntegerField(default=1, verbose_name='周')
    index_of_day = models.IntegerField(default=1, verbose_name='节')
    start = models.TimeField(verbose_name='开始时间')
    end = models.TimeField(verbose_name='结束时间')
    created_time = models.DateTimeField(default=now, verbose_name='添加时间')
    students = models.ManyToManyField(to=Student, through='StudentLessonRel', verbose_name='学生')

    def __str__(self):
        return '{}-{}-{}-{}'.format(self.teacher.name, self.name, self.day_of_week, self.index_of_day)

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = verbose_name


class StudentLessonRel(models.Model):
    """走班学生表"""
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE, verbose_name='学生')
    lesson = models.ForeignKey(to=Lesson, on_delete=models.CASCADE, verbose_name='课程')

    class Meta:
        verbose_name = '学生课程关系'
        verbose_name_plural = verbose_name


class LessonAttendanceHistory(models.Model):
    """走班课程历史"""
    attendance_lesson_history_id = models.CharField(default=get_unique_id, max_length=16, unique=True,
                                                    verbose_name='ID')
    lesson = models.ForeignKey(to=Lesson, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='课程')
    clazz = models.ForeignKey(to=Class, on_delete=models.CASCADE, verbose_name='班级')
    teacher = models.ForeignKey(to=Teacher, blank=True, null=True, verbose_name='任课老师', on_delete=models.CASCADE)
    name = models.CharField(max_length=16, verbose_name='课程名称')
    day_of_week = models.IntegerField(default=1, verbose_name='周')
    index_of_day = models.IntegerField(default=1, verbose_name='节')
    start = models.TimeField(verbose_name='开始时间')
    end = models.TimeField(verbose_name='结束时间')
    date = models.DateField(verbose_name='走班日期')
    should_attendance_count = models.IntegerField(verbose_name='应到人数')
    actual_attendance_number = models.IntegerField(verbose_name='实到人数')

    class Meta:
        verbose_name = '走班课程'
        verbose_name_plural = verbose_name


class LessonAttendanceStudent(models.Model):
    """走班课程历史考勤"""
    history = models.ForeignKey(to=LessonAttendanceHistory, related_name='items', on_delete=models.CASCADE,
                                verbose_name='课程历史')
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE, verbose_name='学生')
    attendance_time = models.DateTimeField(blank=True, null=True, verbose_name='签到时间')

    class Meta:
        verbose_name = '走班考勤'
        verbose_name_plural = verbose_name
