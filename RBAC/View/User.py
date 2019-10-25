from django.shortcuts import render, redirect, HttpResponse
from RBAC.Form.UserForm import LoginForm
from RBAC.models import Menu, Permission2Action, Role
from RBAC.Tool.PermissionHelper import permission,PermissionHelper
import re
def index(request):
    return render(request, 'Home/index.html')
def login(request):
    if request.method == 'GET':
        obj = LoginForm(request)
        return render(request, 'Home/login.html', {'obj': obj})
    else:
        # Post请求，提交而来
        obj = LoginForm(request, request.POST)
        # 判断用户名密码是否正确
        if obj.is_valid():
            current_url = request.path_info  # 获取当前路径
            # menu_string = permissionHelper(obj.cleaned_data['userName'],current_url)
            userName=obj.cleaned_data['userName']
            request.session['user_info'] = {'userName': userName}
            PermissionHelper(request, userName)
            return redirect('menu.html')
        else:
            return render(request, 'Home/login.html', {'obj': obj})
@permission
def menu(request,*args,**kwargs):
    menu_string = kwargs.get('menu_string')
    action_list = kwargs.get('action_list')
    return render(request, 'Home/menu.html', {'menu_string': menu_string, 'action_list': action_list})

def logout(request):
    request.session.clear()
    obj = LoginForm(request)
    return render(request, 'Home/login.html', {'obj': obj})


