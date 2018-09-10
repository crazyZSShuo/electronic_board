# coding=utf-8
import binascii
import os
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models, connection
from django.utils.timezone import now

from common.utils import get_unique_id


def user_avatar_path(instance, filename):
    return 'user/avatar/{0}{1}'.format(binascii.hexlify(os.urandom(20)).decode(), os.path.splitext(filename)[1])


GENDER_CHOICE = (
    ('M', '男'),
    ('F', '女')
)

USER_TYPE = (
    ('SU', '系统管理员'),
    ('T', '教师'),
    ('SA', '学校管理员'),
    ('VA','学校副管理员'),
    ('EA','电子班牌管理员'),
    ('EB','电子班牌'),
)


class UserProfileManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, mobile, password, **extra_fields):
        if not mobile:
            raise ValueError('The given mobile must be set')
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, mobile, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(mobile, password, **extra_fields)

    def create_superuser(self, mobile, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(mobile, password, **extra_fields)


class UserProfile(AbstractUser):
    """
    用户
    """
    user_id = models.CharField(default=get_unique_id, max_length=16, unique=True, editable=False, verbose_name='ID')
    username = models.CharField(max_length=24, default=get_unique_id, blank=True)
    mobile = models.CharField(max_length=24, unique=True, verbose_name='手机号码/班牌MAC')
    name = models.CharField(max_length=32, null=True, verbose_name='姓名')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE, verbose_name='性别')
    birthday = models.DateField(null=True, blank=True, verbose_name='出生年月')
    user_type = models.CharField(max_length=32, default='T', verbose_name='类别')
    avatar = models.ImageField(default='user/avatar/default_avatar.png',
                               max_length=128, upload_to=user_avatar_path, verbose_name='头像')
    objects = UserProfileManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    __original_avatar = None

    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)
        self.__original_avatar = self.avatar

    def save(self, *args, **kwargs):
        super(UserProfile, self).save(*args, **kwargs)
        self.__original_avatar = self.avatar

    @property
    def is_system_admin(self):
        return 'SU' in self.user_type

    @property
    def is_teacher(self):
        return 'T' in self.user_type

    @property
    def is_school_admin(self):
        return 'SA' in self.user_type

    @property
    def is_school_vic_admin(self):
        return 'VA' in self.user_type

    @property
    def is_electronicboard_admin(self):
        return 'EA' in self.user_type

    @property
    def is_electronicboard(self):
        return 'EB' in self.user_type

    def __str__(self):
        return '{}-{}'.format(self.name,self.mobile)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class Teacher(UserProfile):
    teacher_id = models.CharField(default=get_unique_id, max_length=16, unique=True, editable=False, verbose_name='ID')
    desc = models.CharField(max_length=128, verbose_name='简述', null=True, blank=True)
    school = models.ForeignKey(to='school.School', related_name='teachers', on_delete=models.CASCADE, null=True,
                               blank=True, verbose_name='学校')
    teacher_roles = models.CharField(max_length=128, verbose_name='任教科目')
    age = models.IntegerField(default=0,verbose_name='年龄')
    work_years = models.IntegerField(default=0, verbose_name='从教工龄')
    graduate_school = models.CharField(max_length=32, verbose_name='毕业院校')
    achievement = models.TextField(blank=True, null=True, max_length=256, verbose_name='主要成就')
    introduce = models.TextField(verbose_name='个人介绍')

    created_time = models.DateTimeField(default=now, verbose_name='上传时间')

    def __str__(self):
        return '{}-{}'.format(self.school.name,self.name)

    class Meta:
        verbose_name = '教师'
        verbose_name_plural = verbose_name


class Board(UserProfile):
    board_id = models.CharField(default=get_unique_id, max_length=16, unique=True, editable=False, verbose_name='ID')
    install_addr = models.CharField(max_length=32, verbose_name='电子班牌安装位置')
    work_start_time = models.TimeField(default='', verbose_name='电子班牌开始显示时间')
    work_end_time = models.TimeField(default='', verbose_name='电子班牌结束显示时间')
    work_days = models.CharField(max_length=16, verbose_name='班牌工作周期')
    teachers = models.ManyToManyField(to=Teacher, related_name="boards", verbose_name="电子班牌管理员")

    @property
    def board_time(self):
        return '{}-{}'.format(self.work_start_time,self.work_end_time)

    def __str__(self):
        return self.mobile

    def save(self, *args, **kwargs):
        self.user_type = 'EB'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '班牌'
        verbose_name_plural = verbose_name


class Student(models.Model):
    student_id = models.CharField(default=get_unique_id, max_length=16, unique=True, verbose_name='ID')
    clazz = models.ForeignKey(to='school.Class',on_delete=models.CASCADE, related_name='students', null=True, blank=True, verbose_name='班级')
    name = models.CharField(max_length=32, verbose_name='姓名')
    card_num = models.CharField(max_length=64, verbose_name='13.56M卡号')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '学生'
        verbose_name_plural = verbose_name


class AuthToken(models.Model):
    key = models.CharField(max_length=40, verbose_name='KEY')
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name="User"
    )
    created = models.DateTimeField(auto_now_add=True)
    expire = models.DateTimeField(verbose_name='过期时间')

    class Meta:
        verbose_name = "Token"
        verbose_name_plural = "Tokens"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
            self.expire = now() + timedelta(days=2)
        return super(AuthToken, self).save(*args, **kwargs)

    def refresh_key(self):
        self.key = self.generate_key()
        self.expire = now() + timedelta(days=2)
        self.save()

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.user.__str__()
