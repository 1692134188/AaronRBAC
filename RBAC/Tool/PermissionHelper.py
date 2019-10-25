from django.shortcuts import render, redirect, HttpResponse
from django.shortcuts import render
from RBAC.Form import UserForm
from RBAC.models import User,Role,Permission2Action,Menu
from django.urls import reverse
import re
class PermissionHelper(object):
    def __init__(self,request,userName):
        self.request = request
        self.userName=userName
        self.current_url = request.path_info  # 获取当前路径
        # 清空并初始化当前用户信息
        self.permission2action_dict = None
        self.menu_leaf_list = None
        self.menu_list = None
        self.session_data()

    def session_data(self):
        # 从session中获取数据
        permission_dict = self.request.session.get('permission_info')
        if permission_dict:
            self.menu_leaf_list = permission_dict['menu_leaf_list']
            self.menu_list = permission_dict['menu_list']
        else:
            # 01 根据用户名称，获取菜单
            menu_list = Menu.objects.values("id", "caption", "parent_id")
            # 02 根据用户名称，获取角色，方便后期根据角色获取权限
            role_list = Role.objects.filter(user2role__u__userName=self.userName)
            # 03 根据角色名称，获取权限
            menu_leaf_list = Permission2Action.objects.filter(role2permission2action__r__in=role_list) \
                .exclude(p__m__isnull=True).values("p__id", "p__url", "p__caption", "p__m_id", "a__code").distinct()
            # 放入到session中
            self.request.session['permission_info'] = {
                'menu_leaf_list': list(menu_leaf_list),
                'menu_list': list(menu_list),
            }
            self.menu_leaf_list = menu_leaf_list
            self.menu_list = menu_list

    def menu_data_list(self):
        open_leaf_parent_id=None
        menu_left_dict = {}
        for menuLeft in self.menu_leaf_list:
            # 把列表中的元素的值重新初始化成新元素。也就是我们菜单最终想要的格式
            menuLeft = {"id": menuLeft['p__id'],
                        "url": menuLeft['p__url'],
                        "caption": menuLeft['p__caption'],
                        "parent_id": menuLeft['p__m_id'],
                        "children": [],
                        "action": [menuLeft['a__code'], ],
                        'status': True,  # 是否显示
                        'open': False,  # 菜单是否打开
                        }
            # 以父级id为K，内容为 V 分类
            K = menuLeft["parent_id"]
            V = menuLeft
            if K in menu_left_dict:
                # 已经存在 同一级别 的权限了
                for item in menu_left_dict[K]:
                    # 将权限相同，动作不同的，将动作添加到Action中
                    if V["id"] == item["id"]:
                        # 需要注意，添加的时候只能添加字符串
                        item["action"].append(V["action"][0])
                        break
                else:
                    # for else，用的好，功能很强
                    menu_left_dict[K].append(V)
            else:
                menu_left_dict[K] = []
                menu_left_dict[K].append(V)
            # 这里只是记录到需要展开的父编码id，下面再使用
            if re.match(menuLeft["url"], self.current_url):
                menuLeft["open"] = True
                open_leaf_parent_id = menuLeft["parent_id"]

        menu_dict = {}
        # 初始化菜单
        for nemu in self.menu_list:
            menu_dict[nemu['id']] = nemu
            menu_dict[nemu['id']]["children"] = []
            menu_dict[nemu["id"]]["status"] = False  # 默认为不显示节点
            menu_dict[nemu["id"]]["open"] = False  # 默认为不打开节点
        # 将列表放置到菜单中
        for k,v in menu_left_dict.items():
            menu_dict[k]["children"] = v
            parent_id = k
            while parent_id:
                # 将列表挂靠在菜单上的时候，把有权限的那一条菜单的状态值都设置成True
                menu_dict[parent_id]["status"] = True
                parent_id = menu_dict[parent_id]["parent_id"]
            if k==open_leaf_parent_id:
                for item in v:
                   if item["url"]==self.current_url:
                        self.action_list =item["action"]
        # 将本条线上的菜单打开
        while open_leaf_parent_id:
            menu_dict[open_leaf_parent_id]['open'] = True
            open_leaf_parent_id = menu_dict[open_leaf_parent_id]['parent_id']
        top_menu = []
        for menu in menu_dict.values():
            K = menu["parent_id"]
            if K:
                menu_dict[K]['children'].append(menu)
            else:
                top_menu.append(menu)
        return top_menu

    def menu_tree(self,fromWay,childList):
        # 定义formWay，如果formWay=True，表示从外部直接获取；如果formWay=False，表示从自己调用自己
        # 递归方法 主要两大特点：1自己调自己 2：循环有终止
        response = ""
        tpl = """
                 <div class="item %s">
                      <div class="title"  onclick="showChild(this)">%s</div>
                      <div class="content"  >%s</div>
                  </div>
                """
        # 2保证了循环可终止
        if fromWay:
            childList=self.menu_data_list()
        for item in childList:
            if not item["status"]:
                continue
            title = item["caption"]
            content = self.menu_tree(False,item["children"])
            # 1 自己调自己
            if 'url' in item:
                response += "<a class='%s' href='%s'>%s</a>" % ("active" if item['open'] else "", item['url'], item['caption'])
            else:
                response += tpl % ("active" if item['open'] else "", title, content)
        return response

# 定义一个装饰器。（闭包）
def permission(func):
    def inner(request,*args,**kwargs):
        user_info = request.session.get('user_info')
        if not user_info:
            return redirect('login.html')
        obj = PermissionHelper(request,user_info["userName"])
        kwargs['menu_string'] = obj.menu_tree(True,None)
        kwargs['action_list'] = obj.action_list
        return func(request,*args,**kwargs)
    return inner

