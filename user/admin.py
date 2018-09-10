from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# Register your models here.

from .models import Teacher, UserProfile, Student, Board, AuthToken


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('school', 'name', 'mobile', 'avatar',)
    fields = ('teacher_id', 'school', 'name', 'gender', 'mobile', 'teacher_roles', \
              'birthday', 'work_years', 'graduate_school', 'achievement', 'introduce', \
              'avatar')
    readonly_fields = ('teacher_id',)


class BoardAdmin(admin.ModelAdmin):
    fields = ('mobile', 'install_addr', 'work_start_time', 'work_end_time', 'work_days', 'teachers')


class UserProfileAdmin(UserAdmin):
    list_display = ('mobile', 'name', 'gender', 'user_type', 'is_staff')
    fieldsets = (('ExtraInfo', {'fields': (
        'mobile', 'name', 'gender', 'avatar', 'user_type', 'birthday',
        )}),) + UserAdmin.fieldsets
    search_fields = ('username', 'first_name', 'last_name', 'email', 'name', 'mobile')


class StudentAdmin(admin.ModelAdmin):
    fields = ('student_id','name', 'clazz', 'card_num')
    readonly_fields = ('student_id',)
    list_display = ('clazz', 'name', 'card_num')
    search_fields = ('name',)


admin.site.register(Teacher, TeacherAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Board, BoardAdmin)
admin.site.register(AuthToken)
