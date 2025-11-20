from django.conf import settings
from django.contrib.auth.models import User

# model có sẵn trong django
from rest_framework import serializers


class Users(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, user_info):
        user = User.objects.create_user(
            username=user_info["username"],
            email=user_info["email"],
            password=user_info["password"],
        )
        return user


class UserLogin(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        if not data.get("username") or not data.get("password"):
            raise serializers.ValidationError("Cần nhập đủ username và password")
        return data


class Provision(serializers.Serializer):
    db_name = serializers.CharField(allow_blank=True, max_length=100)

    db_password = serializers.CharField(write_only=True, max_length=100)

    def validate(self, data):

        if " " in data.get("db_password"):
            raise serializers.ValidationError(
                "Mật khẩu database không được chứa khoảng trắng."
            )

        return data
