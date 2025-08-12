import os
import shutil
import subprocess
import sys
from pathlib import Path

# ==== Cấu hình ====
APP_NAME = "HTDownloader"
MAIN_FILE = "app.py"                     # Entry point
RESOURCE_DIRS = []                       # Thư mục tài nguyên (src=dst)
RESOURCE_FILES = []                      # File lẻ ở root dự án (src=dst)
ICON_PATH = Path("images/icon.ico")
# để trống nếu không dùng
UPX_PATH = Path(r"D:\Dev\python\upx-5.0.2-win64\upx.exe")

# Nếu bạn dùng pycryptodomex -> 'Cryptodome.*'
# Nếu bạn dùng pycryptodome  -> 'Crypto.*'
HIDDEN_MODULES = [
    "subprocess", "requests", "webbrowser", "uuid",
    "PySide6.QtCore", "PySide6.QtWidgets", "PySide6.QtGui",
    "Cryptodome.Cipher.AES",
]

# Các file chắc chắn phải có trong gói (src_rel, dst_rel)
EXTRA_FILES = [
    ("data/yt-dlp.exe", "data/yt-dlp.exe"),
    ("data/ffmpeg.exe", "data/ffmpeg.exe"),
    ("images/icon.ico", "images/icon.ico"),
]

# ==== Đường dẫn chuẩn ====
PROJECT_DIR = Path(__file__).resolve().parent
BUILD_DIR = PROJECT_DIR / "build_onedir"
DIST_DIR = PROJECT_DIR / "dist"
DIST_DIR.mkdir(exist_ok=True)


def run_cmd(args, cwd=None, check=True):
    print("▶", " ".join(map(str, args)))
    r = subprocess.run(args, cwd=cwd)
    if check and r.returncode != 0:
        sys.exit(r.returncode)


def ensure_tools():
    run_cmd([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run_cmd([sys.executable, "-m", "pip", "install",
             "--upgrade", "nuitka", "ordered-set", "zstandard"])


def clean_old_builds():
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print(f"🧹 Đã xoá {BUILD_DIR}")
    out_dir = DIST_DIR / APP_NAME
    if out_dir.exists():
        shutil.rmtree(out_dir)
        print(f"🧹 Đã xoá {out_dir}")
    DIST_DIR.mkdir(exist_ok=True)


def build_with_nuitka():
    cmd = [
        sys.executable, "-m", "nuitka",
        MAIN_FILE,
        "--standalone",                   # build onedir
        "--output-dir=" + str(BUILD_DIR),
        f"--output-filename={APP_NAME}.exe",
        "--assume-yes-for-downloads",
        "--nofollow-import-to=pytest",
        "--remove-output",
        "--enable-plugin=pyside6",        # PySide6
        "--windows-console-mode=disable",  # ẩn console
    ]

    # Icon
    if ICON_PATH and ICON_PATH.is_file():
        cmd.append(f"--windows-icon-from-ico={ICON_PATH}")
    else:
        print("⚠ Không thấy icon, bỏ qua.")

    # Hidden modules
    for m in HIDDEN_MODULES:
        cmd.append(f"--include-module={m}")

    # Thư mục tài nguyên
    for d in RESOURCE_DIRS:
        src = PROJECT_DIR / d
        if src.is_dir():
            cmd.append(f"--include-data-dir={src}={d}")
            print(f"➕ include dir: {src} -> {d}")

    # File lẻ ở root
    for f in RESOURCE_FILES:
        src = PROJECT_DIR / f
        if src.is_file():
            cmd.append(f"--include-data-files={src}={f}")
            print(f"➕ include file: {src} -> {f}")

    # File bắt buộc (.exe, icon, …)
    for src_rel, dst_rel in EXTRA_FILES:
        src_abs = PROJECT_DIR / src_rel
        if not src_abs.exists():
            print(f"⚠ Bỏ qua (không thấy): {src_abs}")
            continue
        cmd.append(f"--include-data-files={src_abs}={dst_rel}")
        print(f"🧩 include file: {src_abs} -> {dst_rel}")

    # assets.txt (nếu có)
    assets_file = PROJECT_DIR / "assets.txt"
    if assets_file.is_file():
        for raw in assets_file.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                src_rel2, dst_rel2 = map(str.strip, line.split("=", 1))
            else:
                src_rel2, dst_rel2 = line, line
            src_abs2 = PROJECT_DIR / src_rel2
            if src_abs2.is_file():
                cmd.append(f"--include-data-files={src_abs2}={dst_rel2}")
                print(f"🧩 include (assets file): {src_abs2} -> {dst_rel2}")
            elif src_abs2.is_dir():
                cmd.append(f"--include-data-dir={src_abs2}={dst_rel2}")
                print(f"🧩 include (assets dir):  {src_abs2} -> {dst_rel2}")

    run_cmd(cmd)


def compress_with_upx_in_dir(target_dir: Path):
    """Nén tất cả file .exe và .pyd trong thư mục build bằng UPX"""
    upx = None
    if str(UPX_PATH):
        p = Path(UPX_PATH)
        if p.is_file():
            upx = str(p)
    if not upx:
        found = shutil.which("upx")
        if found:
            upx = found

    if not upx:
        print("⚠ Không tìm thấy UPX, bỏ qua nén.")
        return

    for file in target_dir.rglob("*"):
        if file.suffix.lower() in [".exe", ".pyd", ".dll"]:
            run_cmd([upx, "--best", "--lzma", "--force", str(file)])
    print("✅ Đã nén toàn bộ exe/pyd/dll với UPX")


def copy_final_to_dist():
    """Copy cả thư mục onedir sang dist/"""
    build_out = BUILD_DIR / APP_NAME.dist_suffixless
    # với Nuitka onedir, thư mục output nằm trong BUILD_DIR, tên trùng APP_NAME + ".dist"
    for sub in BUILD_DIR.iterdir():
        if sub.is_dir() and sub.name.startswith(APP_NAME):
            build_out = sub
            break

    final_dir = DIST_DIR / APP_NAME
    if final_dir.exists():
        shutil.rmtree(final_dir)
    shutil.copytree(build_out, final_dir)
    print(f"📦 Thư mục cuối: {final_dir}")


if __name__ == "__main__":
    # ensure_tools()   # bật nếu muốn auto-cài lib build
    clean_old_builds()
    build_with_nuitka()
    # compress_with_upx_in_dir(BUILD_DIR)   # nếu muốn nén
    copy_final_to_dist()
    print("✅ Xong! Xem thư mục dist/ để lấy bản build")
