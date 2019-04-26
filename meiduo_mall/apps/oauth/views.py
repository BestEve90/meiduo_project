from QQLoginTool.QQtool import OAuthQQ
from django.shortcuts import render
from django.views import View
from django import http
from meiduo_mall.settings.dev import QQ_CLIENT_ID, QQ_CLIENT_SECRET, QQ_REDIRECT_URI
from meiduo_mall.utils.response_code import RETCODE


class OauthURLView(View):
    def get(self, request):
        next = request.GET.get('next')
        qq_oauth = OAuthQQ(client_id=QQ_CLIENT_ID, client_secret=QQ_CLIENT_SECRET, redirect_uri=QQ_REDIRECT_URI,
                           state=next)
        qq_url = qq_oauth.get_qq_url()
        return http.JsonResponse({'code': RETCODE.OK, 'login_url': qq_url})

class OauthOpenidView(View):
    def get(self,request):
        code=request.GET.get('code')
        qq_oauth = OAuthQQ(client_id=QQ_CLIENT_ID, client_secret=QQ_CLIENT_SECRET, redirect_uri=QQ_REDIRECT_URI)
        token = qq_oauth.get_access_token(code)
        open_id=qq_oauth.get_open_id(token)
        return http.HttpResponse(open_id)