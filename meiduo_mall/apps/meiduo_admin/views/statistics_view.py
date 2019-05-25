from django.views import View
from users.models import User
from datetime import date
from rest_framework.response import Response
from rest_framework.views import APIView


class UerTotalCountView(APIView):
    def get(self, request):
        now_date = date.today()
        count = User.objects.all().count()
        return Response({'count': count, 'date': now_date})
