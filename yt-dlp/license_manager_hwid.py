from tkinter import Tk, messagebox, simpledialog
import license_utils as lu


def check_license_ui():
    key = lu.load_license_key()
    if not key:
        entered_key = simpledialog.askstring(
            "Nhập License Key", "Vui lòng nhập key để kích hoạt:")
        if not entered_key:
            messagebox.showerror("Lỗi", "Chưa nhập key!")
            return False
        key = entered_key.strip()

    ok, msg = lu.verify_license(key)
    if ok:
        lu.save_license_key(key)
        messagebox.showinfo("OK", f"Kích hoạt thành công! ({msg})")
        return True
    else:
        messagebox.showerror("Lỗi", msg)
        return False


def admin_mode():
    hwid = simpledialog.askstring(
        "Admin - Tạo Key",
        "Nhập HWID của máy cần tạo key (để trống để lấy HWID máy này):"
    )
    if hwid is None:
        return
    hwid = hwid.strip() if hwid.strip() else lu.get_hardware_id()

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

    hwid_val, expire_date, key = lu.create_license(hwid, options[choice])
    messagebox.showinfo(
        "License Key đã tạo",
        f"HWID: {hwid_val}\nHết hạn: {expire_date}\n\nKey (đã lưu vào {lu.LICENSE_FILE} và copy vào clipboard):\n{key}"
    )


if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    mode = simpledialog.askstring(
        "Chọn chế độ", "Nhập 'admin' để tạo key, hoặc 'user' để kiểm tra:")
    if mode and mode.lower() == "admin":
        admin_mode()
    else:
        if check_license_ui():
            messagebox.showinfo("Chạy App", "Ứng dụng chính sẽ chạy ở đây...")
        else:
            messagebox.showwarning("Thoát", "Không có license hợp lệ, thoát!")
