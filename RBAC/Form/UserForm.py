from django import forms
from django.forms import fields
from django.core.validators import RegexValidator
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from RBAC.models import User
from .base import BaseForm

class LoginForm(BaseForm,forms.Form):
    userName = fields.CharField(
        error_messages={
            'required': '用户名不能为空',
        }

    )
    password = fields.CharField(
        error_messages={
            'required': '密码不能为空',
        })

    def clean(self):
        userName =self.cleaned_data.get("userName")
        password =self.cleaned_data.get("password")
        # 可以使用Q查询 Q(username=userName) & Q(pwd=pwd)
        userInfo = User.objects.filter(userName=userName,password=password)
        if userInfo:
            pass
        else:
            self.add_error("userName", "用户名不存在或密码错误")
            raise ValidationError(message='用户名不存在或密码错误', code='invalid')
        return self.cleaned_data
