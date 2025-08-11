# updater_stub/updater_stub.py
import argparse, os, sys, time, zipfile, shutil, subprocess
import zipfile
import subprocess
def wait_file_unlocked(path: str, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            if os.path.exists(path):
                with open(path, "ab"):
                    pass
            return True
        except Exception:
            time.sleep(0.5)
    return False

def extract_overwrite(zip_path: str, target_dir: str):
    with zipfile.ZipFile(zip_path, 'r') as z:
        for m in z.infolist():
            # Tạo thư mục nếu cần
            extract_path = os.path.join(target_dir, m.filename)
            if m.is_dir():
                os.makedirs(extract_path, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(extract_path), exist_ok=True)
            # Ghi đè
            with z.open(m, 'r') as src, open(extract_path, 'wb') as dst:
                shutil.copyfileobj(src, dst)

def main():
   
    # python update_tool.py --app "C:\MyApp\main.exe" --zip "update.zip" --dir "C:\MyApp" --restart

    p = argparse.ArgumentParser()
    p.add_argument("--app", required=True, help="đường dẫn exe chính")
    p.add_argument("--zip", required=True, help="gói cập nhật zip")
    p.add_argument("--dir", required=True, help="thư mục app")
    p.add_argument("--restart", action="store_true")
    args = p.parse_args()

    app_exe =  args.app # os.path.abspath(args.app)
    
    app_dir = args.dir # os.path.abspath(args.dir)
    zip_path = args.zip # os.path.abspath(args.zip)
    app_name = os.path.basename(args.app)
    zip_password = "1234x56"
    if not os.path.isfile(args.zip):
        print("❌ Không tìm thấy file zip.")
        exit(1) 
    # In ra giá trị
    print(f"📌 File exe chính: {app_exe}")
    print(f"📌 Gói cập nhật: {zip_path}")
    print(f"📌 Thư mục app: {app_dir}")
    print(f"📌 Restart sau khi cập nhật: {args.restart}")
    # Bước 1: Tắt app nếu đang chạy

    os.system(f'taskkill /f /im "{app_name}" >nul 2>&1')
    # Bước 2: Đợi app thoát và file được unlock
    wait_file_unlocked(app_exe, timeout=60)
    # Bước 2: Giải nén file zip vào thư mục app
    if not os.path.exists(args.zip):
        print("❌ Không tìm thấy file zip.")
        exit(1)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            if zip_password:
                zip_ref.extractall(args.dir, pwd=zip_password.encode('utf-8'))
            else:
                zip_ref.extractall(args.dir)
        # Xóa file zip
        print("✅ Đã giải nén gói cập nhật.")
    
    except RuntimeError:
        print("❌ Mật khẩu không đúng hoặc file zip bị lỗi.")
    except Exception as e:
        print(f"⚠️ Lỗi khi giải nén: {e}")
    os.remove(zip_path)
    print(f"🗑️ Đã xóa file cập nhật: {args.zip}")
    # # 4) Khởi chạy lại app
    if args.restart:
        creationflags = 0x00000008 if sys.platform.startswith("win") else 0  # DETACHED_PROCESS
        subprocess.Popen([app_exe], close_fds=True, creationflags=creationflags)

if __name__ == "__main__":
    main()
# pyinstaller --onefile --name update_tool update_tool.py
 # python update_tool.py --app "C:\Users\HT\Desktop\New_folder\DownloadVID.exe" --zip "C:\Users\HT\Desktop\New_folder\MyApp-v1.3.0.zip" --dir "C:\Users\HT\Desktop\New_folder" --restart
# update_tool.exe --app "C:\Users\HT\Desktop\New_folder\DownloadVID.exe" --zip "C:\Users\HT\Desktop\New_folder\MyApp-v1.3.0.zip" --dir "C:\Users\HT\Desktop\New_folder" --restart
