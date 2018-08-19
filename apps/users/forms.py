# coding=utf-8
_author_ = 'Yasin'
_date_ = '2018-03-30 21:07'

from django import forms
from .models import UserProfile
from captcha.fields import CaptchaField


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)  # 密码必须存在且长度不小于5


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    captcha = CaptchaField(error_messages={"required": u"请输入验证码"})      ##
    # captcha = CaptchaField(error_messages={"invalid": u"验证码错误"})


class ForgetForm(forms.Form):
    email = forms.EmailField(required=True)
    captcha = CaptchaField(error_messages={"required": u"请输入验证码"})


class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)  # 密码必须存在且长度不小于5
    password2 = forms.CharField(required=True, min_length=5)


class UploadImageForm(forms.ModelForm):
    class Meta:    # 指定使用那个model和该model的那些字段
        model = UserProfile
        fields = ['image']


class UserInfoForm(forms.ModelForm):
    class Meta:    # 指定使用那个model和该model的那些字段
        model = UserProfile
        fields = ['nike_name', 'birday', 'gender',  'address', 'mobile']