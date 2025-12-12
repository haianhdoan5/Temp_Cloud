from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import UserDatabase
from .serializers import Provision, UserDatabaseSerializer, UserLogin, Users
from .utils import create_database_and_user, delete_database_from_mysql


# Bỏ qua kiểm tra CSRF cho Session
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # Không kiểm tra CSRF


# API để tạo người dùng mới (Đăng ký)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = Users
    authentication_classes = (CsrfExemptSessionAuthentication,)


# View Đăng nhập
class LoginView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def post(self, request):
        serializer = UserLogin(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return Response(
                    {
                        "message": "Đăng nhập thành công!",
                        "user_id": user.id,
                        "username": user.username,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Tài khoản hoặc mật khẩu không đúng"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View Cung cấp Database (Provisioning)
class ProvisionView(APIView):
    permission_classes = [IsAuthenticated]

    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = Provision(data=request.data)

        if serializer.is_valid():
            db_name = serializer.validated_data.get("db_name")
            db_password = serializer.validated_data["db_password"]

            if not db_name:
                db_name = f"{request.user.username}_{request.user.id}_db"

            success, result = create_database_and_user(
                db_name,
                db_password,
                request.user.id,
            )

            if success:
                UserDatabase.objects.create(
                    user=request.user,
                    db_name=result["db_name"],
                    db_user=result["db_user"],
                    db_password=result["db_password"],
                )
                return Response(
                    {"message": "Tạo Database thành công!", "db_info": result},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {
                        "error": "Lỗi hệ thống khi tạo Database.",
                        "details": result,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View liệt kê các Database của user hiện tại
class DatabaseListView(generics.ListAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserDatabaseSerializer

    def get_queryset(self):
        # Chỉ lấy những database do chính user này tạo ra
        return UserDatabase.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )


class DatabaseDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def delete(self, request, pk):
        try:
            # 1. Tìm Database trong lịch sử Django theo ID (pk) và User
            # (Chỉ xóa được nếu DB đó thuộc về user đang đăng nhập)
            user_db = UserDatabase.objects.get(pk=pk, user=request.user)

            # 2. Xóa thật trong MySQL
            success, msg = delete_database_from_mysql(user_db.db_name)

            if success:
                # 3. Nếu xóa MySQL thành công thì xóa luôn dòng log trong Django
                user_db.delete()
                return Response(
                    {"message": "Đã xóa Database thành công!"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Lỗi MySQL: " + msg},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except UserDatabase.DoesNotExist:
            return Response(
                {"error": "Không tìm thấy Database hoặc bạn không có quyền xóa."},
                status=status.HTTP_404_NOT_FOUND,
            )
