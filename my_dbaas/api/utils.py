import mysql.connector
from django.conf import settings


def create_database_and_user(db_name, db_password, username):
    # Lấy cấu hình Admin MySQL từ settings.py
    DB_CONFIG = settings.DBAAS_ADMIN_CONFIG

    # Tạo login mới cho user
    new_user = f"user_{username}"

    # Kết nối tới MySQL Server bằng tài khoản root/admin
    try:
        mydb = mysql.connector.connect(
            host=DB_CONFIG["HOST"],
            user=DB_CONFIG["USER"],
            password=DB_CONFIG["PASSWORD"],
            port=DB_CONFIG["PORT"],
        )
        mycursor = mydb.cursor()
    except Exception as e:
        return False, f"Lỗi kết nối Admin MySQL: {e}"

    # 1. Tạo Database
    try:
        mycursor.execute(f"CREATE DATABASE {db_name}")
    except Exception as e:
        mydb.close()
        return False, f"Lỗi tạo Database: {e}"

    # 2. Tạo User và cấp quyền truy cập
    try:
        # Tạo user mới với mật khẩu và giới hạn quyền truy cập từ 'localhost' (hoặc '%')
        mycursor.execute(f"CREATE USER '{new_user}'@'%' IDENTIFIED BY '{db_password}'")

        # Cấp toàn quyền (ALL PRIVILEGES) cho user này trên database vừa tạo
        mycursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{new_user}'@'%'")

        # Áp dụng thay đổi
        mydb.commit()
    except Exception as e:
        # Nếu có lỗi, cố gắng xóa database đã tạo để tránh rác
        try:
            mycursor.execute(f"DROP DATABASE {db_name}")
        except:
            pass
        mydb.close()
        return False, f"Lỗi tạo User hoặc cấp quyền: {e}"

    # 3. Kết thúc
    mydb.close()
    return True, {
        "db_name": db_name,
        "db_user": new_user,
        "db_password": db_password,
        "host": DB_CONFIG["HOST"],
    }
