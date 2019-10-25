from django.shortcuts import render, redirect, HttpResponse
from RBAC.Form.UserForm import LoginForm
from RBAC.models import Menu, Permission2Action, Role
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
            menu_string = permissionHelper(obj.cleaned_data['userName'])
            # return redirect('menu.html')
            return render(request, 'Home/menu.html', {'menu_string': menu_string})
        else:
            return render(request, 'Home/login.html', {'obj': obj})
def menu(request):
    return render(request, 'Home/menu.html')
def permissionHelper(userName):
    # 01 根据用户名称，获取菜单
    menu_list = Menu.objects.values("id", "caption", "parent_id")
    # 02 根据用户名称，获取角色，方便后期根据角色获取权限
    role_list = Role.objects.filter(user2role__u__userName=userName)
    # 03 根据角色名称，获取权限
    menu_leaf_list = Permission2Action.objects.filter(role2permission2action__r__in=role_list) \
        .exclude(p__m__isnull=True).values("p__id", "p__url", "p__caption", "p__m_id", "a__code").distinct()
    # 结果示例
    # {'p__id': 4, 'p__url': '/RBAC/GNHDUserInfo.html', 'p__caption': '（国内-华东）用户权限', 'p__m_id': 6, 'a__code': 'get'},
    # {'p__id': 5, 'p__url': '/RBAC/GNHBUserInfo.html', 'p__caption': '（国内-华北）用户权限', 'p__m_id': 6, 'a__code': 'get'},
    # {'p__id': 6, 'p__url': '/RBAC/menu.html', 'p__caption': '菜单权限', 'p__m_id': 2, 'a__code': 'put'},
    # {'p__id': 6, 'p__url': '/RBAC/menu.html', 'p__caption': '菜单权限', 'p__m_id': 2, 'a__code': 'get'},
    # {'p__id': 2, 'p__url': '/RBAC/OrderInfo.html', 'p__caption': '订单权限', 'p__m_id': 4, 'a__code': 'get'}

    formatMenu = menu_data_list(menu_list, menu_leaf_list)
    menu_string = menu_tree(formatMenu)
    # menu_string = menu_content2(0)
    return menu_string
