# coding = utf-8
_author_ = 'Yasin'
_date_ = '2018-03-26 22:54'
import xadmin

from .models import CourseOrg, CityDict, Teacher


class CourseOrgAdmin(object):
    list_display = ['name', 'desc', 'click_nums', 'fav_nums', 'image', 'address', 'city', 'add_time']
    search_fields = ['name', 'desc', 'click_nums', 'fav_nums', 'image', 'address', 'city']
    list_filter = ['name', 'desc', 'click_nums', 'fav_nums', 'image', 'address', 'city', 'add_time']
    model_icon = 'fa fa-universal-access'
    # relfield_style = 'fk-ajax'


class CityDictAdmin(object):
    list_display = ['name', 'desc', 'add_time']
    search_fields = ['name', 'desc']
    list_filter = ['name', 'desc', 'add_time']
    model_icon = 'fa fa-university'


class TeacherAdmin(object):
    list_display = ['org', 'name', 'work_years', 'work_company', 'work_position', 'points', 'fav_nums', 'click_nums']
    search_fields = ['org', 'name', 'work_years', 'work_company', 'work_position', 'points', 'fav_nums', 'click_nums']
    list_filter = ['org', 'name', 'work_years', 'work_company', 'work_position', 'points', 'fav_nums', 'click_nums']
    model_icon = 'fa fa-user-secret'


xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(CityDict, CityDictAdmin)
xadmin.site.register(Teacher, TeacherAdmin)