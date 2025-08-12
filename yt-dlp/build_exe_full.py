import os
import shutil
import subprocess
import sys
from pathlib import Path

# ==== Cấu hình ====
APP_NAME = "HTDownloader"
MAIN_FILE = "app.py"  # Entry point
OBF_DIR = "obf_src"
RESOURCE_DIRS = ["images", "assets", "data"]
RESOURCE_FILES = ["Update.exe"]
ICON_PATH = Path("images/icon.ico")
# hoặc để rỗng để auto-detect
UPX_PATH = Path(r"D:\Dev\python\upx-5.0.2-win64\upx.exe")

RESOURCE_FILES_PY = [
    "ui_setting.py", "downloadWorker.py", "ui_updatedialog.py",
    "ui_checkupdate.py", "ui_downloadUpdateWorker.py", "license_utils.py"
]

# Nếu bạn dùng pycryptodomex -> 'Cryptodome.*'
# Nếu bạn dùng pycryptodome  -> 'Crypto.*'
IMPORT_HIDDEN = [
    "subprocess", "requests", "webbrowser", "Cryptodome.Cipher.AES",
    "PySide6.QtCore", "PySide6.QtWidgets", "PySide6.QtGui", "uuid"
]

PROJECT_DIR = Path(__file__).resolve().parent


def run_cmd(args, cwd=None, check=True):
    """Chạy lệnh (list args), an toàn khoảng trắng."""
    print("▶", " ".join(map(str, args)))
    result = subprocess.run(args, cwd=cwd)
    if check and result.returncode != 0:
        sys.exit(f"❌ Lỗi khi chạy: {' '.join(map(str, args))}")


def ensure_tools():
    """Cài đặt công cụ nếu thiếu."""
    run_cmd([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run_cmd([sys.executable, "-m", "pip", "install",
            "--upgrade", "pyinstaller>=6.6", "pyarmor>=8.5"])


def clean_old_builds():
    """Xoá build cũ."""
    for folder in [OBF_DIR, "dist", "build"]:
        p = PROJECT_DIR / folder
        if p.exists():
            shutil.rmtree(p)
            print(f"🧹 Đã xoá {p}")


def encrypt_code():
    """Mã hoá code Python bằng PyArmor."""
    obf_dir = PROJECT_DIR / OBF_DIR
    if obf_dir.exists():
        shutil.rmtree(obf_dir)
    obf_dir.mkdir(parents=True, exist_ok=True)

    # PyArmor 8.x: 'gen' + danh sách file. Thêm '-r' nếu muốn đệ quy theo import.
    args = ["pyarmor", "gen", "-O", str(obf_dir), MAIN_FILE]
    args.extend(RESOURCE_FILES_PY)
    # args.insert(2, "-r")  # bật nếu cần recursive
    run_cmd(args)
    print("✅ Hoàn tất! Mã hoá code bằng PyArmor")


def copy_resources_into_obf():
    """Copy tài nguyên vào obf_src để PyInstaller gom."""
    obf_abs = PROJECT_DIR / OBF_DIR
    obf_abs.mkdir(exist_ok=True)

    for res_dir in RESOURCE_DIRS:
        src = PROJECT_DIR / res_dir
        dst = obf_abs / res_dir
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"📁 Đã copy thư mục tài nguyên: {res_dir}")

    for res_file in RESOURCE_FILES:
        src = PROJECT_DIR / res_file
        dst = obf_abs / res_file
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"📄 Đã copy file tài nguyên: {res_file}")


def build_exe():
    """Build exe với PyInstaller (CWD=obf_src)."""
    copy_resources_into_obf()
    obf_abs = PROJECT_DIR / OBF_DIR

    py_args = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--noconfirm",
        "--clean",
        "--name", APP_NAME,
    ]

    # Icon (icon đã được copy sang obf_src/images)
    obf_icon = obf_abs / ICON_PATH
    if obf_icon.is_file():
        py_args += ["--icon", str(obf_icon)]
    else:
        print("⚠ Không tìm thấy icon, bỏ qua.")

    # Add data: dùng đường dẫn tương đối tính từ obf_src
    for res_dir in RESOURCE_DIRS:
        if (obf_abs / res_dir).exists():
            # format Windows: "src;dst"
            py_args += ["--add-data", f"{res_dir};{res_dir}"]
            print(f"➕ Sẽ gom thư mục: {res_dir}")

    for res_file in RESOURCE_FILES:
        if (obf_abs / res_file).exists():
            py_args += ["--add-data", f"{res_file};{res_file}"]
            print(f"➕ Sẽ gom file: {res_file}")

    # Hidden-import từ file .py (đã obfuscate)
    for res_py in RESOURCE_FILES_PY:
        mod = Path(res_py).stem
        if (obf_abs / f"{mod}.py").exists():
            py_args += ["--hidden-import", mod]
            print(f"➕ Hidden-import: {mod}")

    # Các hidden import bạn khai báo sẵn
    for h in IMPORT_HIDDEN:
        py_args += ["--hidden-import", h]

    # Entry (đã obfuscate) nằm trong obf_src
    entry_in_obf = obf_abs / MAIN_FILE
    if not entry_in_obf.exists():
        sys.exit(f"❌ Không tìm thấy entry đã mã hoá: {entry_in_obf}")

    py_args.append(str(entry_in_obf))

    # Chạy PyInstaller với cwd=obf_src (không cần cd &&)
    run_cmd(py_args, cwd=str(obf_abs))


def compress_with_upx():
    """Nén exe bằng UPX nếu có."""
    obf_dist = PROJECT_DIR / OBF_DIR / "dist"
    exe_name = APP_NAME + (".exe" if os.name == "nt" else "")
    exe_path = obf_dist / exe_name

    print(f"⚠ exe_name: {exe_name}")
    print(f"⚠ exe_path: {exe_path}")

    if not exe_path.exists():
        print("❌ Không tìm thấy file EXE để nén.")
        return

    # Ưu tiên đường dẫn cấu hình, nếu không có thì which
    upx = None
    if UPX_PATH and UPX_PATH.is_file():
        upx = str(UPX_PATH)
    else:
        found = shutil.which("upx")
        if found:
            upx = found

    if upx:
        run_cmd([upx, "--best", "--lzma", "--force", str(exe_path)])
        print("✅ Đã nén với UPX")

    # Copy sang dist ngoài cùng
    final_dist = PROJECT_DIR / "dist"
    final_dist.mkdir(exist_ok=True)
    final_exe = final_dist / exe_name
    shutil.copy2(exe_path, final_exe)

    size_mb = final_exe.stat().st_size / (1024 * 1024)
    print(f"📦 File cuối: {final_exe} — {size_mb:.2f} MB")


if __name__ == "__main__":
    # ensure_tools()
    clean_old_builds()
    encrypt_code()
    build_exe()
    compress_with_upx()
    print("✅ Hoàn tất! File EXE nằm ở: dist")
