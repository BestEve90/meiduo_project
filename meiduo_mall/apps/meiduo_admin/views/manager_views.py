from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission, Group
from meiduo_admin.utils.page_num import PageNum
from meiduo_admin.serializers.manager_serilizers import PermissionSerializer, ContentTypeSerializer, UserGroupSerializer
from rest_framework.response import Response


class PermisssionViews(ModelViewSet):
    pagination_class = PageNum
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def content_types(self, request):
        types = ContentType.objects.all()
        serializer = ContentTypeSerializer(types, many=True)
        return Response(serializer.data)


class UserGroupViews(ModelViewSet):
    pagination_class = PageNum
    queryset = Group.objects.all()
    serializer_class = UserGroupSerializer
    permission_classes = [IsAdminUser]

    def permission_simple(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)
