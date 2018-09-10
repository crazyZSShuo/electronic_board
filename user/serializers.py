# coding=utf-8
from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers, exceptions

from school.models import Class, School, TeacherClassRelation
from user.models import Student, Teacher, Board, UserProfile

class BoardTokenSerializer(serializers.Serializer):
    uuid = serializers.CharField()

    def validate(self, attrs):
        uuid = attrs.get('uuid')
        try:
            board = Board.objects.get(mobile=uuid)
            if not board.is_active:
                msg = 'User account is disabled.'
                raise serializers.ValidationError(msg, code='authorization')
            attrs['user'] = board
        except Board.DoesNotExist:
            msg = 'Unable to log in with provided credentials.'
            raise serializers.ValidationError(msg, code='authorization')
        return attrs


class WebAuthSerializer(serializers.Serializer):
    mobile = serializers.CharField(label="Mobile")
    password = serializers.CharField(label="Password", style={'input_type': 'password'})

    def validate(self, attrs):
        mobile = attrs.get('mobile')
        password = attrs.get('password')

        if mobile and password:
            user = authenticate(username=mobile, password=password)

            if user:

                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise serializers.ValidationError(msg, code='authorization')
            else:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    nick_name = serializers.CharField(source='name')

    class Meta:
        model = UserProfile
        fields = ('nick_name', 'user_type', 'avatar')


class BoardListSerializer(serializers.ModelSerializer):
    MAC = serializers.CharField(source='mobile')
    clazz_name = serializers.CharField(source='board.clazz.canonical_name')
    school_name = serializers.CharField(source='board.clazz.school.name')
    province = serializers.CharField(source='board.clazz.school.province')
    city = serializers.CharField(source='board.clazz.school.city')
    district = serializers.CharField(source='board.clazz.school.district')

    class Meta:
        model = Board
        fields = ('board_id', 'province', 'city', 'district', 'school_name', 'install_addr', 'clazz_name', 'MAC', 'board_time')


class BoardDetailSerializer(serializers.ModelSerializer):
    MAC = serializers.CharField(source='mobile')
    clazz_name = serializers.CharField(source='board.clazz.canonical_name')
    school_name = serializers.CharField(source='board.clazz.school.name')
    province = serializers.CharField(source='board.clazz.school.province')
    city = serializers.CharField(source='board.clazz.school.city')
    district = serializers.CharField(source='board.clazz.school.district')
    school = serializers.CharField(source='clazz.school.school_id')
    teachers = serializers.SlugRelatedField(slug_field='teacher_id', queryset=Teacher.objects.all(), many=True)

    grade_index = serializers.IntegerField(source='clazz.grade_index')
    index_of_grade = serializers.IntegerField(source='clazz.index_of_grade')

    class Meta:
        model = Board
        fields = ('province', 'city', 'district', 'school', 'school_name', 'install_addr', 'clazz_name',
                  'MAC', 'work_start_time', 'grade_index', 'index_of_grade', 'work_days', 'work_end_time', 'board_time',
                  'teachers')


class BoardCreateSerializer(serializers.ModelSerializer):
    MAC = serializers.CharField(source='mobile')
    school = serializers.SlugRelatedField(slug_field='school_id', queryset=School.objects.all(), write_only=True)
    teachers = serializers.SlugRelatedField(slug_field='teacher_id', queryset=Teacher.objects.all(), many=True)
    grade_index = serializers.IntegerField(write_only=True)
    index_of_grade = serializers.IntegerField(write_only=True)

    def validate(self, attrs):
        mobile = attrs['mobile']
        if Board.objects.filter(mobile=mobile).count() != 0:
            raise exceptions.ValidationError("MAC地址已存在")
        if Class.objects.filter(
            school=attrs['school'],
            index_of_grade=attrs['index_of_grade'],
            grade_index=attrs['grade_index']).count() != 0:
            raise exceptions.ValidationError("该班级已存在班牌")
        return super().validate(attrs)

    @transaction.atomic()
    def create(self, validated_data):
        school = validated_data.pop('school')
        grade_index = validated_data.pop('grade_index')
        index_of_grade = validated_data.pop('index_of_grade')
        board = super().create(validated_data)
        Class.objects.create(
            board=board,
            school=school,
            index_of_grade=index_of_grade,
            grade_index=grade_index
        )
        return board

    class Meta:
        model = Board
        fields = ('school', 'install_addr', 'grade_index', 'index_of_grade', 'MAC', 'work_start_time',
                  'work_days', 'work_end_time', 'teachers')


