from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import Provision, UserLogin, Users
from .utils import create_database_and_user


# API để tạo người dùng mới (Đăng ký)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = Users


# View Đăng nhập
class LoginView(APIView):
    def post(self, request):
        # 1. Lấy dữ liệu từ người dùng gửi lên
        serializer = UserLogin(data=request.data)

        # 2. Kiểm tra dữ liệu có hợp lệ không
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]

            # 3. Dùng hàm authenticate để kiểm tra user/pass trong Database
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                # Nếu đúng: Trả về thông báo thành công
                return Response(
                    {
                        "message": "Đăng nhập thành công!",
                        "user_id": user.id,
                        "username": user.username,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                # Nếu sai: Báo lỗi
                return Response(
                    {"error": "Tài khoản hoặc mật khẩu không đúng"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        # Nếu dữ liệu đầu vào lỗi (ví dụ thiếu username)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View Cung cấp Database (Provisioning)
class ProvisionView(APIView):
    # Người dùng đăng nhập mới gọi được API này
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = Provision(data=request.data)

        if serializer.is_valid():
            db_name = serializer.validated_data.get("db_name")
            db_password = serializer.validated_data["db_password"]

            # Nếu tên DB trống, dùng tên của người dùng + ID để tạo tên duy nhất
            if not db_name:
                db_name = f"{request.user.username}_{request.user.id}_db"

            # GỌI HÀM TẠO DB TỪ FILE utils.py
            success, result = create_database_and_user(
                db_name,
                db_password,
                request.user.id,  # Dùng ID của người dùng làm username MySQL
            )

            if success:
                return Response(
                    {"message": "Tạo Database thành công!", "db_info": result},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {
                        "error": "Lỗi hệ thống khi tạo Database.",
                        "details": result,  # result ở đây là thông báo lỗi
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
