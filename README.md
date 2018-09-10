# 班牌

#### 项目介绍
{**后台班牌管理**
模型：
用户、班牌、学校

权限(permissions.py)：
系统管理员
学校管理员
学校副管理员
老师
班牌管理员
班牌

搜索与过滤(filters.py)：
根据地区、学校名字、班级名字、班牌ID、学生ID、学校ID、老师名字、日期等进行搜索与过滤
search_fields
filter_fields
filterset_class
}

####系统构成
django rest framework 系统实现前台功能
django自带admin后台管理系统

####Django Rest Framework 技能

1.通用view实现 rest api接口
apiview方式实现api
genericView方式实现api接口
Viewset和router方式实现api接口和url配置
Django_filter searchFilter OrderFilter 分页
通用mixin

2.权限和认证；
Authentication用户认证设置
动态设置permission、authentication
Validators实现字段验证

3.序列化和表单验证
Serializer
ModelSerializer
动态设置Serializer

#### 环境搭建
所需环境：
certifi==2018.8.13
chardet==3.0.4
coreapi==2.3.3
coreschema==0.0.4
Django==2.0
django-ckeditor==5.6.1
django-cors-headers==2.4.0
django-filter==2.0.0
django-filters==0.2.1
django-js-asset==1.1.0
djangorestframework==3.8.2
idna==2.7
itypes==1.1.0
Jinja2==2.10
MarkupSafe==1.0
openapi-codec==1.3.2
Pillow==5.2.0
pytz==2018.5
requests==2.19.1
uritemplate==3.0.0
urllib3==1.23
xlrd==1.1.0

#### 使用说明
1.push文件到本地
2.安装所需环境
3.本地运行migrate
4.运行manage.py runserver
