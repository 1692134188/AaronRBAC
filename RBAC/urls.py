from django.conf.urls import url
from .View import User
urlpatterns=[
    url(r'^index.html$', User.index),
    url(r'^login.html$', User.login),
    url(r'^menu.html$', User.menu),
    url('^GNHDUserInfo.html$',User.menu),
    url('^OrderInfo.html$',User.menu),
    url(r'^logout.html$', User.logout),

    url(r'^',  User.index),
]