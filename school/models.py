# coding=utf-8
from django.db import models
from common.utils import cnum, get_unique_id
from user.models import Teacher, Student, Board


class School(models.Model):
    school_id = models.CharField(default=get_unique_id, max_length=16, unique=True, editable=False, verbose_name='ID')
    province = models.CharField(max_length=32, default="", verbose_name='省份')
    city = models.CharField(max_length=32, verbose_name='城市')
    district = models.CharField(max_length=32, verbose_name='行政区')
    name = models.CharField(max_length=64, verbose_name='名称')
    desc = models.TextField(verbose_name='简介', null=True, blank=True)

    create = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '学校'
        verbose_name_plural = verbose_name


class TeacherClassRelation(models.Model):
    teacher = models.ForeignKey(to='user.Teacher', on_delete=models.CASCADE, related_name='class_relations',
                                verbose_name='教师')
    clazz = models.ForeignKey(to='Class', on_delete=models.CASCADE, related_name='teacher_relations', verbose_name='班级')

    def __str__(self):
        return '{}/{}'.format(self.teacher.name, self.clazz.canonical_name)

    class Meta:
        verbose_name = '教师班级关系'
        verbose_name_plural = verbose_name
        db_table = 'school_teacher_class_relation'
        unique_together = ('teacher', 'clazz')


class Class(models.Model):
    class_id = models.CharField(default=get_unique_id, max_length=16, unique=True, editable=False, verbose_name='ID')
    school = models.ForeignKey(to=School, on_delete=models.CASCADE, related_name='classes', null=True,
                               verbose_name='学校')
    board = models.OneToOneField(to=Board, on_delete=models.CASCADE, related_name="clazz", verbose_name='班牌')
    teachers = models.ManyToManyField(to='user.Teacher', through=TeacherClassRelation, related_name='classes',
                                      verbose_name='教师')
    index_of_grade = models.IntegerField(default=1, verbose_name='班级序号')
    grade_index = models.IntegerField(default=1, verbose_name='年级序号')

    create = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    @property
    def canonical_name(self):
        return '%s年级%s班' % (cnum(self.grade_index), cnum(self.index_of_grade))

    def __str__(self):
        return '{}/{}'.format(self.canonical_name, self.school)

    class Meta:
        verbose_name = '班级'
        verbose_name_plural = verbose_name


def pre_delete_class(sender, instance, using, **kwargs):
    if hasattr(instance, 'board'):
        instance.board.delete()


models.signals.post_delete.connect(pre_delete_class, sender=Class)