from Cryptodome.Cipher import AES
from datetime import datetime
import base64
import os
# ===== Cấu hình =====
LICENSE_FILE = "license.lic"
LICENSE_NAME = "HTPTO"
EXPIRE_DATE = "2026-01-01"  # YYYY-MM-DD

# 🔑 Key & IV bí mật (16 bytes mỗi cái)
SECRET_KEY = b"1234567890abcdef"  # 16 bytes
IV = b"abcdef1234567890"          # 16 bytes


def encrypt_aes(text):
    """Mã hoá AES + Base64"""
    cipher = AES.new(SECRET_KEY, AES.MODE_CFB, IV)
    return base64.b64encode(cipher.encrypt(text.encode())).decode()


def decrypt_aes(enc_text):
    """Giải mã AES + Base64"""
    cipher = AES.new(SECRET_KEY, AES.MODE_CFB, IV)
    return cipher.decrypt(base64.b64decode(enc_text)).decode()


def create_license():
    """Tạo file license mã hoá"""
    data = f"{LICENSE_NAME}\n{EXPIRE_DATE}"
    encrypted = encrypt_aes(data)

    with open(LICENSE_FILE, "w") as f:
        f.write(encrypted)
    print(f"✅ Đã tạo license {LICENSE_FILE}")


def check_license():
    """
    Kiểm tra license.
    Return:
        (status, data)
        - status: True/False (hợp lệ hay không)
        - data: dict chứa name, expire_date nếu hợp lệ, hoặc thông báo lỗi
    """
    if not os.path.exists(LICENSE_FILE):
        return False, "❌ Không tìm thấy file license."

    try:
        with open(LICENSE_FILE, "r") as f:
            encrypted_data = f.read()

        plain_text = decrypt_aes(encrypted_data)
        name, expire_str = plain_text.strip().split("\n")
        expire_date = datetime.strptime(expire_str, "%Y-%m-%d").date()

        if datetime.now().date() > expire_date:
            return False, f"❌ License {name} đã hết hạn ({expire_date})"

        return True, {
            "name": name,
            "expire_date": expire_date
        }

    except Exception as e:
        return False, f"❌ Lỗi khi đọc license: {e}"
