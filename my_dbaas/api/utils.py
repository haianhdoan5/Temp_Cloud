import mysql.connector
from django.conf import settings


def create_database_and_user(db_name, db_password, username):
    # Lấy cấu hình Admin MySQL
    DB_CONFIG = settings.DBAAS_ADMIN_CONFIG
    # Tạo tên user dựa trên username của Django
    new_user = f"user_{username}"

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

    # 1. Tạo Database (Giữ nguyên)
    try:
        mycursor.execute(f"CREATE DATABASE {db_name}")
    except Exception as e:
        mydb.close()
        return False, f"Lỗi tạo Database: {e}"

    # 2. Xử lý User (SỬA ĐOẠN NÀY)
    try:
        # Lệnh 1: Tạo user NẾU CHƯA TỒN TẠI (IF NOT EXISTS)
        # Giúp tránh lỗi 1396 khi tạo DB thứ 2 trở đi
        mycursor.execute(
            f"CREATE USER IF NOT EXISTS '{new_user}'@'%' IDENTIFIED BY '{db_password}'"
        )

        # Lệnh 2: Cập nhật mật khẩu mới nhất cho user này (để chắc chắn user dùng pass mới nhập)
        mycursor.execute(f"ALTER USER '{new_user}'@'%' IDENTIFIED BY '{db_password}'")

        # Lệnh 3: Cấp quyền cho user này trên database MỚI
        mycursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{new_user}'@'%'")

        # Lệnh 4: Áp dụng quyền
        mycursor.execute("FLUSH PRIVILEGES")

        mydb.commit()
    except Exception as e:
        # Nếu lỗi thì xóa DB vừa tạo để dọn rác
        try:
            mycursor.execute(f"DROP DATABASE {db_name}")
        except:
            pass
        mydb.close()
        return False, f"Lỗi tạo User hoặc cấp quyền: {e}"

    mydb.close()
    return True, {
        "db_name": db_name,
        "db_user": new_user,
        "db_password": db_password,
        "host": DB_CONFIG["HOST"],
    }


def delete_database_from_mysql(db_name):
    DB_CONFIG = settings.DBAAS_ADMIN_CONFIG

    try:
        mydb = mysql.connector.connect(
            host=DB_CONFIG["HOST"],
            user=DB_CONFIG["USER"],
            password=DB_CONFIG["PASSWORD"],
            port=DB_CONFIG["PORT"],
        )
        mycursor = mydb.cursor()

        # Lệnh DROP DATABASE (IF EXISTS để không lỗi nếu nó lỡ bị xóa rồi)
        mycursor.execute(f"DROP DATABASE IF EXISTS {db_name}")

        mydb.close()
        return True, "Đã xóa thành công"
    except Exception as e:
        return False, str(e)
