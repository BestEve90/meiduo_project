from rest_framework.generics import ListCreateAPIView
from meiduo_admin.serializers.users_serializer import UserSerializer
from meiduo_admin.utils.page_num import PageNum
from users.models import User


class UsersView(ListCreateAPIView):
    serializer_class = UserSerializer
    pagination_class = PageNum

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword == '' or keyword is None:
            return User.objects.all()
        else:
            return User.objects.filter(username=keyword)
