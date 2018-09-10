"""board URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from school.urls import urlpatterns as school_urls
from user.urls import urlpatterns as user_urls
from electronicboard.urls import urlpatterns as electronicboard_urls
from common.views import SchemaView

api_patterns = [

    url(r'^$', SchemaView.as_view()),
]

api_patterns += user_urls
api_patterns += school_urls
api_patterns += electronicboard_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(api_patterns)),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
]
