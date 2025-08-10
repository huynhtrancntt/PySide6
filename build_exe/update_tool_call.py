from update_tool import Updater  # nếu file là updater_stub.py

# Tạo đối tượng updater
app_path = r"C:\Users\HT\Desktop\New_folder\DownloadVID.exe"
zip_path = r"C:\Users\HT\Desktop\New_folder\MyApp-v1.3.0.zip"
app_dir = r"C:\Users\HT\Desktop\New_folder"
u = Updater(
    app_path=app_path,
    zip_path=zip_path,
    app_dir=app_dir,
    restart=True,
    zip_password="123456"
)

# Chạy cập nhật
u.run()
