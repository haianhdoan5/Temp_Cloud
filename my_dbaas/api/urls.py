from django.urls import path

from .views import (
    DatabaseDeleteView,
    DatabaseListView,
    LoginView,
    ProvisionView,
    RegisterView,
)

urlpatterns = [
    # Đường dẫn API sẽ là: /api/register(Đăng ký)/
    path("register/", RegisterView.as_view(), name="register"),
    # Đường dẫn API sẽ là: /api/login(Đăng nhập)/
    path("login/", LoginView.as_view(), name="login"),
    path("provision/", ProvisionView.as_view(), name="provision"),
    path("my-databases/", DatabaseListView.as_view(), name="my-databases"),
    path(
        "delete-database/<int:pk>/",
        DatabaseDeleteView.as_view(),
        name="delete-database",
    ),
]
