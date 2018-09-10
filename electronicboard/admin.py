from django.contrib import admin

# Register your models here.
from electronicboard.models import Gallery, GalleryImageItem, Notification, Honor, SchoolNews, Lesson, \
    HonorImageItem,StudentLessonRel, LessonAttendanceHistory, LessonAttendanceStudent


class GalleryImageItemAdmin(admin.ModelAdmin):
    list_display = ('image', 'created_time',)


class GalleryAdmin(admin.ModelAdmin):
    list_display = ('clazz', 'name', 'teacher', 'is_show', 'created_time',)


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('school', 'type', 'title', 'image', 'content', 'teacher', 'created_time',)


class HonorAdmin(admin.ModelAdmin):
    list_display = ('honor_id', 'clazz', 'title', 'get_time', 'desc', 'teacher', 'created_time',)


class SchoolNewsAdmin(admin.ModelAdmin):
    list_display = ('school', 'title', 'content','teacher', 'created_time',)


class LessonAdmin(admin.ModelAdmin):
    list_display = ('clazz', 'teacher', 'name', 'day_of_week', 'index_of_day', 'start', 'end', 'created_time',)



admin.site.register(GalleryImageItem)
admin.site.register(Gallery, GalleryAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Honor, HonorAdmin)
admin.site.register(HonorImageItem)
admin.site.register(SchoolNews, SchoolNewsAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(StudentLessonRel)
admin.site.register(LessonAttendanceHistory)
admin.site.register(LessonAttendanceStudent)
