# coding=utf-8
"""MxOline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView   # 通用 模版视图
import xadmin
from users.views import LoginView, RegisterView, ActiveUserView, ForgetPwdView, ResetView, ModifyPwdView, LogoutView, IndexView
from organization.views import OrgView
from django.views.static import serve
from MxOline.settings import MEDIA_ROOT, STATIC_ROOT

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url('^$', IndexView.as_view(), name='index'),
    url('^login/$', LoginView.as_view(), name='login'),  # 调用方法 返回句柄，第二个实参指定要调用的视图函数
    url('^logout/$', LogoutView.as_view(), name='logout'),
    url('^register/$', RegisterView.as_view(), name='register'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^active/(?P<active_code>.*)/$', ActiveUserView.as_view(), name="user_active"),
    url(r'^forget/$', ForgetPwdView.as_view(), name="forget_pwd"),
    url(r'^reset/(?P<active_code>.*)/$', ResetView.as_view(), name="reset_pwd"),
    url(r'^modify_pwd/$', ModifyPwdView.as_view(), name="modify_pwd"),
    # 课程机构url配置,分发
    url(r'^org/', include('organization.urls', namespace="org")),
    # 课程相关url配置,分发
    url(r'^course/', include('courses.urls', namespace="course")),

    url(r'^media/(?P<path>.*)/$', serve, {"document_root": MEDIA_ROOT}),     # 配置上传文件的访问处理函数
    # url(r'^static/(?P<path>.*)/$', serve, {"document_root": STATIC_ROOT}),
    # 课程相关url配置,分发
    url(r'^users/', include('users.urls', namespace="users")),
    url(r'^ueditor/',include('DjangoUeditor.urls' )),  # 富文本相关url
]

# 全局404 500页面配置
handler404 = 'users.views.page_not_found'
handler500 = 'users.views.page_error'
