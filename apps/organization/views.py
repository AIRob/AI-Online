# coding=utf-8
from django.shortcuts import render
from django.views.generic import View
from .models import CourseOrg, CityDict, Teacher
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render_to_response
from .forms import UserAskForm
from django.http import HttpResponse
from courses.models import Course
from operation.models import UserFavorite
from courses.models import Course
from django.db.models import Q

# Create your views here.


class OrgView(View):
    """ 课程机构列表功能"""
    def get(self, request):
        all_orgs = CourseOrg.objects.all()   # 取出所有课程机构
        hot_orgs = all_orgs.order_by("-click_nums")[:3]  # 热门机构倒序排名 选取3个
        all_citys = CityDict.objects.all()    # 取出所有城市
        search_keywords = request.GET.get('keywords', "")    # 机构搜索
        if search_keywords:
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))
        city_id = request.GET.get('city', "")       # city={{ city_id }}用户点击此url会将城市ID赋值给city，现从HTML中取出取出筛选城市，默认为空
        if city_id:                                 # 如果数据库city_id存在的话
            all_orgs = all_orgs.filter(city_id=int(city_id))  # 过滤器，Django的model里，可以直接 外键_id 做筛选
        category = request.GET.get('ct', "")        # 类别筛选
        if category:
            all_orgs = all_orgs.filter(category=category)

        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                all_orgs = all_orgs.order_by("-students")
            elif sort == "courses":
                all_orgs = all_orgs.order_by("-course_nums")

        org_nums = all_orgs.count()   # 计算当前机构数

        try:                                # 对课程机构进行分页
            page = request.GET.get('page', 1)  # 取出page页面
        except PageNotAnInteger:
            page = 1
        # 为完成查询的字符串请求对象提供生成分页器。
        p = Paginator(all_orgs, 5, request=request)     # 调用分页函数，将来自于HTML的课程机构进行每页五个的分页处理
        orgs = p.page(page)    # 调用函数取到第几页的数据，返回给定基于页码的页面对象
        return render(request, "org-list.html", {       # 通过字典的键将值返回给HTML页面，以供HTML遍历时使用
            "all_orgs": orgs,  # 当前页只显示分页后的机构，而不是所有机构
            "all_citys": all_citys,
            "org_nums": org_nums,       # 将机构数返回给HTML页面
            "city_id": city_id,  # 返回给HTML页面，完成比对，若HTML页面city.id和数据库ID city_id一样时则选中
            "category": category,  # 将类别返回到HTML中
            "hot_orgs": hot_orgs,
            "sort": sort,
        })


class AddUserAskView(View):  # 用户添加咨询
    def post(self, request):
        userask_form = UserAskForm(request.POST)  # 实例化，预判提交表单是否有效
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)  # 提交到数据库并保存
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加错误"}', content_type='application/json')
            # return HttpResponse('{"status":"fail", "msg":{0}}'.format(userask_form.errors), content_type='application/json')


class OrgHomeView(View):        # 机构首页
    def get(self, request, org_id):
        current_page = "home"
        course_org = CourseOrg.objects.get(id=int(org_id))   # 选出机构
        all_courses = course_org.course_set.all()[:3]       # 选出该机构的前三个课程
        course_org.click_nums += 1
        course_org.save()
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course_org.id), fav_type=2):
                has_fav = True
        all_teachers = course_org.teacher_set.all()[:1]
        return render(request, 'org-detail-homepage.html', {
            'all_courses': all_courses,
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
            })


class OrgCourseView(View):        # 机构课程列表首页
    def get(self,request, org_id):
        current_page = "course"
        course_org = CourseOrg.objects.get(id=int(org_id))  # 取出机构
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id =int(course_org.id),fav_type= 2):
                has_fav = True
        all_courses = course_org.course_set.all()   # 取出课程
        return render(request, 'org-detail-course.html',{
            'all_courses': all_courses,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
            })


