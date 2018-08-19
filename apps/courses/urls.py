# coding=utf-8
_author_ = 'Yasin'
_date_ = '2018-04-15 17:26'
from django.conf.urls import url, include
from .views import CourseListView, CourseDetailView, CourseInfoView, CommentsView, AddCommentsView, VideoPlayView


urlpatterns = [
    url(r'^list/$', CourseListView.as_view(), name="course_list"),  # 课程机构首页
    url(r'^detail/(?P<course_id>\d+)/$', CourseDetailView.as_view(), name="course_detail"),  # 课程详情页
    url(r'^info/(?P<course_id>\d+)/$', CourseInfoView.as_view(), name="course_info"),  # 课程
    url(r'^comment/(?P<course_id>\d+)/$', CommentsView.as_view(), name="course_comments"),  # 课程评论
    url(r'^add_comment/$', AddCommentsView.as_view(), name="add_comment"),  # 添加课程评论
    url(r'^video/(?P<video_id>\d+)/$', VideoPlayView.as_view(), name="video_play"),  # 课程详情页


]

