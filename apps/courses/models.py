# coding=utf-8
from __future__ import unicode_literals
from datetime import datetime               #使用DateTimeField时，别忘了import

from django.db import models
from organization.models import CourseOrg,Teacher
from DjangoUeditor.models import UEditorField
# Create your models here.


class Course(models.Model):
    course_org = models.ForeignKey(CourseOrg, verbose_name=u"课程机构",null=True, blank=True)
    name = models.CharField(max_length=50,verbose_name=u"课程名")
    desc = models.CharField(max_length=300,verbose_name=u"课程描述")
    teacher = models.ForeignKey(Teacher, verbose_name=u"讲师", null=True, blank=True)
    tag = models.CharField(default="", max_length=10, verbose_name=u"课程标签")
    detail =UEditorField(verbose_name=u"课程详情",width=600, height=300, imagePath="courses/ueditor/", filePath="courses/ueditor/", default="")
    is_banner = models.BooleanField(default=False, verbose_name=u"是否轮播")
    degree = models.CharField(verbose_name=u'难度', choices=(("cj", "初级"),("zj", "中级"),("gj", "高级")), max_length=2)
    learn_time = models.IntegerField(default=0,verbose_name=u"学习时长（分钟）")
    student = models.IntegerField(default=0,verbose_name=u"学习人数")
    fav_nums = models.IntegerField(default=0,verbose_name=u"收藏人数")
    category = models.CharField(default=u"后端开发", max_length=20, verbose_name=u"课程类别")
    youneed_know = models.CharField( max_length=300, verbose_name=u"课程需知")
    teacher_tell = models.CharField(max_length=300, verbose_name=u"老师告诉你")
    image = models.ImageField(upload_to="courses/%Y/%m",verbose_name=u"封面", max_length=100)
    click_nums = models.IntegerField(default=0,verbose_name=u"点击数")
    add_time = models.DateTimeField(default=datetime.now,verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程"
        verbose_name_plural = verbose_name

    def get_zj_nums(self):  # 获取课程章节数
        return self.lesson_set.all().count()
    get_zj_nums.short_description = "章节数"

    def get_learn_users(self):
        return self.usercourse_set.all()[:5]

    def get_course_lesson(self):  # 获取课程所有章节
        return self.lesson_set.all()

    def __unicode__(self):              # 重载Unicode方法
        return self.name


class BannerCourse(Course):
    class Meta:
        verbose_name = u"轮播课程"
        verbose_name_plural = verbose_name
        proxy = True


class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name=u"课程")
    name = models.CharField(max_length=100, verbose_name=u"章节名")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"章节"
        verbose_name_plural = verbose_name

    def get_lesson_video(self):  # 获取章节视频
            return self.video_set.all()

    def __unicode__(self):
        return self.name


class Video(models.Model):
    lesson = models.ForeignKey(Lesson,verbose_name=u"章节")
    name = models.CharField(max_length=100,verbose_name=u"视频名")
    url = models.CharField(max_length=500, default="", verbose_name=u"访问地址")
    learn_time = models.IntegerField(default=0, verbose_name=u"学习时长（分钟）")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"视频"
        verbose_name_plural = verbose_name

    def __unicode__(self):              # 重载Unicode方法
        return self.name


class CourseResource(models.Model):
    course = models.ForeignKey(Course,verbose_name=u"课程")
    name = models.CharField(max_length=100,verbose_name=u"名称")
    download = models.FileField(upload_to="courses/resource/%Y/%m",verbose_name="资源文件", max_length=100)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程资源"
        verbose_name_plural = verbose_name










