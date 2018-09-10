from django.contrib import admin

from .models import School, Class, TeacherClassRelation


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('school_id', 'create', 'update')


class ClassAdmin(admin.ModelAdmin):
    list_display = ('class_id','school', 'canonical_name')
    # inlines = [TCRelationInline]
    # list_display = ('school','board_install_addr','canonical_name', 'board_mac_num','board_work_time')


class TeacherClassRelationAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'clazz')


admin.site.register(School, SchoolAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(TeacherClassRelation)
