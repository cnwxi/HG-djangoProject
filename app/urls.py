from django.urls import path
from . import views

urlpatterns = [
    path('login', views.signin),
    path('register', views.register),
    # path('login', views.login),
    path('', views.signin),
    path('<int:userid>', views.index, name='home'),
    path('logout', views.logout, name='myLogout'),
    # path('live', views.live,),
    path('<int:userid>/live', views.live, name='myLive'),
    # path('log', views.log, ),
    path('<int:userid>/log', views.log, name='myLog'),
    # path('setting', views.setting),
    path('<int:userid>/setting', views.setting, name='mySetting'),
    path('post_case', views.post_case),
    path('get_link', views.get_link),
    path('check_link', views.check_link),
    path('data', views.data),
    path('<int:userid>/change_link', views.change_link),
    path('<int:userid>/change_push', views.change_push),
    path('<int:userid>/on_off_push', views.on_off_push),
    path('<int:userid>/change_email', views.change_email),
    path('<int:userid>/change_password', views.change_password),
    path('<int:userid>/check_push', views.check_push),
    path('test', views.test)
]
