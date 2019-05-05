import json
import re
from celery_tasks.email.tasks import send_email
import django_redis
import logging
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django import http
from django.views import View
from meiduo_mall.utils import signature_serializer
from users import constants
from users.models import User, Address
from django.conf import settings
from meiduo_mall.utils.response_code import RETCODE

logger = logging.getLogger('django')


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

        if not all([user_name, pwd, cpwd, phone, msg_code_cli, allow]):
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
        if not re.match(r'^1[345789]\d{9}$', phone):
            return http.HttpResponseBadRequest('请输入正确的手机号码')

        if User.objects.filter(mobile=phone).count() > 0:
            return http.HttpResponseBadRequest('手机号已存在')

        # 检验短信验证码  问题:新返回的页面一直存在error_sms_message这条信息
        conn = django_redis.get_redis_connection('identification')
        msg_code_server = conn.get('sms_%s' % phone)
        if msg_code_server is None:
            return render(
                request, 'register.html', {
                    'error_sms_message': '短信验证码已过期'})
        msg_code_server = msg_code_server.decode()
        if msg_code_server != msg_code_cli:
            return render(
                request, 'register.html', {
                    'error_sms_message': '短信验证码填写有误'})
        conn.delete('sms_%s' % phone)

        # 处理
        user = User.objects.create_user(
            username=user_name, password=pwd, mobile=phone)
        login(request, user)

        # 响应
        response = redirect('/')
        response.set_cookie('username', user_name, max_age=60 * 60 * 24 * 14)
        return response


class UserCheckView(View):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'count': count})


class PhoneCheckView(View):
    def get(self, request, phonenum):
        count = User.objects.filter(mobile=phonenum).count()
        return http.JsonResponse({'count': count})


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        remembered = request.POST.get('remembered')
        if not all([pwd, username]):
            return http.HttpResponseBadRequest('缺少必传参数')
        if not re.match('^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')
        if not re.match('^[0-9A-Za-z]{8,20}$', pwd):
            return http.HttpResponseBadRequest('请输入8-12位的密码')

        user = authenticate(
            username=username,
            password=pwd)  # username可以是用户名或手机号
        if user is None:
            return render(request, 'login.html', {'loginerror': '用户名或密码错误'})

        login(request, user)
        response = redirect('/')
        username = user.username
        if not remembered:
            request.session.set_expiry(0)
            response.set_cookie('username', username)
        else:
            response.set_cookie(
                'username',
                username,
                max_age=60 * 60 * 24 * 14)
        return response


class LogoutView(View):
    def get(self, request):
        logout(request)
        response = redirect('/')
        response.delete_cookie('username')
        return response


class InfoView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context)


class EmailView(LoginRequiredMixin, View):
    def put(self, request):
        email = json.loads(request.body.decode()).get('email')
        if not email:
            return http.HttpResponseBadRequest('邮箱为空')
        if not re.match(
                r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',
                email):
            return http.HttpResponseBadRequest('邮箱格式错误')
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse(
                {'code': RETCODE.EMAILERR, 'errmsg': '添加邮箱失败'})
        # 发送邮件
        # 将user.id加密成token放在激活链接里,以便后面解密找到对应的用户,设置邮箱激活状态
        token = signature_serializer.generate_access_token(
            {'userid': request.user.id}, constants.EMAIL_EXPIRE_TIME)
        # 激活连接包括url和查询字符串token
        verify_url = settings.EMAIL_ACTIVE_URL + '?token=' + token
        send_email.delay(email, verify_url)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


class EmailVerifyView(View):
    def get(self, request):
        # 获取
        token = request.GET.get('token')
        # 验证
        try:
            userid = signature_serializer.check_access_token(
                token, constants.EMAIL_EXPIRE_TIME).get('userid')
        except BaseException:
            return http.HttpResponseBadRequest('激活链接已失效')
        # 处理
        try:
            user = User.objects.get(pk=userid)
        except BaseException:
            return http.HttpResponseBadRequest('激活链接无效')
        else:
            user.email_active = True
            user.save()
        # 响应
        return redirect('/info/')


