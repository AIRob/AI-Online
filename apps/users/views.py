# coding=utf-8
import json
from django.shortcuts import render         # 快捷键
from django.contrib.auth import authenticate, login, logout     # 扩展包 认定  鉴定
from django.contrib.auth.backends import ModelBackend
from users.models import UserProfile, EmailVerifyRecord
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from operation.models import UserCourse,UserFavorite, UserMessage
from organization.models import CourseOrg, Teacher
from courses.models import Course
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from .models import Banner
from django.views.generic.base import View
from django.core.urlresolvers import reverse
from users.forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, UploadImageForm, UserInfoForm

# Create your views here.


class CustomBackend(ModelBackend):  # 通过后台模版将其实例化
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class ActiveUserView(View):     # 与ResetView(View)类似，用于鉴定激活链接是否有效，是否可以返回注册或找回密码页面
    def get(self, request, active_code):    # get返回的是一个对象
        all_records = EmailVerifyRecord.objects.filter(code=active_code)  # filter返回的是一个list
        if all_records:     # 验证链接是否有效
            for record in all_records:
                email = record.email   # 将请求的email赋值给email
                user = UserProfile.objects.get(email=email)  # 将用email获取数据库里的用户，并返回激活信息
                user.is_active = True
                user.save()
        else:
            return render(request, "active_fail.html")  # 若无效则返回，链接无效页面
        return render(request, "login.html")


class RegisterView(View):       # 处理前端请求的View类，加view是为了增加代码的可读性
    def get(self, request):
        register_form = RegisterForm()
        all_banners = Banner.objects.all().order_by('index')  # 取出轮播图
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'register.html', {
            'register_form': register_form,
            'all_banners': all_banners,
            'courses': courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs
        })

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email', '')
            if UserProfile.objects.filter(email=user_name):  # 使用过滤器判断用户名是否存在
                return render(request, 'register.html', {"register_form": register_form, "msg": "用户已经存在"})
            pass_word = request.POST.get('password', '')
            user_profile = UserProfile()        # 建立一个新用户，将类进行实例化，用于存储用户信息
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False
            user_profile.password = make_password(pass_word)    # Django自带密码加密函数
            user_profile.save()

            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = "欢迎注册慕学在线-人工智能在线学习交流平台"
            user_message.save()

            send_register_email(user_name, "register")  # 发送验证邮件，类型为register
            return render(request, "send_success.html")  # 邮件发送成功提示
        else:
            return render(request, 'register.html', {"register_form": register_form})


class LogoutView(View):   # 用户退出
    def get(self, request):
        logout(request)

        return HttpResponseRedirect(reverse("index"))


class LoginView(View):
    def get(self, request):
        all_banners = Banner.objects.all().order_by('index')  # 取出轮播图
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        course_orgs = CourseOrg.objects.all()[:15]

        return render(request, 'login.html', {
            'all_banners': all_banners,
            'courses': courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs
        })

    def post(self, request):
        login_form = LoginForm(request.POST)        # 使用form对post进行预处理，判断是否为空，最小最大长度，减小其它负担
        if login_form.is_valid():
            user_name = request.POST.get('username', '')
            pass_word = request.POST.get('password', '')
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)

                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, 'login.html', {'msg': '用户未激活！'})

            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误！'})
        else:
            return render(request, 'login.html', {'login_form': login_form})


class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        all_banners = Banner.objects.all().order_by('index')  # 取出轮播图
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, "forgetpwd.html", {
            'forget_form': forget_form,
            'all_banners': all_banners,
            'courses': courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs
        })

    def post(self, request):
        forget_form = ForgetForm(request.POST)      # 此处传的是dic
        if forget_form.is_valid():
            email = request.POST.get('email', '')
            send_register_email(email, 'forget')        # 发送邮件，类型为forget
            return render(request, "send_success.html")    # 邮件发送成功提示
        else:
            return render(request, "forgetpwd.html", {'forget_form': forget_form})


class ResetView(View):          # 进入密码重置页面
    def get(self, request, active_code):    # get返回的是一个对象
        all_records = EmailVerifyRecord.objects.filter(code=active_code)  # filter返回的是一个list
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, "password_reset.html", {'email': email})
        else:
            return render(request, "active_fail.html")
        return render(request, "login.html")


class ModifyPwdView(View):      # 重置密码逻辑

    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            email = request.POST.get('email', '')
            if pwd1 != pwd2:
                return render(request, "password_reset.html", {'email': email, "msg": "密码不一致"})
            user = UserProfile.objects.get(email=email)     # 匹配用户
            user.password = make_password(pwd2)  # 对密码进行加密
            user.save()
            return render(request, "login.html")
        else:
            email = request.POST.get('email', '')
            return render(request, "password_reset.html", {'email': email, "modify_form": modify_form})


class UserInfoView(LoginRequiredMixin, View):    # 用户个人信息,继承登录才能访问的VIEW
    def get(self, request):
        return render(request, 'usercenter-info.html', {})

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')


class UploadImageView(LoginRequiredMixin, View):    # 修改用户头像
    def post(self, request):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


class UpdatePwdView(View):      # 个人中心重置密码逻辑

    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail", "msg":"密码不一致"}', content_type='application/json')
            user = request.user     # 匹配用户
            user.password = make_password(pwd2)  # 对密码进行加密
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


class SendEmailCodeView(LoginRequiredMixin, View):   # 发送邮箱验证码
    def get(self, request):
        email = request.GET.get('email', '')

        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已经存在"}', content_type='application/json')
        send_register_email(email, "update_email")
        return HttpResponse('{"status":"success"}', content_type='application/json')


class UpdateEmailView(LoginRequiredMixin, View):  # 修改个人邮箱
    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')

        existed_recodes = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        if existed_recodes:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"验证码出错"}', content_type='application/json')


class MyCourseView(LoginRequiredMixin, View):   # 我的课程
    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, "usercenter-mycourse.html", {
            "user_courses": user_courses
        })


class MyFavOrgView(LoginRequiredMixin, View):   # 我收藏的课程机构
    def get(self, request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, "usercenter-fav-org.html", {
            "org_list": org_list
        })


class MyFavTeacherView(LoginRequiredMixin, View):   # 我收藏的课程机构
    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, "usercenter-fav-teacher.html", {
            "teacher_list": teacher_list
        })


class MyFavCourseView(LoginRequiredMixin, View):   # 我收藏的课程
    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request, "usercenter-fav-course.html", {
            "course_list": course_list
        })


class MyMessageView(LoginRequiredMixin, View):   # 我的消息
    def get(self, request):
        all_messages = UserMessage.objects.filter(user=request.user.id)
        # 用户进入个人消息后清空未读记录
        all_unread_messages = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()
        try:                                # 进行分页
            page = request.GET.get('page', 1)  # 取出page页面
        except PageNotAnInteger:
            page = 1
        # 为完成查询的字符串请求对象提供生成分页器。
        p = Paginator(all_messages, 1, request=request)     # 调用分页函数，将来自于HTML的课程机构进行每页五个的分页处理
        messages = p.page(page)    # 调用函数取到第几页的数据，返回给定基于页码的页面对象

        return render(request, "usercenter-message.html", {
            "messages": messages
        })


class IndexView(View):   # 慕学在线网首页
    def get(self, request):
        all_banners = Banner.objects.all().order_by('index')  # 取出轮播图
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html', {
            'all_banners': all_banners,
            'courses':courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs
        })


def page_not_found(request):    # 全局404处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def page_error(request):    # 全局500处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response




