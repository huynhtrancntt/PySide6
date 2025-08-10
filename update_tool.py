import os
import sys
import time
import zipfile
import shutil
import subprocess


class Updater:
    def __init__(self, app_path, zip_path, app_dir, restart=False, zip_password=None):
        self.app_path = os.path.abspath(app_path)
        self.zip_path = os.path.abspath(zip_path)
        self.app_dir = os.path.abspath(app_dir)
        self.restart = restart
        self.zip_password = zip_password
        self.app_name = os.path.basename(self.app_path)

    def wait_file_unlocked(self, path, timeout=30):
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

    def kill_app(self):
        os.system(f'taskkill /f /im "{self.app_name}" >nul 2>&1')
        self.wait_file_unlocked(self.app_path, timeout=60)

    def extract_zip(self):
        if not os.path.isfile(self.zip_path):
            print("❌ Không tìm thấy file zip.")
            return False
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                if self.zip_password:
                    zip_ref.extractall(
                        self.app_dir, pwd=self.zip_password.encode('utf-8'))
                else:
                    zip_ref.extractall(self.app_dir)
            print("✅ Đã giải nén gói cập nhật.")
            return True
        except RuntimeError:
            print("❌ Mật khẩu không đúng hoặc file zip bị lỗi.")
        except Exception as e:
            print(f"⚠️ Lỗi khi giải nén: {e}")
        return False

    def remove_zip(self):
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
            print(f"🗑️ Đã xóa file: {self.zip_path}")

    def restart_app(self):
        if self.restart:
            creationflags = 0x00000008 if sys.platform.startswith("win") else 0
            subprocess.Popen([self.app_path], close_fds=True,
                             creationflags=creationflags)
            print(f"🚀 Đã khởi động lại {self.app_name}")

    def run(self):
        current_exe_path = sys.executable
        print("Đang chạy file:", current_exe_path)
        print(f"📌 App: {self.app_path}")
        print(f"📌 Zip: {self.zip_path}")
        print(f"📌 Dir: {self.app_dir}")
        print(f"📌 Restart: {self.restart}")

        self.kill_app()
        if self.extract_zip():
            self.remove_zip()
        self.restart_app()


if __name__ == "__main__":
    app_path = r"D:\Dev\python\PySide6\dist\TTSApp.exe"
    zip_path = r"D:\Dev\python\PySide6\dist\update_v1.6.0.zip"
    app_dir = r"D:\Dev\python\PySide6\dist"
    restart = True
    zip_password = "123456"
    u = Updater(
        app_path=app_path,
        zip_path=zip_path,
        app_dir=app_dir,
        restart=restart,
        zip_password=zip_password
    )
    u.run()

# python update_tool.py --app "C:\Users\HT\Desktop\New_folder\DownloadVID.exe" --zip "C:\Users\HT\Desktop\New_folder\MyApp-v1.3.0.zip" --dir "C:\Users\HT\Desktop\New_folder" --restart
# pyinstaller --onefile --name update update_tool.py
# update.exe --app "C:\Users\HT\Desktop\New_folder\DownloadVID.exe" --zip "C:\Users\HT\Desktop\New_folder\MyApp-v1.3.0.zip" --dir "C:\Users\HT\Desktop\New_folder" --restart
