# coding=utf-8
from django.shortcuts import render
from django.views.generic.base import View
from .models import Course, CourseResource, Video
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger  # 分页
from operation.models import UserFavorite, CourseComments, UserCourse
from django.http import HttpResponse
from utils.mixin_utils import LoginRequiredMixin
from django.db.models import Q
# Create your views here.


class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by("-add_time")
        hot_courses = Course.objects.all().order_by("-click_nums")[:3]
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            all_courses = all_courses.filter(Q(name__icontains=search_keywords)|Q(desc__icontains=search_keywords)|Q(detail__icontains=search_keywords))

        sort = request.GET.get('sort', "")      # 课程排序
        if sort:
            if sort == "student":
                all_courses = all_courses.order_by("-student")
            elif sort == "hot":
                all_courses = all_courses.order_by("-click_nums")

        try:                                # 对课程机构进行分页
            page = request.GET.get('page', 1)  # 取出page页面
        except PageNotAnInteger:
            page = 1
        # 为完成查询的字符串请求对象提供生成分页器。
        p = Paginator(all_courses, 6, request=request)     # 调用分页函数，将来自于HTML的课程机构进行每页五个的分页处理
        courses = p.page(page)    # 调用函数取到第几页的数据，返回给定基于页码的页面对象

        return render(request, 'course-list.html',{
            "all_courses": courses,   # 将变量返回给HTML页面
            "sort": sort,
            "hot_courses": hot_courses
            })


class CourseDetailView(View):  # 课程详情页
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1      # 增加课程点击数
        course.save()

        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated():  # 判断用户是否登录
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True

            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        tag = course.tag
        if tag:
            relate_courses = Course.objects.filter(tag=tag)[:1]
        else:
            relate_courses = []

        return render(request, "course-detail.html", {
            "course": course,
            "relate_courses": relate_courses,
            "has_fav_course": has_fav_course,
            "has_fav_org": has_fav_org
        })


class CourseInfoView(LoginRequiredMixin, View):  # 课程章节信息
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))                          # 获取该课程的信息
        course.student += 1
        course.save()
        user_courses = UserCourse.objects.filter(user=request.user, course=course)  # 查询用户是否已经关联了该课程
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)   # 添加该用户信息
            user_course.save()
        user_courses = UserCourse.objects.filter(course=course)                 # 取出学习该课程的用户
        user_ids = [user_course.user.id for user_course in user_courses]        # 列表推导，取出所有用户的ID
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)      # 取出所有用户的课程
        course_ids = [user_course.course.id for user_course in all_user_courses]    # 取出所有课程id
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]  # 取出该用户学过的其他所有课程
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, "course-video.html", {
            "course": course,
            "course_resources": all_resources,
            "relate_courses": relate_courses

        })


class CommentsView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        user_courses = UserCourse.objects.filter(user=request.user, course=course)  # 查询用户是否已经关联了该课程
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)  # 添加该用户信息
            user_course.save()
        user_courses = UserCourse.objects.filter(course=course)  # 取出学习该课程的用户
        user_ids = [user_course.user.id for user_course in user_courses]  # 列表推导，取出所有用户的ID
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)  # 取出所有用户的课程
        course_ids = [user_course.course.id for user_course in all_user_courses]  # 取出所有课程id
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]  # 取出该用户学过的其他所有课程
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.all().order_by("-add_time")   # 将所有评论取出

        return render(request, "course-comment.html", {
            "course": course,
            "course_resources": all_resources,
            "all_comments": all_comments,
            "relate_courses": relate_courses

        })


class AddCommentsView(View):        # 用户添加课程评论
    def post(self,request):
        if not request.user.is_authenticated():   # 判断用户是否登录
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        course_id = request.POST.get("course_id", 0)    # 取出ID和评论
        comments = request.POST.get("comments", "")
        if course_id >0 and comments:   # 验证ID 并保证评论不为空
            course_comments = CourseComments()              # 对ID用户，评论保存到数据库
            course = Course.objects.get(id=int(course_id))
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse('{"status":"success", "msg":"添加成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加失败"}', content_type='application/json')


class VideoPlayView(View):          # 视频播放页面
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))                          # 获取该课程的信息
        course = video.lesson.course
        course.student += 1
        course.save()
        user_courses = UserCourse.objects.filter(user=request.user, course=course)  # 查询用户是否已经关联了该课程
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)   # 添加该用户信息
            user_course.save()
        user_courses = UserCourse.objects.filter(course=course)                 # 取出学习该课程的用户
        user_ids = [user_course.user.id for user_course in user_courses]        # 列表推导，取出所有用户的ID
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)      # 取出所有用户的课程
        course_ids = [user_course.course.id for user_course in all_user_courses]    # 取出所有课程id
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]  # 取出该用户学过的其他所有课程
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, "course-play.html", {
            "course": course,
            "course_resources": all_resources,
            "relate_courses": relate_courses,
            "video": video

        })









