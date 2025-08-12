import os
import shutil
import subprocess
import sys

# ==== Cấu hình ====
APP_NAME = "HTDownloader"
MAIN_FILE = "app.py"
OBF_DIR = "obf_src"
RESOURCE_DIRS = ["images", "assets", "data"]
RESOURCE_FILES = ["Update.exe"]
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join("images", "icon.ico")

RESOURCE_FILES_PY = [
    "ui_setting.py", "downloadWorker.py", "ui_updatedialog.py",
    "ui_checkupdate.py", "ui_downloadUpdateWorker.py", "license_manager.py"
]

IMPORT_HIDDEN = [
    'subprocess', 'requests', 'webbrowser', 'Cryptodome.Cipher.AES',
    'PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui'
]

MPRESS_PATH = r"C:\tools\mpress\mpress.exe"  # nếu không dùng thì để None


def run_cmd(cmd):
    print(f"▶ {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        sys.exit(f"❌ Lỗi khi chạy: {cmd}")


def clean_old_builds():
    for folder in [OBF_DIR, "dist", "build"]:
        folder_path = os.path.join(PROJECT_DIR, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"🧹 Đã xoá {folder_path}")


def encrypt_code():
    cmd = f"pyarmor gen -O {OBF_DIR} {MAIN_FILE} " + \
        " ".join(RESOURCE_FILES_PY)
    run_cmd(cmd)
    print("✅ Hoàn tất! Mã hoá code Python bằng PyArmor")


def copy_resources_into_obf():
    obf_abs = os.path.join(PROJECT_DIR, OBF_DIR)
    os.makedirs(obf_abs, exist_ok=True)

    for res_dir in RESOURCE_DIRS:
        src_dir = os.path.join(PROJECT_DIR, res_dir)
        dst_dir = os.path.join(obf_abs, res_dir)
        if os.path.isdir(src_dir):
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)
            print(f"📁 Đã copy thư mục tài nguyên: {res_dir}")

    for res_file in RESOURCE_FILES:
        src_file = os.path.join(PROJECT_DIR, res_file)
        dst_file = os.path.join(obf_abs, res_file)
        if os.path.isfile(src_file):
            shutil.copy2(src_file, dst_file)
            print(f"📄 Đã copy file tài nguyên: {res_file}")


def build_exe_with_nuitka():
    copy_resources_into_obf()

    add_data_args = []
    for res_dir in RESOURCE_DIRS:
        src_path = os.path.join(OBF_DIR, res_dir)
        if os.path.exists(src_path):
            add_data_args.append(f'--include-data-dir={src_path}={res_dir}')

    for res_file in RESOURCE_FILES:
        src_path = os.path.join(OBF_DIR, res_file)
        if os.path.exists(src_path):
            add_data_args.append(f'--include-data-file={src_path}={res_file}')

    for res_file_py in RESOURCE_FILES_PY:
        module_name = os.path.splitext(res_file_py)[0]
        add_data_args.append(f'--include-module={module_name}')

    for hidden in IMPORT_HIDDEN:
        add_data_args.append(f'--include-module={hidden}')

    icon_arg = f'--windows-icon-from-ico="{ICON_PATH}"' if os.path.exists(
        ICON_PATH) else ""

    cmd = (
        f'python -m nuitka --onefile --windows-disable-console '
        f'--output-filename={APP_NAME}.exe '
        f'{icon_arg} '
        f'{" ".join(add_data_args)} '
        f'{os.path.join(OBF_DIR, MAIN_FILE)}'
    )

    run_cmd(cmd)
    print("✅ Hoàn tất build EXE bằng Nuitka")


def compress_with_mpress():
    exe_path = os.path.join(PROJECT_DIR, f"{APP_NAME}.exe")
    if MPRESS_PATH and os.path.isfile(MPRESS_PATH) and os.path.exists(exe_path):
        cmd = f'"{MPRESS_PATH}" -s -q "{exe_path}"'
        run_cmd(cmd)
        print("✅ Đã nén exe bằng MPRESS")
    else:
        print("⚠ MPRESS không khả dụng, bỏ qua bước nén.")


if __name__ == "__main__":
    clean_old_builds()
    encrypt_code()
    build_exe_with_nuitka()
    # compress_with_mpress()
    print(f"✅ Hoàn tất! File EXE: {APP_NAME}.exe")
