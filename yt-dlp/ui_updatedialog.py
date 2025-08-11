

import os
import sys
import subprocess
import webbrowser

from ui_downloadUpdateWorker import DownloadUpdateWorker
from ui_setting import _init_addStyle, resource_path, APP_VERSION
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox,
    QProgressBar, QHBoxLayout, QFrame
)


class UI_UpdateDialog(QDialog):
    """Dialog hiển thị thông tin update"""

    def __init__(self, update_info, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.download_worker = None
        self.init_ui()

    def init_ui(self):
        """Khởi tạo giao diện dialog"""
        self.setWindowTitle("🎉 Cập nhật có sẵn")
        # self.setMinimumWidth(600)
        # self.setMinimumHeight(500)

        layout = QVBoxLayout()
        self.setLayout(layout)
        _init_addStyle(self)
        version_box = QFrame()
        version_box.setObjectName("versionBox")
        version_layout = QVBoxLayout(version_box)

        version_label = QLabel(
            f"<b>🎉 Cập nhật phiên bản mới v{self.update_info['version']}</b>")
        version_label.setStyleSheet("color: #05df60; font-size: 16px;")
        version_old = QLabel(
            f"<span>📱 Phiên bản hiện tại: v{APP_VERSION}</span>")

        version_layout.addWidget(version_label)
        version_layout.addWidget(version_old)
        if self.update_info.get('name'):
            version_name = QLabel(
                f"<span>📋 Tên phiên bản: {self.update_info['name']}")
            version_layout.addWidget(version_name)
            # Ngày phát hành
        if self.update_info.get('published_at'):
            try:
                from datetime import datetime
                pub_date = datetime.fromisoformat(
                    self.update_info['published_at'].replace('Z', '+00:00'))
                date_str = pub_date.strftime("%d/%m/%Y %H:%M")
                date_label = QLabel(
                    f"<span>📅 Ngày phát hành: {date_str}</span>")
                version_layout.addWidget(date_label)
            except:
                pass

        buttons = QHBoxLayout()
        auto_download_button = QPushButton("🚀 Cài đặt tự động")
        auto_download_button.setObjectName("autoDownloadBtn")
        auto_download_button.clicked.connect(self.start_auto_download)
        btn_install_manual = QPushButton("🔗 Tải về thủ công")
        btn_install_manual.setObjectName("manualDownloadBtn")
        btn_install_manual.clicked.connect(self.download_update)
        btn_skip = QPushButton("⏰ Để sau")
        btn_skip.setObjectName("skipBtn")
        btn_skip.clicked.connect(self.reject)
        buttons.addWidget(auto_download_button)
        buttons.addWidget(btn_install_manual)
        buttons.addWidget(btn_skip)
        version_layout.addLayout(buttons)

        layout.addWidget(version_box)

        # Release notes
        if self.update_info.get('notes'):
            notes_label = QLabel("📝 Ghi chú phiên bản:")
            notes_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
            layout.addWidget(notes_label)

            notes_text = QTextEdit()
            notes_text.setPlainText(self.update_info['notes'])
            notes_text.setReadOnly(True)
            notes_text.setMaximumHeight(120)
            layout.addWidget(notes_text)
        self.update_progress_bar = QProgressBar()
        self.update_progress_bar.setVisible(True)
        layout.addStretch()
        layout.addWidget(self.update_progress_bar)
        # self.update_status_label = QLabel("Checking for updates...")
        # self.update_status_label.setStyleSheet("color: #05df60;")
        # self.update_status_label.setVisible(True)

    def start_auto_download(self):
        """Bắt đầu tải về tự động"""
        # Kiểm tra xem có URL download không
        if not self.update_info.get('download_url'):
            # self.add_log("❌ Không có URL download hợp lệ")
            QMessageBox.warning(
                self, "Lỗi", "❌ Không có URL download hợp lệ.\nVui lòng thử tải về thủ công.")
            return

        print(self.update_info['download_url'])
        self.download_worker = DownloadUpdateWorker(
            self.update_info['download_url'], self.update_info['version'])
        self.download_worker.progress_signal.connect(
            self.update_download_progress)
        # self.download_worker.message_signal.connect(self.add_download_log)
        self.download_worker.finished_signal.connect(self.on_download_finished)
        self.download_worker.start()

    def on_download_finished(self, success, message):

        current_exe_path = sys.executable

        app_name = os.path.basename(current_exe_path)
        folder_path = os.path.dirname(current_exe_path)
        download_url = self.update_info['download_url']
        download_file_name = os.path.basename(download_url)
        output_file = os.path.join(folder_path, "update_info.txt")
        zip_path = os.path.join(folder_path, download_file_name)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"current_exe_path: {current_exe_path}\n")
            f.write(f"App Name: {app_name}\n")
            f.write(f"Folder Path: {folder_path}\n")
            f.write(f"Download URL: {download_url}\n")
            f.write(f"Download File Name: {download_file_name}\n")
            f.write(f"zip_path: {zip_path}\n")

        if success:
            # self.add_log("✅ Cập nhật thanh cong!")
            QMessageBox.information(self, "Cập nhật",
                                    f"✅ Cập nhật len phiên bản v{self.update_info['version']} thanh cong!\n\n"
                                    f"📦 Ứng dụng sẽ tải về và cài đặt cập nhật.\n"
                                    f"⏱️ Quá trình này có thể mất vài phút.")

        app_path = current_exe_path

        QMessageBox.information(self, "Cập nhật", f"✅ {current_exe_path}\n\n"
                                f"📦 {app_name}\n"
                                f"📦 {folder_path}\n"
                                f"📦 {download_file_name}\n"
                                f"📦 {zip_path}\n")
        # exe_path = sys.argv[0]  # đường dẫn app hiện tại
        app_dir = os.path.dirname(os.path.abspath(current_exe_path))

        # tìm updater_stub cạnh exe khi đóng gói
        updater_name = "updater_stub.exe" if sys.platform.startswith(
            "win") else "updater_stub"
        candidate_paths = [
            os.path.join(app_dir, updater_name),
            resource_path(updater_name)
        ]
        updater = next((p for p in candidate_paths if os.path.exists(p)), None)
        if not updater:
            raise FileNotFoundError(
                "Không tìm thấy updater_stub cạnh ứng dụng.")

        args = [updater, "--app", current_exe_path, "--zip",
                zip_path, "--dir", app_dir, "--restart"]

        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NO_WINDOW
        subprocess.Popen(args, close_fds=True, creationflags=creation_flags)

    def download_update(self):
        """Mở trang download thủ công"""
        try:
            webbrowser.open(self.update_info['download_url'])
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể mở trình duyệt: {e}")

    def update_download_progress(self, value):
        """Cập nhật progress bar cho download"""
        self.update_progress_bar.setValue(value)
        # if value < 95:
        #     self.update_status_label.setText(f"⬇️ Đang tải về... {value}%")
        # else:
        #     self.update_status_label.setText(f"📦 Đang cài đặt... {value}%")
