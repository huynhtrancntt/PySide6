@echo off
@chcp 65001 >nul
setlocal

echo 🔍 Đang kiểm tra môi trường ảo...

if not exist env (
    echo ❗ Chưa có môi trường ảo. Đang tạo venv...
    python -m venv env
)

if exist env\Scripts\activate.bat (
    echo ✅ Kích hoạt môi trường ảo...
    call env\Scripts\activate.bat
	
) else (
    echo ❌ Không tìm thấy file kích hoạt môi trường.
    exit /b 1
)

python app.py
cmd