class BoardUpdateSerializer(serializers.ModelSerializer):
    teachers = serializers.SlugRelatedField(slug_field='teacher_id', queryset=Teacher.objects.all(), many=True)

    class Meta:
        model = Board
        fields = ('teachers', 'install_addr', 'work_start_time', 'work_end_time', 'work_days')


class TeacherSerializer(serializers.ModelSerializer):
    school_province = serializers.CharField(read_only=True, source='school.province')
    school_city = serializers.CharField(read_only=True, source='school.city')
    school_district = serializers.CharField(read_only=True, source='school.district')
    school_name = serializers.CharField(read_only=True, source='school.name')

    class Meta:
        model = Teacher
        fields = ('teacher_id', 'school_province', 'school_city', 'school_district', 'school_name', 'name',
                  'mobile')


class TeacherCreateSerializer(serializers.ModelSerializer):
    school = serializers.SlugRelatedField(slug_field='school_id',queryset=School.objects.all())
    classes = serializers.SlugRelatedField(slug_field='class_id',queryset=Class.objects.all(),many=True)

    def validate(self, attrs):
        mobile = attrs['mobile']
        if Teacher.objects.filter(mobile=mobile).count() != 0:
            raise exceptions.ValidationError("手机号已存在")

        return super().validate(attrs)

    @transaction.atomic()
    def create(self, validated_data):
        classes = validated_data.pop('classes')
        teacher = super().create(validated_data)
        all_relations = []
        for cls in classes:
            all_relations.append(TeacherClassRelation(**{
                'teacher': teacher,
                'clazz': cls
            }))
        TeacherClassRelation.objects.bulk_create(all_relations)
        return teacher

    class Meta:
        model = Teacher
        fields = ('school', 'name', 'mobile', 'teacher_roles', 'birthday', 'work_years', 'graduate_school',
                  'achievement', 'introduce', 'avatar', 'classes')


class TeacherUpdateSerializer(serializers.ModelSerializer):
    classes = serializers.SlugRelatedField(slug_field='class_id', queryset=Class.objects.all(), many=True)

    @transaction.atomic()
    def update(self, instance, validated_data):
        classes = validated_data.pop('classes')
        instance = super().update(instance, validated_data)

        TeacherClassRelation.objects.filter(teacher=instance).delete()
        all_relations = []
        for cls in classes:
            all_relations.append(TeacherClassRelation(**{
                'teacher': instance,
                'clazz': cls
            }))
        TeacherClassRelation.objects.bulk_create(all_relations)
        return instance

    class Meta:
        model = Teacher
        fields = ('name', 'teacher_roles', 'birthday', 'work_years', 'graduate_school', 'achievement',
                  'introduce', 'avatar', 'classes')


class TeacherRetrieveSerializer(serializers.ModelSerializer):
    school = serializers.CharField(source='school.school_id')
    classes = serializers.SlugRelatedField(slug_field='class_id',queryset=Class.objects.all(),many=True)

    class Meta:
        model = Teacher
        fields = ('school', 'name', 'mobile', 'teacher_roles', 'birthday', 'work_years', 'graduate_school',
                  'achievement', 'introduce', 'avatar', 'classes')


class TinyTeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Teacher
        fields = ('teacher_id', 'name')


class StudentSerializer(serializers.ModelSerializer):
    clazz = serializers.CharField(source='clazz.canonical_name')
    class_id = serializers.CharField(source='clazz.class_id')
    school_province = serializers.CharField(source='clazz.school.province')
    school_city = serializers.CharField(source='clazz.school.city')
    school_district = serializers.CharField(source='clazz.school.district')
    school_name = serializers.CharField(source='clazz.school.name')

    class Meta:
        model = Student
        fields = ('student_id', 'clazz', 'class_id', 'school_province', 'school_city', 'school_district', 'school_name',
                  'name', 'card_num')


class StudentCreateSerializer(serializers.ModelSerializer):
    clazz = serializers.SlugRelatedField(slug_field='class_id', queryset=Class.objects.all())

    class Meta:
        model = Student
        fields = ('clazz','name','card_num')


class StudentUpdateSerializer(serializers.ModelSerializer):
    clazz = serializers.SlugRelatedField(slug_field='class_id',queryset=Class.objects.all())

    class Meta:
        model = Student
        fields = ('clazz', 'name', 'card_num')