class AdressesView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        addresses_obj = user.adresses.all()
        addresses = []
        for address in addresses_obj:
            if not address.is_deleted:
                addresses.append(address.to_dict())
        default_address_id = user.default_address_id
        return render(request, 'user_center_site.html', {
            'addresses': addresses,
            'default_address_id': default_address_id
        })


class AdressesCreateView(LoginRequiredMixin, View):
    def post(self, request):
        new_address_info = json.loads(request.body.decode())
        receiver = new_address_info.get('receiver')
        province_id = new_address_info.get('province_id')
        city_id = new_address_info.get('city_id')
        district_id = new_address_info.get('district_id')
        place = new_address_info.get('place')
        mobile = new_address_info.get('mobile')
        tel = new_address_info.get('tel')
        email = new_address_info.get('email')
        # 验证(非空,电话格式,邮箱格式)
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数不全'})
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '手机号格式错误'})
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '电话格式错误'})
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '邮箱格式错误'})

        # 处理(创建收货地址并返回)
        new_address = Address.objects.create(
            user=request.user,
            title=receiver,
            receiver=receiver,
            province_id=province_id,
            city_id=city_id,
            district_id=district_id,
            place=place,
            mobile=mobile,
            tel=tel,
            email=email
        )
        user = request.user
        if user.default_address is None:
            user.default_address = new_address

        return http.JsonResponse(
            {'code': RETCODE.OK, 'errmsg': 'ok', 'address': new_address.to_dict()})


class AdressesUpdateView(LoginRequiredMixin, View):
    def delete(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '地址编号无效'})
        address.is_deleted = True
        address.save()
        user = request.user
        if user.default_address_id == address_id:
            user.default_address = None
            user.save()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})

    def put(self, request, address_id):
        new_address_info = json.loads(request.body.decode())
        receiver = new_address_info.get('receiver')
        province_id = new_address_info.get('province_id')
        city_id = new_address_info.get('city_id')
        district_id = new_address_info.get('district_id')
        place = new_address_info.get('place')
        mobile = new_address_info.get('mobile')
        tel = new_address_info.get('tel')
        email = new_address_info.get('email')
        # 验证(非空,电话格式,邮箱格式)
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数不全'})
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '手机号格式错误'})
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '电话格式错误'})
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '邮箱格式错误'})

        # 处理(修改收货地址并返回)
        try:
            address = Address.objects.get(id=address_id)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '地址编号无效'})
        address.receiver = receiver
        address.province_id = province_id
        address.city_id = city_id
        address.district_id = district_id
        address.place = place
        address.mobile = mobile
        address.tel = tel
        address.email = email
        address.save()
        return http.JsonResponse(
            {'code': RETCODE.OK, 'errmsg': 'ok', 'address': address.to_dict()})


class AdressesDefaulteView(LoginRequiredMixin, View):
    def put(self, request, address_id):
        user = request.user
        user.default_address_id = address_id
        user.save()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})


class AdressesTitleView(LoginRequiredMixin, View):
    def put(self, request, address_id):
        title = json.loads(request.body.decode()).get('title')
        if not all([title]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '地址标题为空'})
        try:
            address = Address.objects.get(id=address_id)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '地址编号错误'})
        address.title = title
        address.save()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})


class PassWordView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_center_pass.html')

    def post(self, request):
        old_pwd = request.POST.get('old_pwd')
        new_pwd = request.POST.get('new_pwd')
        new_cpwd = request.POST.get('new_cpwd')
        # 检验
        user = request.user
        if not all([old_pwd, new_cpwd, new_pwd]):
            return http.HttpResponseBadRequest('数据不能为空')

        if not user.check_password(old_pwd):
            return http.HttpResponseBadRequest('原始密码错误')

        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_pwd):
            return http.HttpResponseBadRequest('新密码格式不对')

        if new_pwd != new_cpwd:
            return http.HttpResponseBadRequest('两次输入的新密码不一致')

        user.set_password(new_pwd)
        user.save()
        return render(request, 'user_center_pass.html')
