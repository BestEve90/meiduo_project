from QQLoginTool.QQtool import OAuthQQ
from django.shortcuts import render, redirect
from django.views import View
from django import http
from meiduo_mall.settings.dev import QQ_CLIENT_ID, QQ_CLIENT_SECRET, QQ_REDIRECT_URI
from meiduo_mall.utils.response_code import RETCODE
from oauth.models import OAuthQQUser
from django.contrib.auth import login
from users.models import User
from oauth.utils import *
import logging

logger=logging.getLogger('django')

class OauthURLView(View):
    def get(self, request):
        next = request.GET.get('next')
        qq_oauth = OAuthQQ(client_id=QQ_CLIENT_ID, client_secret=QQ_CLIENT_SECRET, redirect_uri=QQ_REDIRECT_URI,
                           state=next)
        qq_url = qq_oauth.get_qq_url()
        return http.JsonResponse({'code': RETCODE.OK, 'login_url': qq_url})


class OauthOpenidView(View):
    def get(self, request):
        code = request.GET.get('code')
        qq_oauth = OAuthQQ(client_id=QQ_CLIENT_ID, client_secret=QQ_CLIENT_SECRET, redirect_uri=QQ_REDIRECT_URI)
        token = qq_oauth.get_access_token(code)
        open_id = qq_oauth.get_open_id(token)
        # 判断用户是否已关联用户
        try:
            qq_user = OAuthQQUser.objects.get(open_id=open_id)
        # 否: 返回oauth_callback页面,携带加密的openid
        except Exception as e:
            token = generate_access_token(open_id)
            return render(request, 'oauth_callback.html', {'token': token})
        # 是: 状态保持  返回首页
        else:
            user = qq_user.user
            login(request, user)
            response = redirect('/')
            response.set_cookie('username', user.username)
        return response

    def post(self, request):
        # 获取
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('pwd')
        pic_code = request.POST.get('pic_code')
        msg_code = request.POST.get('msg_code')
        token = request.POST.get('access_token')
        open_id = check_access_token(token)
        # 校验
        if not open_id:
            logger.info(token)
            return http.HttpResponse('无效的openid')
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
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        return response
