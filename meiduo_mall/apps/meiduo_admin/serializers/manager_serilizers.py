from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from django.contrib.auth.models import Permission, Group


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'name']


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
