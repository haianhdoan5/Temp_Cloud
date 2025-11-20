from django.urls import path

from .views import LoginView, ProvisionView, RegisterView

urlpatterns = [
    # Đường dẫn API sẽ là: /api/register(Đăng ký)/
    path("register/", RegisterView.as_view(), name="register"),
    # Đường dẫn API sẽ là: /api/login(Đăng nhập)/
    path("login/", LoginView.as_view(), name="login"),
    path("provision/", ProvisionView.as_view(), name="provision"),
]
