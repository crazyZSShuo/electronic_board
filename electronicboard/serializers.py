from datetime import timedelta, datetime

from rest_framework import serializers, exceptions

from electronicboard.models import GalleryImageItem, Notification, Honor, SchoolNews, Lesson, \
    HonorImageItem, Gallery, LessonAttendanceHistory, LessonAttendanceStudent
from school.models import Class,School
from user.models import Student, Teacher,Board


class TeacherDetailSerializer(serializers.Serializer):
    teacher_id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    teacher_roles = serializers.CharField()
    age = serializers.IntegerField()
    work_years = serializers.IntegerField()
    graduate_school = serializers.CharField()
    achievement = serializers.CharField()
    introduce = serializers.CharField()
    avatar = serializers.ImageField()

    # school = serializers.CharField(source='school.name', read_only=True)
    # school_id = serializers.SlugRelatedField(source='school', slug_field='school_id', queryset=School.objects.all())

    def update(self, instance, validated_data):
        class_relations = validated_data.pop('class_relations')
        if class_relations:
            if instance.class_relations.all().count() > 0:
                instance.class_relations.all().delete()

        for attr, value in validated_data.items():
            if getattr(instance, attr) != value:
                setattr(instance, attr, value)
        instance.save()
        return instance

    def create(self, validated_data):
        try:
            class_relations = None
            if 'class_relations' in validated_data:
                class_relations = validated_data.pop('class_relations')
            instance = Teacher.objects.create(**validated_data)
            instance.set_password('123456')
            instance.save()
            return instance
        except TypeError as e:
            print(e)


class TeacherListSerializer(serializers.Serializer):
    teacher_id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    teacher_roles = serializers.CharField()
    age = serializers.IntegerField()
    work_years = serializers.IntegerField()
    # school = serializers.CharField(source='school.name', read_only=True)
    # school_id = serializers.SlugRelatedField(source='school', slug_field='school_id', queryset=School.objects.all())


class ClassInfoSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name')
    name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    bg = serializers.SerializerMethodField()
    city_number = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.canonical_name

    def get_address(self, obj):
        return obj.school.address

    def get_bg(self, obj):
        return ''

    def get_city_number(self, obj):
        return 'CN10121010'

    class Meta:
        model = Class
        fields = ('class_id', 'address', 'name', 'bg', 'city_number', 'school_name')


class LessonStudentSerializer(serializers.ModelSerializer):
    original_class = serializers.CharField(source='clazz.canonical_name_class')
    device_id = serializers.CharField(source='card_num')

    class Meta:
        model = Student
        fields = ('student_id', 'device_id', 'original_class', 'name')


class LessonSerializer(serializers.ModelSerializer):
    teacher = serializers.CharField(source='teacher.name')
    teacher_id = serializers.CharField(source='teacher.teacher_id')
    teacher_portrait = serializers.CharField(source='teacher.avatar')
    students = LessonStudentSerializer(many=True)  # 该课程下的所有学生
    start_attendance_time = serializers.SerializerMethodField()

    def get_start_attendance_time(self, obj):
        return (datetime.combine(datetime.now().date(), obj.start) - timedelta(minutes=10)).time()

    class Meta:
        model = Lesson
        fields = (
            'lesson_id', 'teacher_id', 'teacher_portrait', 'students', 'name', 'teacher', 'start', 'end', 'day_of_week', \
            'index_of_day', 'start_attendance_time', 'is_attendance')


class LessonAttendanceSerializer(serializers.Serializer):
    student = serializers.SlugRelatedField(slug_field='student_id', queryset=Student.objects.all())
    attendance = serializers.DateTimeField()


class HistoryAttendanceQuerySerializer(serializers.Serializer):
    date = serializers.DateField()


class LessonAttendanceHistoryItemSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name')
    student_original_class = serializers.CharField(source='student.clazz.new_canonical_name')

    # device = serializers.CharField(source='student.card_num')

    class Meta:
        model = LessonAttendanceStudent
        fields = ('student_name', 'student_original_class', 'attendance_time')


class ClassNotificationSerializer(serializers.ModelSerializer):
    from_name = serializers.CharField(source='teacher.name')

    class Meta:
        model = Notification
        fields = ('title', 'content', 'image', 'created_time', 'type', 'from_name')


class ClassGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'


class GalleryImageItemSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='gallery.name')

    class Meta:
        model = GalleryImageItem
        fields = ('image', 'title')


class ClassHonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Honor
        fields = ('honor_id', 'get_time', 'title',)


class HonorImageItemSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='honor.title')

    class Meta:
        model = HonorImageItem
        fields = ('image', 'title')


class ClassHonorDetailSerializer(serializers.ModelSerializer):
    images = HonorImageItemSerializer(many=True)

    class Meta:
        model = Honor
        fields = ('honor_id', 'get_time', 'title', 'images')


class SchoolNewsSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return 'http://{}/api/electronic_board/rich_context/?news_id={}'.format(self.context['request'].get_host(),
                                                                                obj.news_id)

    class Meta:
        model = SchoolNews
        fields = ('title', 'content', 'url', 'created_time')


class ClassIndexSerializer(serializers.Serializer):
    honor = ClassHonorSerializer()
    notification = ClassNotificationSerializer()
    news = SchoolNewsSerializer()


class GallerySerializer(serializers.ModelSerializer):
    school_province = serializers.CharField(source='clazz.school.province')
    school_city = serializers.CharField(source='clazz.school.city')
    school_district = serializers.CharField(source='clazz.school.district')
    school_name = serializers.CharField(source='clazz.school.name')
    clazz_name = serializers.CharField(source='clazz.canonical_name')

    class Meta:
        model = Gallery
        fields = ('gallery_id', 'school_province', 'school_name', 'school_city', 'school_district', 'clazz_name',
                  'name', 'created_time', 'is_show')


class GalleryImageItemCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    gallery = serializers.SlugRelatedField(slug_field='gallery_id', queryset=Gallery.objects.all())

    class Meta:
        model = GalleryImageItem
        fields = ('gallery', 'image', 'item_id')


class GalleryDetailSerializer(serializers.ModelSerializer):
    school_province = serializers.CharField(source='clazz.school.province')
    school_city = serializers.CharField(source='clazz.school.city')
    school_district = serializers.CharField(source='clazz.school.district')
    school_name = serializers.CharField(source='clazz.school.name')
    clazz_name = serializers.CharField(source='clazz.canonical_name')
    clazz = serializers.CharField(source='clazz.class_id')
    images = GalleryImageItemCreateSerializer(many=True)

    class Meta:
        model = Gallery
        fields = ('gallery_id', 'clazz', 'school_province', 'school_name', 'school_city', 'school_district',
                  'clazz_name', 'name', 'created_time', 'is_show', 'images')


class GalleryCreateSerializer(serializers.ModelSerializer):
    clazz = serializers.SlugRelatedField(slug_field='class_id',queryset=Class.objects.all())

    def validate(self, attrs):
        attrs['teacher'] = self.context['request'].user
        return attrs

    class Meta:
        model = Gallery
        fields = ('is_show', 'name', 'clazz')


class GalleryUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Gallery
        fields = ('name', 'is_show')


class HonorSerializer(serializers.ModelSerializer):
    school_province = serializers.CharField(source='clazz.school.province')
    school_city = serializers.CharField(source='clazz.school.city')
    school_district = serializers.CharField(source='clazz.school.district')
    school_name = serializers.CharField(source='clazz.school.name')
    clazz_name = serializers.CharField(source='clazz.canonical_name')

    class Meta:
        model = Honor
        fields = ('honor_id', 'school_name', 'school_province', 'school_city', 'school_district', 'clazz_name', 'get_time', 'title')


class HonorCreateSerializer(serializers.ModelSerializer):
    clazz = serializers.SlugRelatedField(slug_field='class_id',queryset=Class.objects.all())

    def validate(self, attrs):
        attrs['teacher'] = self.context['request'].user
        return attrs

    class Meta:
        model = Honor
        fields = ('get_time', 'desc', 'title', 'clazz',)


class HonorImageItemCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    honor = serializers.SlugRelatedField(slug_field='honor_id', queryset=Honor.objects.all())

    class Meta:
        model = HonorImageItem
        fields = ('image', 'honor', 'item_id')