class OrgDescView(View):        # 机构介绍页
    def get(self,request, org_id):
        current_page = "desc"
        course_org = CourseOrg.objects.get(id=int(org_id))  # 取出机构
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course_org.id), fav_type=2):
                has_fav = True
        return render(request, 'org-detail-desc.html',{
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
            })


class OrgTeacherView(View):        # 机构教师页
    def get(self,request, org_id):
        current_page = "teacher"
        course_org = CourseOrg.objects.get(id=int(org_id))  # 取出机构
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course_org.id), fav_type=2):
                has_fav = True
        all_teachers = course_org.teacher_set.all()   # 取出课程
        return render(request, 'org-detail-teachers.html',{
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
            })


class AddFavView(View):         # 用户收藏
    def post(self, request):
        fav_id = request.POST.get('fav_id',0)  # 从前端页面取回 ID 和type
        fav_type = request.POST.get('fav_type',0)

        if not request.user.is_authenticated():   # 判断用户是否登录
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id =int(fav_id),fav_type= int(fav_type) )
        if exist_records:  # 如果记录存在，则表示用户取消收藏
            exist_records.delete()
            if int(fav_type) == 1:
                course = Course.objects.get(id=int(fav_id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(fav_type) == 2:
                course_org = CourseOrg.objects.get(id=int(fav_id))
                course_org.fav_nums -= 1
                if course_org.fav_nums < 0:
                    course_org.fav_nums = 0
                course_org.save()
            elif int(fav_type) == 3:
                teacher = Teacher.objects.get(id=int(fav_id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()

            return HttpResponse('{"status":"success", "msg":"收藏"}', content_type='application/json')
        else:
            user_fav = UserFavorite()       # 实例化对象
            if int(fav_id) > 0 and int(fav_type) > 0:  # 如果请求存在的话
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()
                if int(fav_type) == 1:
                    course = Course.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    course.save()
                elif int(fav_type) == 2:
                    course_org = CourseOrg.objects.get(id=int(fav_id))
                    course_org.fav_nums += 1
                    course_org.save()
                elif int(fav_type) == 3:
                    teacher = Teacher.objects.get(id=int(fav_id))
                    teacher.fav_nums += 1
                    teacher.save()
                return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json' )


class TeacherListView(View):   # 课程讲师列表页
    def get(self, request):
        all_teachers = Teacher.objects.all()
        search_keywords = request.GET.get('keywords', "")  # 教师搜索
        if search_keywords:
            all_teachers = all_teachers.filter(Q(name__icontains=search_keywords) |
                                               Q(work_company__icontains=search_keywords)|
                                               Q(work_position__icontains=search_keywords))
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "hot":
                all_teachers = all_teachers.order_by("-click_nums")
        teacher_nums = all_teachers.count()  # 计算当前机构数
        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]

        try:                                # 进行分页
            page = request.GET.get('page', 1)  # 取出page页面
        except PageNotAnInteger:
            page = 1
        # 为完成查询的字符串请求对象提供生成分页器。
        p = Paginator(all_teachers, 5, request=request)     # 调用分页函数，将来自于HTML的课程机构进行每页五个的分页处理
        teachers = p.page(page)    # 调用函数取到第几页的数据，返回给定基于页码的页面对象
        return render(request, "teachers-list.html", {
            "all_teachers": teachers,
            "sorted_teacher": sorted_teacher,
            "sort": sort,
            "teacher_nums": teacher_nums
        })


class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        teacher.click_nums += 1
        teacher.save()
        all_courses = Course.objects.filter(teacher=teacher)

        has_teacher_faved = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
                has_teacher_faved = True

        has_org_faved = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
                has_org_faved = True
        # 讲师排行
        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]
        return render(request, "teacher-detail.html", {
            "teacher": teacher,
            "all_courses": all_courses,
            "sorted_teacher": sorted_teacher,
            "has_teacher_faved": has_teacher_faved,
            "has_org_faved": has_org_faved,
        })







