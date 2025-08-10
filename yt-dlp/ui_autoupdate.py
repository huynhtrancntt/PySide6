from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel, QListWidget,
    QSizePolicy, QApplication, QMessageBox, QFrame
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QTimer
from ui_setting import APP_VERSION, _init_addStyle, resource_path
from ui_checkupdate import UI_CheckUpdate
from ui_downloadUpdateWorker import DownloadUpdateWorker
import os
import sys


class UI_AutoUpdateDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Update")
        self.setMinimumWidth(800)
        self.setMaximumHeight(100)
        icon_path = resource_path("ico.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        _init_addStyle(self)
        self.init_ui()
        # Hiển thị progress bar ngay khi khởi động
        self.update_progress_bar.setVisible(True)
        self.update_status_label.setVisible(True)
        self.update_progress_bar.setValue(5)
        self.update_status_label.setText("Đang kiểm tra...")
        self.output_list.setVisible(False)
        # self.output_list.addItem("🔄 Đang kiểm tra phiên bản mới...")

        # Kiểm tra update tự động khi khởi động (sau 3 giây)
        QTimer.singleShot(2000, self.auto_check_update)

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Layout chứa toàn bộ phần thân
        self.layout = QVBoxLayout()
        main_layout.addLayout(self.layout)
        self.version_box = QFrame()
        self.version_box.setObjectName("versionBox")
        self.version_layout = QVBoxLayout(self.version_box)

        self.version_label = QLabel(
            f"<b>🎉 Cập nhật phiên bản mới</b>")
        self.version_label.setStyleSheet("color: #05df60; font-size: 16px;")
        self.version_old = QLabel(
            f"<span>📱 Phiên bản hiện tại: v{APP_VERSION}</span>")
        self.version_name = QLabel()
        self.version_layout.addWidget(self.version_label)
        self.version_layout.addWidget(self.version_old)
        self.version_layout.addWidget(self.version_name)

        self.layout.addWidget(self.version_box)
        self.version_box.setVisible(False)
        self._create_progress_bar_section()
        self._create_log_section()

    def _create_progress_bar_section(self):
        """Tạo phần thanh tiến trình"""

        self.update_progress_layout = QHBoxLayout()

        self.update_progress_bar = QProgressBar()
        self.update_progress_bar.setVisible(False)
        self.update_progress_bar.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.update_status_label = QLabel("Checking for updates...")
        self.update_status_label.setStyleSheet("color: #05df60;")
        self.update_status_label.setVisible(False)
        self.update_status_label.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.update_progress_layout.addWidget(self.update_progress_bar)
        self.update_progress_layout.addWidget(self.update_status_label)

        # Đặt vào một widget bao ngoài để kiểm soát layout tốt hơn
        container = QWidget()
        container.setLayout(self.update_progress_layout)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.layout.addWidget(container)

    def _create_log_section(self):
        """Tạo phần nhật ký"""

        self.output_list = QListWidget()
        self.output_list.setObjectName("logListWidget")
        self.output_list.setWordWrap(True)
        self.output_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.output_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Cho phép chiếm phần không gian còn lại
        self.output_list.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout.addWidget(self.output_list)

    def scroll_to_bottom(self):
        """Cuộn xuống cuối danh sách"""
        self.output_list.scrollToBottom()

    def auto_check_update(self):
        self.update_progress_bar.setValue(10)
        self.update_status_label.setText("Đang kiểm tra...")
        self.output_list.setVisible(True)
        self.output_list.addItem("🔄 Đang kiểm tra phiên bản mới...")
        self.scroll_to_bottom()
        self._start_update_check()

    def _start_update_check(self):
        # Cập nhật progress bar
        self.update_progress_bar.setValue(20)
        # self.update_status_label.setText("🔄 Đang kết nối server...")
        # self.output_list.addItem("🔄 Đang kết nối server...")
        self.scroll_to_bottom()
        self.update_checker = UI_CheckUpdate()
        self.update_checker.update_available.connect(self.on_update_available)
        self.update_checker.no_update.connect(self.on_no_update)
        self.update_checker.error_occurred.connect(self.on_update_error)
        self.update_checker.progress_update.connect(
            self.update_progress_and_status)
        self.update_checker.start()

    def on_update_available(self, update_info):
        # print(update_info)
        version = update_info.get('version', '1.0.0')
        version_name = update_info.get('name', 'Phiên bản mẫu')

        self.version_label.setText(
            f"<b>🎉 Cập nhật phiên bản mới v{version}</b>")
        self.version_name.setText(
            f"<span>📋 Tên phiên bản: {version_name}</span>")
        self.version_box.setVisible(True)

        # Tạo và chạy download worker
        self.download_worker = DownloadUpdateWorker(
            update_info['download_url'], update_info['version'])
        self.download_worker.progress_signal.connect(
            self.update_download_progress)
        self.download_worker.message_signal.connect(self.add_download_log)
        self.download_worker.finished_signal.connect(self.on_download_finished)
        self.download_worker.start()

    def on_no_update(self):
        self.update_status_label.setText("✅ Phiên bản mới nhất")
        QMessageBox.information(
            self, "Không có cập nhật", f"✅Phiên bản mới nhất\n\n"
            f"🔄 Vui lòng khởi động lại ứng dụng.")
        pass

    def on_update_error(self, error):
        pass

    def update_progress_and_status(self, progress, message):
        """Cập nhật progress bar và status label"""
        # Giữ progress ở 20% thay vì 100%
        self.output_list.addItem(message)
        self.update_progress_bar.setValue(progress)
        self.update_status_label.setText(message)

    def update_download_progress(self, value):
        """Cập nhật progress bar cho download"""
        self.update_progress_bar.setValue(value)
        if value < 80:
            self.update_status_label.setText(f"⬇️ Đang tải về... {value}%")
        else:
            self.update_status_label.setText(f"📦 Đang cài đặt... {value}%")

    def on_download_finished(self, success, message):
        if success:
            self.add_download_log("✅ Cập nhật thành công!")
            self.add_download_log("🔄 Ứng dụng sẽ khởi động lại...")
            self.update_status_label.setVisible(False)
            # Hiển thị thông báo thành công
            QMessageBox.information(self, "Cập nhật thành công",
                                    f"✅ Cập nhật lên phiên bản v{self.download_worker.version} thành công!\n\n"
                                    f"🔄 Vui lòng khởi động lại để áp dụng thay đổi.")

            # Tự động khởi động lại ứng dụng
            # QApplication.instance().quit()
            # os.system("taskkill /f /im DownloadVID.exe")
            # os.system("taskkill /f /im Update.exe")
            # subprocess.run([r"DownloadVID.exe"])
        else:
            # Ẩn log output
            self.output_list.addItem(f"❌ Lỗi cập nhật")
            self.scroll_to_bottom()

            # Hiển thị thông báo lỗi
            QMessageBox.warning(self, "Lỗi cập nhật",
                                f"❌ Không thể cập nhật: {message}")

            # Ẩn progress bar sau 3 giây
            # QTimer.singleShot(3000, self._hide_update_progress

    def add_download_log(self, message):
        """Thêm log cho quá trình download - ẩn log"""
        # Ẩn log output
        self.output_list.addItem(message)
        self.scroll_to_bottom()
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UI_AutoUpdateDialog()
    window.show()
    sys.exit(app.exec())
