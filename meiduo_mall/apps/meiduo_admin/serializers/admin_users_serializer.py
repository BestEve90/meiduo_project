from rest_framework import serializers
from users.models import User


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8
            },
            'username': {
                'max_length': 20,
                'min_length': 5
            }
        }

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data.get('password'))
        user.is_staff = True
        user.save()
        return user

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.set_password(validated_data.get('password'))
        instance.save()
        return instance
