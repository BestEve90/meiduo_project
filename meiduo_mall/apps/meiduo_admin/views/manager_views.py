from django.contrib.contenttypes.models import ContentType
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission
from meiduo_admin.utils.page_num import PageNum
from meiduo_admin.serializers.manager_serilizers import PermissionSerializer, ContentTypeSerializer
from rest_framework.response import Response


class PermisssionViews(ModelViewSet):
    pagination_class = PageNum
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def content_types(self, request):
        types = ContentType.objects.all()
        serializer = ContentTypeSerializer(types, many=True)
        return Response(serializer.data)
