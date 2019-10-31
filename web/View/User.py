from django.shortcuts import render, HttpResponse
from django.views import View
from RBAC.models import User, models
from django.http.request import QueryDict
import json


class UserView(View):
    def get(self, request, *args, **kwargs):
        # 数据库中获取数据
        return render(request, 'Manage/user.html')


class UserJsonView(View):
    def get(self, request, *args, **kwargs):
        table_config = [
            {
                'q': None,
                'title': "选项",
                'display': True,
                'text': {'content': "<input type='checkbox' />", "kwargs": {}},
                'attrs': {}
            },
            {
                'q': 'id',
                'title': 'ID',
                'display': False,
                'text': '',
            },
            {
                'q': 'userName',
                'title': '用户名称',
                'display': True,
                'text': {'content': "{n}", 'kwargs': {'n': "@userName"}},
                'attrs': {'name': 'userName', 'origin': "@userName", 'edit-enable': 'true',
                          'edit-type': 'input'}
            },
            {
                'q': 'user_status_id',
                'title': '状态',
                'display': True,
                'text': {'content': "{n}", 'kwargs': {'n': "@@user_status_choices"}},
                'attrs': {'name': 'user_status_id', 'origin': "@user_status_id", 'edit-enable': 'true',
                          'edit-type': 'select', "global-name": 'user_status_choices'}
            },
            {
                'q': None,
                'title': '操作',
                'display': True,
                'text': {'content': "<a href='/userdetail-{m}.html'>{n}</a>", 'kwargs': {'n': '查看详细', 'm': '@id'}},
            }
        ]
        q_list = []
        for tbcg in table_config:
            if not tbcg['q']:
                continue
            q_list.append(tbcg["q"])

        data_list = User.objects.all().values(*q_list)
        data_list = list(data_list)
        result = {
            'table_config': table_config,
            'data_list': data_list,
            'global_dict': {
                'user_status_choices': User.user_status_choices
            }
        }
        return HttpResponse(json.dumps(result))

    def put(self, request, *args, **kwargs):
        import chardet
        content = request.body
        put_dict = QueryDict(request.body, encoding='utf-8')
        post_list = json.loads(put_dict.get('post_list'))
        # [{'id': '1', 'userName': '赵生1'}]
        for row_dict in post_list:
            id = row_dict.pop('id')
            User.objects.filter(id=id).update(**row_dict)
        ret = {
            'status': True
        }
        return HttpResponse(json.dumps(ret))
