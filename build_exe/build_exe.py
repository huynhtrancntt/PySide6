import os
import shutil
import subprocess
import sys

# ==== Cấu hình ====
APP_NAME = "HTDownloader"
MAIN_FILE = "yt_ui_downloader.py"       # File entry point
OBF_DIR = "obf_src"                     # Thư mục output mã hoá
RESOURCE_DIRS = ["images", "assets", "data"]  # Thư mục tài nguyên cần gom
RESOURCE_FILES = ["down-arrow.png", "yt-dlp.exe",
                  "ffmpeg.exe"]  # File lẻ cần gom
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
UPX_PATH = fr"D:\Dev\python\upx-5.0.2-win64\upx.exe"  # đường dẫn file upx.ex


def run_cmd(cmd):
    """Chạy lệnh và in log"""
    print(f"▶ {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        sys.exit(f"❌ Lỗi khi chạy: {cmd}")


def clean_old_builds():
    """Xoá build cũ"""
    for folder in [OBF_DIR, "dist", "build"]:
        folder_path = os.path.join(PROJECT_DIR, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"🧹 Đã xoá {folder_path}")


def encrypt_code():
    """Mã hoá code Python bằng PyArmor"""
    os.chdir(PROJECT_DIR)
    run_cmd(f"pyarmor gen -O {OBF_DIR} {MAIN_FILE} ui_setting.py")


def copy_resources_into_obf():
    """Copy resource directories/files sang thư mục obfuscate để PyInstaller gom được"""
    obf_abs = os.path.join(PROJECT_DIR, OBF_DIR)
    os.makedirs(obf_abs, exist_ok=True)

    # Copy thư mục
    for res_dir in RESOURCE_DIRS:
        src_dir = os.path.join(PROJECT_DIR, res_dir)
        dst_dir = os.path.join(obf_abs, res_dir)
        if os.path.isdir(src_dir):
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)
            print(f"📁 Đã copy thư mục tài nguyên: {res_dir}")

    # Copy file lẻ
    for res_file in RESOURCE_FILES:
        src_file = os.path.join(PROJECT_DIR, res_file)
        dst_file = os.path.join(obf_abs, res_file)
        if os.path.isfile(src_file):
            shutil.copy2(src_file, dst_file)
            print(f"📄 Đã copy file tài nguyên: {res_file}")


def build_exe():
    """Build exe với PyInstaller và gom tài nguyên"""
    copy_resources_into_obf()

    add_data_args = []

    # Gom thư mục tài nguyên
    for res_dir in RESOURCE_DIRS:
        src_path = os.path.join(OBF_DIR, res_dir)
        if os.path.exists(src_path):
            add_data_args.append(
                f'--add-data "{res_dir}{os.pathsep}{res_dir}"')
            print(f"➕ Sẽ gom thư mục: {res_dir}")

    # Gom file lẻ
    for res_file in RESOURCE_FILES:
        src_path = os.path.join(OBF_DIR, res_file)
        if os.path.exists(src_path):
            add_data_args.append(
                f'--add-data "{res_file}{os.pathsep}{res_file}"')
            print(f"➕ Sẽ gom file: {res_file}")

    # Hidden imports
    add_data_args += [
        '--add-data=yt-dlp.exe;yt-dlp.exe',
        '--add-data=ffmpeg.exe;ffmpeg.exe',
        '--hidden-import=ui_setting',
        '--hidden-import=subprocess',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=PySide6.QtGui',
        # '--collect-submodules PySide6.QtCore'
        # '--collect-submodules PySide6.QtWidgets'
        # '--collect-submodules PySide6.QtGui'
        # '--hidden-import=PySide6.QtGui',
        # '--collect-all PySide6'
    ]

    # Build
    cmd = (
        f'cd {OBF_DIR} && '
        f'pyinstaller --onedir --noconsole --noconfirm --clean '
        # f'pyinstaller --onefile --noconsole --noconfirm --clean '
        # f'pyinstaller  --noconsole --noconfirm --clean '
        f'--name {APP_NAME} '
        f'{" ".join(add_data_args)} '
        f'{MAIN_FILE}'
    )
    run_cmd(cmd)


def compress_with_upx():
    """Nén exe bằng UPX nếu có"""
    exe_name = os.path.splitext(
        APP_NAME)[0] + (".exe" if os.name == "nt" else "")
    exe_path = os.path.join(PROJECT_DIR, OBF_DIR, "dist", exe_name)

    print(f"⚠ exe_name: {exe_name}")
    print(f"⚠ exe_path: {exe_path}")

    if os.path.exists(exe_path):
        # if shutil.which("upx"):
        if os.path.isfile(UPX_PATH):
            # cmd = f'upx --best --lzma --force "{exe_path}"'
            cmd = f'"{UPX_PATH}" --best --lzma --force "{exe_path}"'
            run_cmd(cmd)
            print("✅ Hoàn tất! File EXE đã được nén với UPX thành công")
            # Copy sang thư mục dist ngoài cùng
            final_dist_dir = os.path.join(PROJECT_DIR, "dist")
            os.makedirs(final_dist_dir, exist_ok=True)
            final_exe_path = os.path.join(final_dist_dir, exe_name)
            shutil.copy2(exe_path, final_exe_path)

            # Lấy dung lượng (MB)
            size_mb = os.path.getsize(final_exe_path) / (1024 * 1024)
            print(
                f"📦 File cuối: {exe_name} — {size_mb:.2f} MB — {final_exe_path}")
        else:
            print("⚠ UPX chưa được cài hoặc không có trong PATH, bỏ qua bước nén.")
    else:
        print("❌ Không tìm thấy file EXE để nén.")


if __name__ == "__main__":
    clean_old_builds()
    encrypt_code()
    build_exe()
    compress_with_upx()
    print(f"✅ Hoàn tất! File EXE nằm ở: {OBF_DIR}/dist")
