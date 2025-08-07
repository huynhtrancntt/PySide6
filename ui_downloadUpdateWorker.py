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

    def __init__(self, download_url, version):
        super().__init__()
        self.download_url = download_url
        self.version = version
        self.stop_flag = False

    def run(self):
        """Thực hiện download và extract"""
        try:
            # Tạo tên file
            output_file = f"update_v{self.version}.zip"
            extract_to = "temp_update"

            # Bước 1: Download file
            self.message_signal.emit("⬇️ Đang tải file cập nhật...")
            if not self._download_with_progress(self.download_url, output_file):
                return

            if self.stop_flag:
                self._cleanup(output_file, extract_to)
                return

            # Bước 2: Giải nén file
            self.message_signal.emit("📦 Đang giải nén file...")
            if not self._extract_and_install(output_file, extract_to):
                return

            if self.stop_flag:
                self._cleanup(output_file, extract_to)
                return

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

    def _extract_and_install(self, zip_file, extract_to):
        """Giải nén và cài đặt cập nhật"""
        try:
            # Xóa thư mục tạm cũ nếu có
            if os.path.exists(extract_to):
                shutil.rmtree(extract_to)
            os.makedirs(extract_to)

            # Giải nén
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                total_files = len(file_list)

                for i, file_name in enumerate(file_list):
                    if self.stop_flag:
                        # Xóa thư mục extract và file zip
                        self._cleanup(zip_file, extract_to)
                        return False

                    zip_ref.extract(file_name, extract_to)
                    # 50% cho extract (từ 50% đến 100%)
                    percent = 0 + int((i + 1) / total_files * 100)
                    self.progress_signal.emit(percent)
                    self.message_signal.emit(f"📦 Giải nén: {file_name}")

            # Copy files
            self.message_signal.emit("📋 Đang cập nhật files...")
            current_dir = os.getcwd()

            copied_files = []
            for root, dirs, files in os.walk(extract_to):
                for file in files:
                    if self.stop_flag:
                        # Xóa thư mục extract và file zip
                        self._cleanup(zip_file, extract_to)
                        return False

                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(src_file, extract_to)
                    dst_file = os.path.join(current_dir, rel_path)

                    # Tạo thư mục đích nếu chưa có
                    dst_dir = os.path.dirname(dst_file)
                    if dst_dir and not os.path.exists(dst_dir):
                        os.makedirs(dst_dir)

                    # Copy file
                    shutil.copy2(src_file, dst_file)
                    copied_files.append(rel_path)
                    self.message_signal.emit(f"📋 Cập nhật: {rel_path}")

            # Lưu phiên bản mới vào file
            # try:
            #     version_file = os.path.join(current_dir, "version.txt")
            #     with open(version_file, 'w', encoding='utf-8') as f:
            #         f.write(self.version)
            #     self.message_signal.emit(
            #         f"💾 Đã lưu phiên bản mới: {self.version}")
            # except Exception as e:
            #     self.message_signal.emit(f"⚠️ Không thể lưu phiên bản: {e}")

            # Dọn dẹp - xóa file zip và thư mục extract
            self.message_signal.emit("🧹 Đang dọn dẹp...")
            self._cleanup(zip_file, extract_to)

            self.progress_signal.emit(100)
            self.message_signal.emit(
                f"✅ Đã cập nhật {len(copied_files)} files")
            self.message_signal.emit(
                "🎉 Cập nhật hoàn tất! Ứng dụng sẽ khởi động lại...")
            return True

        except Exception as e:
            self.message_signal.emit(f"❌ Lỗi giải nén: {str(e)}")
            # Xóa file zip và thư mục extract khi có lỗi
            self._cleanup(zip_file, extract_to)
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
