from ui_setting import _init_addStyle
from datetime import datetime
import os
import sys
import subprocess
import webbrowser
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox,
    QProgressBar, QHBoxLayout, QApplication, QFrame
)
from PySide6.QtCore import QTimer, Signal, QObject
# Phiên bản ứng dụng
APP_VERSION = "1.0.0"  # Placeholder for actual version, replace with


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

    def start_auto_download(self):
        """Bắt đầu tải về tự động"""
        # Kiểm tra xem có URL download không
        if not self.update_info.get('download_url'):
            self.add_log("❌ Không có URL download hợp lệ")
            QMessageBox.warning(
                self, "Lỗi", "❌ Không có URL download hợp lệ.\nVui lòng thử tải về thủ công.")
            return

        # Thêm thông báo bắt đầu cập nhật
        QMessageBox.information(self, "Cập nhật",
                                f"🔄 Bắt đầu cập nhật lên phiên bản v{self.update_info['version']}\n\n"
                                f"📦 Ứng dụng sẽ tự động tải về và cài đặt cập nhật.\n"
                                f"⏱️ Quá trình này có thể mất vài phút.")
        QApplication.instance().quit()
        # os.system("taskkill /f /im DownloadVID.exe")
        subprocess.run([r"Update.exe"])

    def download_update(self):
        """Mở trang download thủ công"""
        try:
            webbrowser.open(self.update_info['download_url'])
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể mở trình duyệt: {e}")
