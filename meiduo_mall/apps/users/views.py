import re

import django_redis
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django import http
from django.views import View

from users.models import User


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        user_name = request.POST.get('user_name')
        pwd = request.POST.get('pwd')
        cpwd = request.POST.get('cpwd')
        phone = request.POST.get('phone')
        msg_code_cli = request.POST.get('msg_code')
        allow = request.POST.get('allow')

        if not all([user_name, pwd, cpwd, phone, allow]):
            return http.HttpResponseBadRequest('参数不全')

        # 检验用户名
        if not re.match('^[a-zA-Z0-9_-]{5,20}$', user_name):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')

        if User.objects.filter(username=user_name).count() > 0:
            return http.HttpResponseBadRequest('用户名已存在')

        # 检验密码
        if not re.match('^[0-9A-Za-z]{8,20}$', pwd):
            return http.HttpResponseBadRequest('请输入8-20位的密码')

        if pwd != cpwd:
            return http.HttpResponseBadRequest('两次输入的密码不一致')

        # 检验手机号
        if not re.match('^1[345789]\d{9}$', phone):
            return http.HttpResponseBadRequest('请输入正确的手机号码')

        if User.objects.filter(mobile=phone).count()>0:
            return http.HttpResponseBadRequest('手机号已存在')

        # 检验短信验证码
        conn = django_redis.get_redis_connection('identification')
        msg_code_server = conn.get(phone)
        if msg_code_server is None:
            return http.HttpResponseBadRequest('验证码已过期')
        msg_code_server = msg_code_server.decode()
        if msg_code_server !=msg_code_cli:
            return http.HttpResponseBadRequest('验证码填写有误')

        # 处理
        user = User.objects.create_user(username=user_name,password=pwd,mobile=phone)
        login(request,user)

        # 响应
        return redirect('/')


class UserCheckView(View):
    def get(self,request,username):
        count=User.objects.filter(username=username).count()
        return http.JsonResponse({'count':count})

class PhoneCheckView(View):
    def get(self,request,phonenum):
        count=User.objects.filter(mobile=phonenum).count()
        return http.JsonResponse({'count':count})
