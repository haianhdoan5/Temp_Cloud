from django.contrib.auth.models import User
from django.db import models


class UserDatabase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Database này của ai?
    db_name = models.CharField(max_length=255)
    db_user = models.CharField(max_length=255)
    db_password = models.CharField(
        max_length=255
    )  # Lưu tạm password (thực tế nên mã hóa kỹ hơn)
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo

    def __str__(self):
        return self.db_name