def menu_data_list(menu_list, menu_leaf_list):
    menu_left_dict = {}
    for menuLeft in menu_leaf_list:
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
    # 此时 权限表中的数据是这样的
    # 4[{'id': 4, 'url': '/RBAC/GNHDUserInfo.html', 'caption': '（国内-华东）用户权限', 'parent_id': 4, 'children': [],'action': ['get'], 'status': True, 'open': False},
    #   {'id': 5, 'url': '/RBAC/GNHBUserInfo.html', 'caption': '（国内-华北）用户权限', 'parent_id': 4, 'children': [],'action': ['get'], 'status': True, 'open': False}]
    # 2[{'id': 6, 'url': '/RBAC/menu.html', 'caption': '菜单权限', 'parent_id': 2, 'children': [], 'action': ['put', 'get'],'status': True, 'open': False}]
    # 6[{'id': 2, 'url': '/RBAC/OrderInfo.html', 'caption': '订单权限', 'parent_id': 6, 'children': [], 'action': ['get'],'status': True, 'open': False}]
    menu_dict = {}
    # 初始化菜单
    for nemu in menu_list:
        menu_dict[nemu['id']] = nemu
        menu_dict[nemu['id']]["children"] = []
        menu_dict[nemu["id"]]["status"] = False  # 默认为不显示节点
        menu_dict[nemu["id"]]["open"] = False  # 默认为不打开节点
    # 将列表放置到菜单中
    for k, v in menu_left_dict.items():
        menu_dict[k]["children"] = v
    # 此时的菜单列表
    # 1 {'id': 1, 'caption': '一、报表管理', 'parent_id': None, 'children': [], 'status': False, 'open': False}
    # 2 {'id': 2, 'caption': '二、系统管理', 'parent_id': None, 'children': [{'id': 6, 'url': '/RBAC/menu.html', 'caption': '菜单权限', 'parent_id': 2, 'children': [], 'action': ['put', 'get'], 'status': True, 'open': False}], 'status': False, 'open': False}
    # 3 {'id': 3, 'caption': '菜单三', 'parent_id': None, 'children': [], 'status': False, 'open': False}
    # 4 {'id': 4, 'caption': '一、1、1、国内客户', 'parent_id': 5, 'children': [{'id': 4, 'url': '/RBAC/GNHDUserInfo.html', 'caption': '（国内-华东）用户权限', 'parent_id': 4, 'children': [], 'action': ['get'], 'status': True, 'open': False}, {'id': 5, 'url': '/RBAC/GNHBUserInfo.html', 'caption': '（国内-华北）用户权限', 'parent_id': 4, 'children': [], 'action': ['get'], 'status': True, 'open': False}], 'status': False, 'open': False}
    # 5 {'id': 5, 'caption': '一、1、客户报表', 'parent_id': 1, 'children': [], 'status': False, 'open': False}
    # 6 {'id': 6, 'caption': '一、2、订单报表', 'parent_id': 1, 'children': [{'id': 2, 'url': '/RBAC/OrderInfo.html', 'caption': '订单权限', 'parent_id': 6, 'children': [], 'action': ['get'], 'status': True, 'open': False}], 'status': False, 'open': False}
    # 设置表单等级，并且获取顶级菜单

    top_menu = []
    for menu in menu_dict.values():
        K = menu["parent_id"]
        if K:
            menu_dict[K]['children'].append(menu)
        else:
            top_menu.append(menu)
    # {'id': 1, 'caption': '一、报表管理', 'parent_id': None,
    #  'children': [{'id': 5, 'caption': '一、1、客户报表', 'parent_id': 1,
    #                'children': [{'id': 4, 'caption': '一、1、1、国内客户', 'parent_id': 5,
    #                              'children': [{'id': 4, 'url': '/RBAC/GNHDUserInfo.html', 'caption': '（国内-华东）用户权限',
    #                                            'parent_id': 4, 'children': [], 'action': ['get'], 'status': True,
    #                                            'open': False},
    #                                           {'id': 5, 'url': '/RBAC/GNHBUserInfo.html', 'caption': '（国内-华北）用户权限',
    #                                            'parent_id': 4, 'children': [], 'action': ['get'], 'status': True,
    #                                            'open': False}],
    #                              'status': False, 'open': False}],
    #                'status': False, 'open': False},
    #               {'id': 6, 'caption': '一、2、订单报表', 'parent_id': 1,
    #                'children': [
    #                    {'id': 2, 'url': '/RBAC/OrderInfo.html', 'caption': '订单权限', 'parent_id': 6, 'children': [],
    #                     'action': ['get'], 'status': True, 'open': False}], 'status': False, 'open': False}],
    #  'status': False, 'open': False}
    # {'id': 2, 'caption': '二、系统管理', 'parent_id': None,
    #  'children': [{'id': 6, 'url': '/RBAC/menu.html', 'caption': '菜单权限', 'parent_id': 2, 'children': [],
    #                'action': ['put', 'get'], 'status': True, 'open': False}], 'status': False, 'open': False}
    # {'id': 3, 'caption': '菜单三', 'parent_id': None, 'children': [], 'status': False, 'open': False}
    return top_menu
def menu_tree(formatMenu):
    # 递归方法 主要两大特点：1自己调自己 2：循环有终止
    response = ""
    tpl = """
             <div>
                  <div class="title" >%s</div>
                  <div class="content">%s</div>
              </div>
              """

    # 2保证了循环可终止
    for item in formatMenu:
        title = item["caption"]
        content=menu_tree(item["children"])
        # 1 自己调自己
        if 'url' in item:
            response += "<a href='%s'>%s</a>" % (item['url'], item['caption'])
        else:
            response += tpl % (title, content)
    return response

def menu_content2(parid):
    # 递归方法 主要两大特点：1自己调自己 2：循环有终止
    response = ""
    tpl = """
             <div>
                  <div class="title" >%s</div>
                  <div class="content">%s</div>
              </div>
              """
    if parid == 0:
        menu_list = Menu.objects.all()
    else:
        menu_list = Menu.objects.filter(parent_id=parid)
    # 2保证了循环可终止
    if menu_list:
        for item in menu_list:
            if item.parent_id == parid:
                title = item.caption
                # 1 自己调自己
                content = menu_content2(item.id)
                response += tpl % (title, content)
            elif not item.parent_id:
                title = item.caption
                # 1 自己调自己
                content = menu_content2(item.id)
                response += tpl % (item.caption, content)
    return response

