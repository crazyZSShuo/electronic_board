from rest_framework import serializers, exceptions
from django.db import transaction
from school.models import School, Class
from user.models import Teacher, UserProfile, Board


class CascaderClassItemSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='canonical_name')
    value = serializers.CharField(source='class_id')

    class Meta:
        model = Class
        fields = ('label', 'value')


class CascaderBoardItemSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='board.install_addr')
    value = serializers.CharField(source='board.board_id')

    class Meta:
        model = Board
        fields = ('label', 'value')


class CascaderSchoolSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='name')
    value = serializers.CharField(source='school_id')

    class Meta:
        model = School
        fields = ('province', 'city', 'district', 'label', 'value')


class CascaderClassSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='name')
    value = serializers.CharField(source='school_id')
    children = CascaderClassItemSerializer(many=True, source='classes')

    class Meta:
        model = School
        fields = ('province', 'city', 'district', 'label', 'value', 'children')


class CascaderBoardSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='name')
    value = serializers.CharField(source='school_id')
    children = CascaderBoardItemSerializer(many=True, source='classes')

    class Meta:
        model = School
        fields = ('province', 'city', 'district', 'label', 'value', 'children')


class TinySchoolSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return '{}/{}/{}-{}'.format(obj.province, obj.city, obj.district, obj.name)

    class Meta:
        model = School
        fields = ('school_id', 'name')


class SchoolSerializer(serializers.ModelSerializer):
    board_num = serializers.SerializerMethodField()
    normal_num = serializers.SerializerMethodField()
    abnormal_num = serializers.SerializerMethodField()
    admin_mobile = serializers.CharField(write_only=True, max_length=11)
    admin_password = serializers.CharField(write_only=True)

    def get_board_num(self,obj):
        return obj.classes.count()

    def get_normal_num(self,obj):
        return "10"

    def get_abnormal_num(self,obj):
        return "1"

    def validate(self, attrs):
        if UserProfile.objects.exclude(user_type__contains='T').filter(mobile=attrs['admin_mobile']).count() != 0:
            raise exceptions.ValidationError("用户已存在")
        return super().validate(attrs)

    @transaction.atomic()
    def create(self, validated_data):
        admin_mobile = validated_data.pop('admin_mobile')
        admin_password = validated_data.pop('admin_password')
        school = super().create(validated_data)
        teacher, created = Teacher.objects.update_or_create(
            defaults={
                'user_type': 'T,SA',
                'school': school,
            },
            mobile=admin_mobile,
        )
        teacher.set_password(admin_password)
        teacher.save()
        return school


    class Meta:
        model = School
        fields = (
            'school_id', 'name', 'province', 'city', 'district', 'board_num','normal_num',\
            'abnormal_num','admin_mobile','admin_password')
        read_only_fields = ('school_id', 'board_num','normal_num', 'abnormal_num',)


class SchoolUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = School
        fields = ('name', 'province', 'city', 'district')


class ClassSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='canonical_name')
    school = SchoolSerializer()

    class Meta:
        model = Class
        fields = (
            'class_id', 'name',  'school')
        read_only_fields = (
            'class_id', 'name',  'school')


class TinyClassSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='canonical_name')

    class Meta:
        model = Class
        fields = ('class_id', 'name')
