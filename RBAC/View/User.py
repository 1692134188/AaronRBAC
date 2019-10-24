from django.shortcuts import render, redirect, HttpResponse
from RBAC.Form.UserForm import LoginForm
from RBAC.models import Menu


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
            menu_string = PermissionHelper(obj.cleaned_data['userName'])
            # return redirect('menu.html')
            return render(request, 'Home/menu.html', {'menu_string': menu_string})
        else:
            return render(request, 'Home/login.html', {'obj': obj})


def menu(request):
    return render(request, 'Home/menu.html')
def PermissionHelper(userName):
    # 01 根据用户名称，获取菜单
    menu_list = Menu.objects.all()
    # menu_string = menu_tree(menu_list)
    menu_string = menu_content2(0)
    return menu_string

def menu_content2(parid):
    #递归方法 主要两大特点：1自己调自己 2：循环有终止
    response = ""
    tpl = """
             <div>
                  <div class="title" >%s</div>
                  <div class="content">%s</div>
              </div>
              """
    if parid==0:
        menu_list = Menu.objects.all()
    else:
        menu_list = Menu.objects.filter(parent_id=parid)
    # 2保证了循环可终止
    if menu_list :
        for item in menu_list:
            if item.parent_id == parid :
                title = item.caption
                # 1 自己调自己
                content = menu_content2(item.id)
                response += tpl % (title, content)
            elif not item.parent_id :
                title = item.caption
                # 1 自己调自己
                content = menu_content2(item.id)
                response += tpl % (item.caption, content)
    return response