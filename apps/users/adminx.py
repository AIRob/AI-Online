# coding=utf-8
import xadmin
from xadmin import views

from .models import EmailVerifyRecord, Banner


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True

# class BaseSetting(object):
#     enable_themes = True        # 打开主题功能
#     use_bootswatch = True       # 打开主题样式


class GlobalSettings():
    site_title = '慕学后台管理系统'
    site_footer = '慕学在线网'
    menu_style = 'accordion'


class EmailVerifyRecordAdmin(object):
    list_display = ['code', 'email', 'send_type', 'send_time']
    search_fields = ['code', 'email', 'send_type']
    list_filter = ['code', 'email', 'send_type', 'send_time']
    model_icon = 'fa fa-envelope'


class BannerAdmin(object):
    list_display = ['title', 'image', 'url', 'index', 'add_time'] # 显示字段
    search_fields = ['title', 'image', 'url', 'index']            # 搜索框
    list_filter = ['title', 'image', 'url', 'index', 'add_time']  # 过滤器
    model_icon = 'fa fa-caret-square-o-right'


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
xadmin.site.register(views.BaseAdminView,BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)