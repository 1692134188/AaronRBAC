from django.shortcuts import render,redirect,HttpResponse
from RBAC.Form.UserForm import LoginForm
def index(request):
    return render(request,'Home/index.html')

def login(request):
    if request.method=='GET':
        obj=LoginForm(request)
        return render(request,'Home/login.html',{'obj':obj})
    else:
        # Post请求，提交而来
        obj = LoginForm(request,request.POST)
        # 判断用户名密码是否正确
        if  obj.is_valid():
            return HttpResponse("登录成功")
        else:
            return render(request, 'Home/login.html', {'obj': obj})
