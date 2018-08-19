# coding=utf-8
_author_ = 'Yasin'
_date_ = '2018-04-10 14:43'
from django import forms
from operation.models import UserAsk
import re


class UserAskForm(forms.ModelForm):
    # 此处可以增加model没有的字段
    class Meta:    # 指定使用那个model和该model的那些字段
        model = UserAsk
        fields = ['name', 'mobile', 'course_name']

    def clean_mobile(self):  # 验证手机号码是否合法
        mobile = self.cleaned_data['mobile']
        REGEX_MOBILE = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        p = re.compile(REGEX_MOBILE)
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError(u"手机号码非法", code="mobile_invalid")