class HonorDetailSerializer(serializers.ModelSerializer):
    school_province = serializers.CharField(source='clazz.school.province')
    school_city = serializers.CharField(source='clazz.school.city')
    school_district = serializers.CharField(source='clazz.school.district')
    school_name = serializers.CharField(source='clazz.school.name')
    clazz_name = serializers.CharField(source='clazz.canonical_name')
    clazz = serializers.CharField(source='clazz.class_id')
    images = HonorImageItemCreateSerializer(many=True)

    class Meta:
        model = Honor
        fields = ('honor_id', 'school_name', 'school_province', 'school_city', 'school_district', 'clazz_name',
                  'get_time', 'clazz', 'desc', 'title', 'images')


class NotificationSerializer(serializers.ModelSerializer):
    from_name = serializers.CharField(source='teacher.name')
    receiver = serializers.SerializerMethodField()
    school_province = serializers.SerializerMethodField()
    school_city = serializers.SerializerMethodField()
    school_district = serializers.SerializerMethodField()

    def get_receiver(self, obj):
        if obj.type == 'school':
            return obj.school.name
        elif obj.type == 'class':
            return '{}/{}'.format(obj.clazz.school.name, obj.clazz.canonical_name)

        return ''

    def get_school_province(self,obj):
        if obj.type == 'school':
            return obj.school.province
        if obj.type == 'class':
            return obj.clazz.school.province
        return ''

    def get_school_city(self,obj):
        if obj.type == 'school':
            return obj.school.city
        if obj.type == 'class':
            return obj.clazz.school.city
        return ''

    def get_school_district(self,obj):
        if obj.type == 'school':
            return obj.school.district
        if obj.type == 'class':
            return obj.clazz.school.district
        return ''

    class Meta:
        model = Notification
        fields = ('notification_id', 'school_province', 'school_city', 'school_district', 'title', 'content', 'created_time',\
                  'is_show', 'receiver', 'from_name')


class NotificationCreateSerializer(serializers.ModelSerializer):
    clazz = serializers.SlugRelatedField(required=False, slug_field='class_id', queryset=Class.objects.all(),
                                         write_only=True)
    school = serializers.SlugRelatedField(required=False, slug_field='school_id', queryset=School.objects.all(),
                                          write_only=True)

    def validate(self, attrs):  # 获取上传者方法
        attrs['teacher'] = self.context['request'].user

        if attrs['type'] != 'school' and attrs['type'] != 'class':
            raise exceptions.ValidationError('请填入正确的通知类型')

        if attrs['type'] == 'school':
            if 'school' in attrs.keys() and 'clazz' not in attrs.keys():
                return attrs
            raise exceptions.ValidationError("'school' 没有传入值")

        if attrs['type'] == 'class':
            if 'school' not in attrs.keys() and 'clazz' in attrs.keys():
                return attrs
            raise exceptions.ValidationError("'class' 没有传入值")

        return attrs

    class Meta:
        model = Notification
        fields = ('clazz', 'school', 'type', 'title', 'content', 'is_show',)


class NewsSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    teacher = serializers.CharField(source='teacher.name')
    school_province = serializers.CharField(source='school.province')
    school_city = serializers.CharField(source='school.city')
    school_district = serializers.CharField(source='school.district')
    school_name = serializers.CharField(source='school.name')

    def get_url(self, obj):
        return 'http://{}/api/electronic_board/rich_context/?news_id={}'.format(self.context['request'].get_host(),
                                                                                obj.news_id)

    class Meta:
        model = SchoolNews
        fields = ('news_id', 'school_province', 'school_city', 'school_district', 'school_name', 'title', 'teacher',\
                  'url', 'created_time', 'is_show')


class NewsCreateSerializer(serializers.ModelSerializer):
    school = serializers.SlugRelatedField(slug_field='school_id',queryset=School.objects.all(),write_only=True)

    def validate(self, attrs):
        attrs['teacher'] = self.context['request'].user
        return attrs

    class Meta:
        model = SchoolNews
        fields = ('school', 'title', 'content', 'rich_content', 'is_show')


class LessonHistorySerializer(serializers.ModelSerializer):
    school_province = serializers.CharField(source='clazz.school.province')
    school_city = serializers.CharField(source='clazz.school.city')
    school_district = serializers.CharField(source='clazz.school.district')
    school_name = serializers.CharField(source='clazz.school.name')
    class_name = serializers.CharField(source='clazz.canonical_name')

    class Meta:
        model = LessonAttendanceHistory
        fields = ('school_province', 'school_city', 'school_district', 'school_name', 'class_name', 'date', \
                  'day_of_week','name', 'should_attendance_count', 'actual_attendance_number')