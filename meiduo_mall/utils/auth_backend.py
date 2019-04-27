import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


class AuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if re.match('^1[345789]\d{9}',username):
            try:
                user=User.objects.get(mobile=username)
            except Exception as e:
                return None
            else:
                if not user.check_password(password):
                    return None
                return user
