#目的是引入Django的后台admin管理工具
from django.contrib import admin
from . import models

#注册所需要管理的模型
admin.site.register(models.User)
admin.site.register(models.Role)
admin.site.register(models.User2Role)
admin.site.register(models.Permission)
admin.site.register(models.Action)
admin.site.register(models.Permission2Action)
admin.site.register(models.Role2Permission2Action)
admin.site.register(models.Menu)
