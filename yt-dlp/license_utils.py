import os
import uuid
import base64
import json
from datetime import datetime, timedelta
from Cryptodome.Cipher import AES

# ===== Cấu hình =====
SECRET_KEY = b"1234567890ABCDEF1234567890ABCDEF"  # 32 bytes
LICENSE_FILE = "license.key"

# ===== Hàm tiện ích =====


def get_hardware_id():
    """Lấy HWID (MAC address dạng XX-XX-XX-XX-XX-XX)"""
    mac = uuid.getnode()
    return "-".join(f"{(mac >> ele) & 0xff:02X}" for ele in range(40, -1, -8))
    # return   str(uuid.getnode())


def encrypt_data(data: dict) -> str:
    """Mã hóa dict -> string"""
    json_data = json.dumps(data).encode()
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(json_data)
    return base64.urlsafe_b64encode(cipher.nonce + tag + ciphertext).decode()


def decrypt_data(key: str) -> dict:
    """Giải mã string -> dict"""
    raw = base64.urlsafe_b64decode(key.encode())
    nonce = raw[:16]
    tag = raw[16:32]
    ciphertext = raw[32:]
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX, nonce=nonce)
    json_data = cipher.decrypt_and_verify(ciphertext, tag)
    return json.loads(json_data.decode())


def save_license_key(key: str):
    """Lưu key vào file"""
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        f.write(key.strip())


def load_license_key() -> str:
    """Đọc key từ file"""
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def create_license(hwid: str, duration: str) -> str:
    """Tạo license với thời hạn"""
    if duration == "forever":
        expire_date = datetime(9999, 12, 31).strftime("%Y-%m-%d")
    else:
        expire_date = (datetime.now() +
                       timedelta(days=int(duration))).strftime("%Y-%m-%d")
    data = {"hwid": hwid, "expire": expire_date}
    key = encrypt_data(data)
    save_license_key(key)
    return hwid, expire_date, key


def verify_license(key: str) -> (bool, str):
    """Kiểm tra license hợp lệ hay không"""
    try:
        data = decrypt_data(key)
        actual_hwid = get_hardware_id()
        expire_date = datetime.strptime(data["expire"], "%Y-%m-%d")

        if data["hwid"] != actual_hwid:
            return False, "License Key không khớp với máy này!"

        if expire_date != datetime(9999, 12, 31) and datetime.now() > expire_date:
            return False, "License Key đã hết hạn!"

        if expire_date == datetime(9999, 12, 31):
            return True, "Vĩnh viễn"
        else:
            days_left = (expire_date - datetime.now()).days
            return True, f"Còn {days_left} ngày sử dụng"
    except Exception:
        return False, "Key không hợp lệ!"
