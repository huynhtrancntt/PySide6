@REM Set-Alias run .\run.bat

@echo off
@chcp 65001 >nul
setlocal

echo 🔍 Đang kiểm tra môi trường ảo...

if not exist venv (
    echo ❗ Chưa có môi trường ảo. Đang tạo venv...
    python -m venv venv
)

if exist venv\Scripts\activate.bat (
    echo ✅ Kích hoạt môi trường ảo...
    call venv\Scripts\activate.bat
) else (
    echo ❌ Không tìm thấy file kích hoạt môi trường.
    exit /b 1
)

cmd