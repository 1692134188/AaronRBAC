from django.db import models

# Create your models here.

#用户表
class User(models.Model):
    userName=models.CharField(max_length=32)
    password=models.CharField(max_length=64)
    class Meta:
        verbose_name_plural='用户表'
    def __str__(self):
        return self.userName
#角色表
class Role(models.Model):
    caption=models.CharField(max_length=100)
    class Meta:
        verbose_name_plural='角色表'
    def __str__(self):
        return self.caption
#用户 角色 关系(多对多)
class User2Role(models.Model):
    u=models.ForeignKey(User,on_delete=models.CASCADE)
    r=models.ForeignKey(Role,on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural="角色配置表"
    def __str__(self):
        return "%s_%s" %(self.u.userName,self.r.caption)
# 菜单表
class Menu(models.Model):
    caption = models.CharField(max_length=200)
    parent=models.ForeignKey('self',related_name='p',null=True,on_delete=True,blank=True)
    class Meta:
        verbose_name_plural='菜单表'#权限表 实质就url
    def __str__(self):
        return "%s" %(self.caption)
class Permission(models.Model):
    caption=models.CharField(max_length=200)
    url=models.CharField(max_length=200)
    m=models.ForeignKey(Menu,on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        verbose_name_plural = "权限表"
    def __str__(self):
        return "%s_%s"%(self.caption,self.url)

#动作表 用户补充权限表中的增删改查(只有4条数据 post、delete、put、get)
class Action(models.Model):
    caption = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
    class Meta:
        verbose_name_plural = "动作表"
    def __str__(self):
        return self.caption

#权限 动作 关系表
class Permission2Action(models.Model):
    p=models.ForeignKey(Permission,on_delete=models.CASCADE)
    a=models.ForeignKey(Action,on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = "权限动作关系表"
    def __str__(self):
        return "%s_%s" %(self.p.caption,self.a.caption)

#角色 权限 关系表  （为角色分配权限）
class Role2Permission2Action(models.Model):
    r=models.ForeignKey(Role,on_delete=models.CASCADE)
    p2a=models.ForeignKey(Permission2Action,on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = "角色分配权限表"
    def __str__(self):
        return "%s_%s_%s" %(self.r.caption,self.p2a.p.caption,self.p2a.a.caption)
