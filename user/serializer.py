# from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers

from user.models import Profile


# from user.models import User


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['first_name', 'last_name', 'email','username','password','phone']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        field = ['image', 'address', 'nin', 'bvn']