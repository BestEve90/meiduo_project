from django.views import View
from users.models import User
from datetime import date
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import ListAPIView
from meiduo_admin.serializers.statistics_serializers import CategoryVisitSerializer
from goods.models import GoodsVisitCount


class UerTotalCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()
        count = User.objects.all().count()
        return Response({'count': count, 'date': now_date})


class DailyUerIncrementView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()
        count = User.objects.filter(date_joined__gte=date.today()).count()
        return Response({'count': count, 'date': now_date})


class DailyActiveUserView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()
        count = User.objects.filter(last_login__gte=date.today()).count()
        return Response({'count': count, 'date': now_date})


class DailyOrdersUserView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()
        count = User.objects.filter(orderinfo__create_time__gte=date.today()).count()
        return Response({'count': count, 'date': now_date})


class DailyCategoryVisitView(ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = GoodsVisitCount.objects.filter(date=date.today())
    serializer_class = CategoryVisitSerializer
