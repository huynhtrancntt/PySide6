import os

import shutil
import zipfile
import requests
from PySide6.QtCore import QThread, Signal


class DownloadUpdateWorker(QThread):
    """Worker thread để tải về và giải nén update"""
    progress_signal = Signal(int)
    message_signal = Signal(str)
    finished_signal = Signal(bool, str)  # success, message

    def __init__(self, download_url, version, zip_path):
        super().__init__()
        self.download_url = download_url
        self.version = version
        self.stop_flag = False
        self.zip_path = zip_path

    def run(self):
        """Thực hiện download và extract"""

        try:
            # Ghép đường dẫn file zip
            # Tạo tên file
            if not self.zip_path:
                self.zip_path = f"{self.version}.zip"

            # output_file = f"update_v{self.version}.zip"
            # # extract_to = "temp_update"
            # output_file = rf"C:\Users\HT\Desktop\Test_Update\update_v{self.version}.zip"
            # Bước 1: Download file
            self.message_signal.emit("⬇️ Đang tải file cập nhật...")
            # print("Start download and extract")
            if not self._download_with_progress(self.download_url, self.zip_path):
                return

            # if self.stop_flag:
            #     self._cleanup(output_file, extract_to)
            #     return

            # # Bước 2: Giải nén file
            # self.message_signal.emit("📦 Đang giải nén file...")
            # if not self._extract_and_install(output_file, extract_to):
            #     return

            # if self.stop_flag:
            #     self._cleanup(output_file, extract_to)
            #     return

            # Bước 3: Hoàn thành
            self.message_signal.emit("✅ Cập nhật hoàn tất!")
            self.progress_signal.emit(100)
            self.finished_signal.emit(
                True, f"Cập nhật thành công! Ứng dụng sẽ khởi động lại.")

        except Exception as e:
            self.finished_signal.emit(False, f"Lỗi cập nhật: {str(e)}")

    def _download_with_progress(self, url, output_file):
        """Tải file với thanh tiến trình"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            total_mb = total_size / (1024 * 1024)

            downloaded = 0
            chunk_size = 1024 * 1024  # 1MB

            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if self.stop_flag:
                        f.close()
                        self.message_signal.emit("⏹ Đã dừng tải")
                        return False

                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        downloaded_mb = downloaded / (1024 * 1024)

                        if total_mb > 0:
                            # 50% cho download
                            percent = int((downloaded_mb / total_mb) * 100)
                            self.progress_signal.emit(percent)
                            self.message_signal.emit(
                                f"⬇️ Đang tải: {downloaded_mb:.1f}/{total_mb:.1f} MB ({percent}%)")
                        else:
                            self.message_signal.emit(
                                f"⬇️ Đã tải: {downloaded_mb:.1f} MB")

            self.message_signal.emit("✅ Tải xuống hoàn tất!")
            return True

        except Exception as e:
            self.message_signal.emit(f"❌ Lỗi tải xuống: {str(e)}")
            return False

    def _cleanup(self, zip_file, extract_to):
        """Dọn dẹp files tạm"""
        try:
            # Xóa file zip
            if os.path.exists(zip_file):
                os.remove(zip_file)
                self.message_signal.emit(
                    f"🗑️ Đã xóa file: {os.path.basename(zip_file)}")

            # Xóa thư mục extract
            if os.path.exists(extract_to):
                shutil.rmtree(extract_to)
                self.message_signal.emit("🗑️ Đã xóa thư mục tạm")
        except Exception as e:
            self.message_signal.emit(f"⚠️ Lỗi khi dọn dẹp: {e}")

    def stop(self):
        """Dừng quá trình download"""
        self.stop_flag = True
