import logging

import django_redis
from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.views import View

from meiduo_mall.settings.dev import QQ_CLIENT_ID, QQ_CLIENT_SECRET, QQ_REDIRECT_URI
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.signature_serializer import *
from oauth import constants
from oauth.models import OAuthQQUser
from users.models import User

logger = logging.getLogger('django')


class OauthURLView(View):
    def get(self, request):
        next = request.GET.get('next')
        qq_oauth = OAuthQQ(client_id=QQ_CLIENT_ID, client_secret=QQ_CLIENT_SECRET, redirect_uri=QQ_REDIRECT_URI,
                           state=next)
        qq_url = qq_oauth.get_qq_url()
        return http.JsonResponse({'code': RETCODE.OK, 'login_url': qq_url})


class OauthCallBackView(View):
    def get(self, request):
        code = request.GET.get('code')
        next_url = request.GET.get('state')
        qq_oauth = OAuthQQ(client_id=QQ_CLIENT_ID, client_secret=QQ_CLIENT_SECRET, redirect_uri=QQ_REDIRECT_URI)
        token = qq_oauth.get_access_token(code)
        open_id = qq_oauth.get_open_id(token)
        # 判断openid是否已关联用户
        try:
            qq_user = OAuthQQUser.objects.get(open_id=open_id)
        # 否: 返回oauth_callback页面,携带加密的openid
        except:
            token = generate_access_token({'openid': open_id}, constants.OPENID_EXPIRES)
            return render(request, 'oauth_callback.html', {'token': token})
        # 是: 状态保持  返回首页
        else:
            user = qq_user.user
            login(request, user)
            response = redirect(next_url)
            response.set_cookie('username', user.username)
        return response

    def post(self, request):
        # 获取
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('pwd')
        msg_code_cli = request.POST.get('sms_code')
        token = request.POST.get('access_token')
        # 校验
        conn=django_redis.get_redis_connection('identification')
        try:
            msg_code_server=conn.get('sms_%s' % mobile)
            logger.info(msg_code_cli)
        except:
            return render(request, 'oauth_callback.html', {'errmsg': '短信验证码已过期'})
        if msg_code_cli != msg_code_server.decode():
            return render(request, 'oauth_callback.html', {'errmsg': '短信验证码填写错误'})

        open_id = check_access_token(token, constants.OPENID_EXPIRES)
        if not open_id:
            logger.info(token)
            return render(request, 'oauth_callback.html', {'errmsg': 'openid已过期'})
        # 处理
        # 查看用户是否存在
        try:
            user = User.objects.get(mobile=mobile)
        # 不存在,创建用户
        except Exception as e:
            user = User.objects.create_user(username=mobile, password=pwd, mobile=mobile)
        # 存在,检查用户密码
        else:
            if not user.check_password(pwd):
                return render(request, 'oauth_callback.html', {'errmsg': '手机号或密码错误'})
        # 将用户绑定open_id
        try:
            OAuthQQUser.objects.create(open_id=open_id, user=user)
        except Exception as e:
            return render(request, 'oauth_callback.html', {'errmsg': 'qq登录失败'})
        login(request, user)
        next_url = request.GET.get('state')
        response = redirect(next_url)
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)
        return response
