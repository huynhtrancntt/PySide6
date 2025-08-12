import os
import uuid
import base64
import pyperclip
import json
from datetime import datetime, timedelta
from Cryptodome.Cipher import AES
from tkinter import Tk, messagebox, simpledialog

# ===== Cấu hình =====
SECRET_KEY = b"1234567890ABCDEF1234567890ABCDEF"  # 32 bytes (AES-256)
LICENSE_FILE = "license.key"

# ===== Hàm tiện ích =====


def get_hardware_id():
    """Lấy HWID (ở đây dùng MAC address)"""
    return str(uuid.getnode())


def encrypt_data(data: dict) -> str:
    """Mã hóa dữ liệu dict và trả về key"""
    json_data = json.dumps(data).encode()
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(json_data)
    return base64.urlsafe_b64encode(cipher.nonce + tag + ciphertext).decode()


def decrypt_data(key: str) -> dict:
    """Giải mã key và trả về dict"""
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

# ===== Giao diện =====


def check_license():
    key = load_license_key()
    if not key:
        entered_key = simpledialog.askstring(
            "Nhập License Key", "Vui lòng nhập key để kích hoạt:"
        )
        if not entered_key:
            messagebox.showerror("Lỗi", "Chưa nhập key!")
            return False
        key = entered_key.strip()

    try:
        data = decrypt_data(key)
        actual_hwid = get_hardware_id()
        expire_date = datetime.strptime(data["expire"], "%Y-%m-%d")

        if data["hwid"] != actual_hwid:
            messagebox.showerror(
                "Sai Key", "License Key không khớp với máy này!")
            return False

        if expire_date != datetime(9999, 12, 31) and datetime.now() > expire_date:
            messagebox.showerror("Hết hạn", "License Key đã hết hạn!")
            return False

        save_license_key(key)  # lưu lại nếu nhập lần đầu
        if expire_date == datetime(9999, 12, 31):
            messagebox.showinfo("OK", "Kích hoạt thành công! (Vĩnh viễn)")
        else:
            days_left = (expire_date - datetime.now()).days
            messagebox.showinfo(
                "OK", f"Kích hoạt thành công!\nCòn {days_left} ngày sử dụng.")
        return True

    except Exception as e:
        messagebox.showerror("Lỗi", f"Key không hợp lệ!\n{e}")
        return False


def admin_mode():
    hwid = simpledialog.askstring(
        "Admin - Tạo Key",
        "Nhập HWID của máy cần tạo key (để trống để lấy HWID máy này):"
    )
    if hwid is None:
        return
    hwid = hwid.strip() if hwid.strip() else get_hardware_id()

    # Menu chọn thời hạn
    options = {
        "1": 7,
        "2": 14,
        "3": 30,
        "4": 180,
        "5": 365,
        "6": "forever"
    }
    choice = simpledialog.askstring(
        "Chọn thời hạn",
        "1. 7 ngày\n2. 14 ngày\n3. 1 tháng\n4. 6 tháng\n5. 1 năm\n6. Vĩnh viễn\n\nNhập số:"
    )
    if choice not in options:
        messagebox.showerror("Lỗi", "Lựa chọn không hợp lệ!")
        return

    if options[choice] == "forever":
        expire_date = datetime(9999, 12, 31).strftime("%Y-%m-%d")
    else:
        expire_date = (datetime.now() +
                       timedelta(days=options[choice])).strftime("%Y-%m-%d")

    data = {"hwid": hwid, "expire": expire_date}
    key = encrypt_data(data)

    save_license_key(key)  # Lưu key vào file
    try:
        pyperclip.copy(key)  # Copy vào clipboard
    except Exception:
        pass

    messagebox.showinfo(
        "License Key đã tạo",
        f"HWID: {hwid}\nHết hạn: {expire_date}\n\nKey (đã lưu vào {LICENSE_FILE} và copy vào clipboard):\n{key}"
    )


# ===== Main App =====
if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Ẩn cửa sổ chính

    mode = simpledialog.askstring(
        "Chọn chế độ", "Nhập 'admin' để tạo key, hoặc 'user' để kiểm tra:"
    )
    if mode and mode.lower() == "admin":
        admin_mode()
    else:
        if check_license():
            messagebox.showinfo("Chạy App", "Ứng dụng chính sẽ chạy ở đây...")
        else:
            messagebox.showwarning("Thoát", "Không có license hợp lệ, thoát!")
