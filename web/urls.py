from django.conf.urls import url
from .View import User
urlpatterns=[
    url(r'^user.html$',  User.UserView.as_view()),
    url(r'^user-json.html$', User.UserJsonView.as_view()),
]