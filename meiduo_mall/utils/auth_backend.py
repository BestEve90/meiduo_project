import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


class AuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if request is None:
            try:
                user = User.objects.get(username=username, is_staff=True)
            except:
                return None
            else:
                if not user.check_password(password):
                    return None
                return user
        else:
            try:
                if re.match('^1[345789]\d{9}', username):
                    user = User.objects.get(mobile=username)
                else:
                    user = User.objects.get(username=username)
            except Exception as e:
                return None
            else:
                if not user.check_password(password):
                    return None
                return user
