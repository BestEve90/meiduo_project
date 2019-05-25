from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import Serializer
from meiduo_admin.serializers.users_serializer import UserSerializer
from rest_framework.response import Response
from users.models import User


class PageNum(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'pagesize'
    max_page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'counts': self.page.paginator.count,
            'lists': data,
            'page': self.page.number,
            'pages': self.page.paginator.num_pages,
            'pagesize': self.page_size
        })


class UsersView(ListAPIView):
    serializer_class = UserSerializer
    pagination_class = PageNum

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword == '' or keyword is None:
            return User.objects.all()
        else:
            return User.objects.filter(username=keyword)
