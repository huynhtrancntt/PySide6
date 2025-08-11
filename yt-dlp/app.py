from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QComboBox, QTabWidget, QFormLayout, QListWidget, QGroupBox, QCheckBox, QFileDialog, QProgressBar, QMessageBox, QListWidgetItem, QMenuBar
)
from PySide6.QtCore import Signal, QTime, QTimer
from PySide6.QtGui import QColor, QIcon, QAction
from ui_setting import APP_VERSION, show_about_ui, _init_addStyle, resource_path
from ui_checkupdate import UI_CheckUpdate
from ui_updatedialog import UI_UpdateDialog
from downloadWorker import DownloadVideo
from license_manager import check_license, create_license
import os
import subprocess
# from ui_updatedialog import UI_UpdateDialog
from datetime import datetime
import sys


class Tab_1(QWidget):
    progress_update = Signal(int, str)

    def __init__(self, append_log,  log_widget, output_list, progress, tab_name="Tab 1"):
        super().__init__()
        self.append_log = append_log
        self.worker = None
        # Thread
        self.index = 1
        self.active_threads = []
        self.max_workers = 4
        self.running = 0
        self.stopped = False

        self.download_folder = ""
        self.urls = []
        self.output_list = output_list
        self.log_widget = log_widget
        self.progress = progress
        self.log_widget.setVisible(True)
        # self.progress.setVisible(False)
        self.progress.setValue(0)  # Thiết lập giá trị ban đầu
        self.progress.hide()  # Hiện progress_bar khi bắt đầu
        self.append_log(
            f"Đang sử dung tab {tab_name}")
        layout = QVBoxLayout()

        # Nhập URL
        url_layout = QVBoxLayout()
        url_label = QLabel("🔗 Nhập URL video hoặc văn bản")
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText(
            "Nhập URL video hoặc văn bản tại đây...")
        self.url_input.setObjectName("urlInput")
        self.url_input.setText(
            "https://www.youtube.com/watch?v=uqSF-h404jc\nhttps://www.youtube.com/watch?v=uqSF-h404jc\nhttps://www.youtube.com/watch?v=uqSF-h404jc")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Nhập tên thư mục
        self.group_box = QGroupBox("📁 Tên thư mục tải (tuỳ chọn)")
        group_layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        self.folder_name_input = QLineEdit()
        self.folder_name_input.setPlaceholderText(
            "Nhập tên thư mục hoặc chọn thư mục...")
        self.folder_name_input.setReadOnly(True)
        self.folder_name_input.setObjectName("folderNameInput")
        # self.folder_name_input.setText("Videos")
        folder_button = QPushButton("Open")
        folder_button.clicked.connect(self.open_folder_dialog)
        input_layout.addWidget(self.folder_name_input)
        input_layout.addWidget(folder_button)
        group_layout.addLayout(input_layout)
        self.group_box.setLayout(group_layout)
        layout.addWidget(self.group_box)

        # Cài đặt video
        self.group_box_setting_video = QGroupBox()
        layout_chedo = QFormLayout()
        self.group_box_setting_video.setLayout(layout_chedo)

        lang_layout = QHBoxLayout()
        self.type_video = QComboBox()
        self.type_video.addItems(["Video", "Playlist"])
        self.type_video.setCurrentText("Video")
        self.sub_mode = QComboBox()
        self.sub_mode_list = [
            ("❌ Không tải xuống", ""),
            ("📄 Phụ đề có sẵn", "1"),
            ("🤖 Phụ đề tự động", "2"),
        ]
        for name, code in self.sub_mode_list:
            self.sub_mode.addItem(name, userData=code)

        for i in range(self.sub_mode.count()):
            if self.sub_mode.itemData(i) == "2":
                self.sub_mode.setCurrentIndex(i)
                break
        self.language_box = QComboBox()
        self.languages = [
            ("Tiếng Việt", "vi"),
            ("Tiếng Anh", "en"),
            ("Tiếng Nhật", "ja"),
            ("Tiếng Trung", "zh")
        ]
        for name, code in self.languages:
            self.language_box.addItem(name, userData=code)

        # Chọn ngôn ngữ theo mã code (VD: "ja")
        for i in range(self.language_box.count()):
            if self.language_box.itemData(i) == "vi":
                self.language_box.setCurrentIndex(i)
                break
        # self.language_box.addItems(
        #     ["Tiếng Việt", "Tiếng Anh", "Tiếng Nhật", "Tiếng Trung"])
        # lang_layout.addWidget(self.type_video)
        lang_layout.addStretch()
        lang_layout.addWidget(QLabel("Chế độ tải xuống:"))
        lang_layout.addWidget(self.sub_mode)
        lang_layout.addWidget(QLabel("Ngôn ngữ"))
        lang_layout.addWidget(self.language_box)
        layout_chedo.addRow(self.type_video, lang_layout)
        self.thread_combo = QComboBox()
        self.thread_combo.addItems([str(i) for i in range(1, 11)])  # 1 -> 10
        self.thread_combo.setCurrentText("2")
        row1_layout = QHBoxLayout()
        self.audio_only = QCheckBox("🎵 Tải âm thanh MP3")
        self.include_thumb = QCheckBox("🖼️ Tải ảnh thumbnail")
        self.subtitle_only = QCheckBox("📜 Chỉ tải phụ đề")
        row1_layout.addStretch()
        row1_layout.addWidget(self.audio_only)
        row1_layout.addWidget(self.include_thumb)
        row1_layout.addWidget(self.subtitle_only)
        # row1_layout.addStretch()
        # layout_Thread = QHBoxLayout()
        # layout_Thread.addWidget(self.thread_combo)
        layout_chedo.addRow(self.thread_combo, row1_layout)
        # layout.addWidget(layout_Thread)
        layout.addWidget(self.group_box_setting_video)
        layout.addStretch()

        # Nút
        layout_download = QHBoxLayout()
        self.download_button = QPushButton("🚀 Bắt đầu tải")
        self.download_button.setObjectName("downloadBtn")
        self.download_button.clicked.connect(self.start_download)

        self.stop_button = QPushButton("⏹️ Dừng")
        self.stop_button.setObjectName("stopBtn")
        self.stop_button.clicked.connect(self.stop_download)
        self.stop_button.setEnabled(False)
        layout_download.addWidget(self.download_button)
        layout_download.addWidget(self.stop_button)
        layout.addLayout(layout_download)

        # print("Mã ngôn ngữ được chọn:", selected_code)
        self.setLayout(layout)

    def open_folder_dialog(self):
        self.log_widget.setVisible(True)
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục")
        if folder:
            self.folder_name_input.setText(folder)

    def _get_selected_language_code(self):
        selected_code = self.language_box.currentData()
        return selected_code

    def start_download(self):

        urls = [u.strip()
                for u in self.url_input.toPlainText().splitlines() if u.strip()]
        if not urls:
            QMessageBox.warning(self, "Cảnh báo", "Bạn chưa nhập URL nào.")
            return

        urls = self.url_input.toPlainText().splitlines()
        urls = [u.strip() for u in urls if u.strip()]

        self.urls = urls
        # self._prepare_ui_for_download()
        # Lấy mã ngôn ngữ tương ứng khi người dùng chọn
        selected_lang_code = self._get_selected_language_code()
        # self.add_message(f"Mã ngôn ngữ tài liệu: {selected_lang_code}")

        # Hiển thị các tùy chọn khác
        options = []
        if self.audio_only.isChecked():
            options.append("🎵 Audio MP3")
        if self.include_thumb.isChecked():
            options.append("🖼️ Thumbnail")
        if self.subtitle_only.isChecked():
            options.append("📝 Chỉ phụ đề")

        if options:
            self.append_log(f"⚙️ Tùy chọn: {', '.join(options)}")

        # Folder name
        custom_folder = self.folder_name_input.text()
        if custom_folder:
            self.append_log(f"📁 Thư mục: {custom_folder}")

        selected_sub_mode = self.sub_mode.currentData()
        sub_mode_name = next(
            (name for name, code in self.sub_mode_list if code == selected_sub_mode), None)
        if selected_sub_mode:
            self.append_log(f"📜 Chế độ {sub_mode_name}")

        # Lấy số Thread từ DropBox
        self.max_workers = int(self.thread_combo.currentText())
        if not self.urls:
            self.append_log("❌ Không có URL hợp lệ.", "warning")
            return

        self.append_log(f"📦 Tổng số link: {len(self.urls)}")

        self.stopped = False
        self.download_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress.show()
        self.progress.setValue(0)

        self.append_log("🚀 Bắt đầu tải video...")
        self.index = 1
        self.active_threads.clear()
        self.running = 0
        self.custom_folder_name = custom_folder
        self.video_mode = self.type_video.currentText()

        self.audio_only_flag = self.audio_only.isChecked()
        self.sub_mode_flag = selected_sub_mode
        self.sub_lang_code_flag = selected_lang_code
        self.sub_lang_name_flag = self.language_box.currentText()
        self.include_thumb_flag = self.include_thumb.isChecked()
        self.subtitle_only_flag = self.subtitle_only.isChecked()
        self.download_folder = self._create_download_folder()
        self.download_next_batch()

    def download_next_batch(self):

        while self.running < self.max_workers and self.index <= len(self.urls) and not self.stopped:
            url = self.urls[self.index - 1]
            worker_id = self.running + 1
            thread = DownloadVideo(
                url=url,
                video_index=self.index,
                total_urls=len(self.urls),
                worker_id=worker_id,
                video_mode=self.video_mode,
                audio_only=self.audio_only_flag,
                sub_mode=self.sub_mode_flag,
                sub_lang=self.sub_lang_code_flag,
                sub_lang_name=self.sub_lang_name_flag,
                include_thumb=self.include_thumb_flag,
                subtitle_only=self.subtitle_only_flag,
                custom_folder_name=self.download_folder
            )
            thread.message_signal.connect(self.append_log)
            thread.finished_signal.connect(self.handle_thread_done)
            thread.progress_signal.connect(self.update_progress)
            thread.error_signal.connect(self.error_thread)
            self.active_threads.append(thread)
            thread.start()
            self.running += 1
            self.index += 1

    def handle_thread_done(self):
        self.running -= 1
        if not self.stopped and self.index <= len(self.urls):
            self.download_next_batch()
        elif self.running == 0:
            if self.stopped:
                self.append_log("⏹ Đã dừng toàn bộ tiến trình.")
            else:
                self.progress.setValue(100)
                self.append_log("✅ Tải xong tất cả video.")
                self.append_log(
                    f"📂 Video được lưu tại: {self.download_folder}")
            self.download_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.progress.setValue(0)
            self.progress.hide()

    def update_progress(self, value):
        self.progress.setValue(value)
        # self._reset_ui_after_download()

    def error_thread(self, value):
        self.append_log(value, "error")

    def stop_download(self):
        self.stopped = True

        for thread in self.active_threads:
            thread.stop_flag = True

        self.append_log("⏹ Đang dừng các tiến trình tải...")
        self.stop_button.setEnabled(False)
        self.download_button.setEnabled(True)
        self.progress.hide()  # Ẩn progress_bar khi dừng

    # def on_download_progress_message(self, message):
    #     self.add_message(message)

    #     self.progress.hide()  # Ẩn progress_bar khi dừng

    # def on_download_finished(self, message):
    #     """Xử lý khi download hoàn thành"""

    #     self.add_message("✅ Download hoàn tất!")
    #     self.add_message(message)
    #     # self._reset_ui_after_download()

    # Tao

    def _create_download_folder(self):
        """Tạo thư mục download với cấu trúc đơn giản"""
        base_folder = "Video"
        os.makedirs(base_folder, exist_ok=True)

        if self.custom_folder_name:
            # Nếu có tên thư mục tùy chọn
            if os.path.isabs(self.custom_folder_name):
                # Đường dẫn đầy đủ
                date_folder = self.custom_folder_name
            else:
                # Tên thư mục - tạo trong thư mục Video
                date_folder = os.path.join(
                    base_folder, self.custom_folder_name)
        else:
            # Không có tên tùy chọn - tạo theo ngày
            date_str = datetime.now().strftime("%Y-%m-%d")
            date_folder = os.path.join(base_folder, date_str)

        # Tạo thư mục con với số thứ tự (01, 02, 03...)
        download_folder = self._create_numbered_subfolder(date_folder)

        os.makedirs(download_folder, exist_ok=True)
        return download_folder

    def _create_numbered_subfolder(self, date_folder):
        """Tạo thư mục con với số thứ tự (01, 02, 03...)"""
        if not os.path.exists(date_folder):
            os.makedirs(date_folder, exist_ok=True)

        # Tìm số thứ tự cao nhất trong thư mục ngày
        max_number = 0
        for item in os.listdir(date_folder):
            item_path = os.path.join(date_folder, item)
            if os.path.isdir(item_path) and item.isdigit():
                max_number = max(max_number, int(item))

        # Tạo thư mục con mới với số tiếp theo (format 2 chữ số)
        next_number = max_number + 1
        subfolder_name = f"{next_number:02d}"
        download_folder = os.path.join(date_folder, subfolder_name)

        return download_folder

    def _prepare_ui_for_download(self):
        """Chuẩn bị UI cho quá trình download"""
        # self.output_list.clear()
        self.progress.setValue(0)
        self.stop_button.setVisible(True)
        self.progress.setVisible(True)
        self.download_button.setEnabled(False)

    def _reset_ui_after_download(self):
        """Reset UI sau khi download xong hoặc dừng"""
        self.stop_button.setVisible(False)
        self.progress.setVisible(False)
        # self.progress.setVisible(True)
        self.download_button.setEnabled(True)


class TranslateTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        input_output_layout = QHBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Nhập văn bản cần dịch vào đây...")
        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText(
            "Kết quả dịch sẽ hiển thị ở đây...")
        self.output_text.setReadOnly(True)
        input_output_layout.addWidget(self.input_text)
        input_output_layout.addWidget(self.output_text)
        layout.addLayout(input_output_layout)

        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText("Nhập prompt tại đây...")
        layout.addWidget(QLabel("Prompt Tùy chỉnh cho các mô hình AI:"))
        layout.addWidget(self.prompt_text)

        self.translate_button = QPushButton("Dịch văn bản")
        self.translate_button.setStyleSheet(
            "background-color: #2196F3; color: white; padding: 6px;")
        layout.addWidget(self.translate_button)

        self.setLayout(layout)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("App HT")
        icon_path = resource_path("images/icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        _init_addStyle(self)
        self.is_manual_check = False
        self.version = APP_VERSION  # Placeholder for server connection
        self._init_ui()

    def _init_ui(self):

        # Layout chính
        self.layout = QVBoxLayout(self)

        # Layout gom Tabs + Log + Progress
        self.main_content_layout = QVBoxLayout()

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setMovable(True)

        # Log widget
        self.log_widget = QWidget()
        self.layout_log = QVBoxLayout(self.log_widget)
        self.output_list = QListWidget()
        self.output_list.setObjectName("logListWidget")
        self.layout_log.addWidget(QLabel("📝 Nhật ký hoạt động"))
        self.layout_log.addWidget(self.output_list)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setObjectName("progressBar")
        self.progress.setRange(0, 100)
        self.progress.setVisible(False)

        # Thêm Tab
        self.tabs.addTab(
            Tab_1(self.append_log,
                  self.log_widget,
                  self.output_list,
                  self.progress,
                  "Video Downloader"),
            "Video Downloader"
        )
        self.tabs.addTab(TranslateTab(), "Dịch Văn bản / Prompt Tùy chỉnh")

        # Gom Tabs + Log + Progress vào chung layout
        self.main_content_layout.addWidget(self.tabs)
        self._ui_session_manager_key()
        self.main_content_layout.addWidget(self.log_widget)
        self.main_content_layout.addWidget(self.progress)
        # self.main_content_layout.addWidget(
        #
        # )
        # self._ui_session_manager_key()
        # Thêm menu(nếu muốn menu bar nằm trên cùng)
        # Tạo menu bar
        self.menu_bar = QMenuBar()

        # Menu File
        file_menu = self.menu_bar.addMenu("📂 File")
        file_menu.addAction("Thoát")

        # Menu Help
        help_menu = self.menu_bar.addMenu("❓ Help")
        update_action = QAction("🔄 Check for Updates", self)
        update_action.triggered.connect(self.show_update_dialog)
        help_menu.addAction(update_action)

        # Gán menu bar vào layout chính
        self.layout.setMenuBar(self.menu_bar)

        # Thêm layout gom vào layout chính
        self.layout.addLayout(self.main_content_layout)
        self._start_update_check()
        # Gọi hàm xử lý key

    def show_update_dialog(self):
        self.is_manual_check = True
        self._start_update_check()

    def _ui_session_manager_key(self):
        # QGroupBox "Quản lý License"
        self.group_box = QGroupBox("Quản lý License")

        group_layout = QVBoxLayout()

        # Thông tin license
        info_label = QLabel("""
            <b>Trạng thái License:</b> ✅ Hợp lệ |
            <b>Loại:</b> HTPRO |
            <b>Hết hạn:</b> 2025-08-11 |
            <b>Lượt còn:</b> 200
        """)
        info_label.setWordWrap(True)
        group_layout.addWidget(info_label)

        # Input + nút kích hoạt
        input_layout = QHBoxLayout()
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Nhập mã kích hoạt tại đây")
        btn_activate = QPushButton("Kích hoạt")
        btn_activate.clicked.connect(self.apply_manager_key)

        input_layout.addWidget(self.input_code)
        input_layout.addWidget(btn_activate)

        group_layout.addLayout(input_layout)
        self.group_box.setLayout(group_layout)

        # === Bọc QGroupBox để tạo margin trái-phải ===
        wrapper_widget = QWidget()
        wrapper_layout = QVBoxLayout(wrapper_widget)
        wrapper_layout.setContentsMargins(
            10, 0, 10, 0)  # left, top, right, bottom
        wrapper_layout.addWidget(self.group_box)

        # Thêm vào layout chính
        self.main_content_layout.addWidget(wrapper_widget)

        self.group_box.setVisible(True)
        if __import__("os").path.exists("license.lic"):
            # self.group_box.setVisible(True)
            status, data = check_license()
            print(status, data)
            if status:
                self.group_box.setVisible(False)
            else:
                self.append_log(
                    f"⚠️ Bản quyền không hợp lệ, vui lòng kích hoạt lại", "warning")

        # print(data)  # data lúc này là chuỗi báo lỗi

    def _start_update_check(self):
        self.update_checker = UI_CheckUpdate()
        self.update_checker.update_available.connect(
            self._on_update_available)
        self.update_checker.error_occurred.connect(
            lambda error: QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra khi kiểm tra cập nhật:\n{error}"))
        self.update_checker.no_update.connect(
            lambda: self._on_no_update())
        self.update_checker.start()

    def _on_update_available(self, update_info):
        # self.output_list.addItem("📥 Cập nhật có sẵn:")

        # version = update_info.get('version', '1.0.0')
        # version_name = update_info.get('name', 'Phiên bản mẫu')

        # # self.version_label.setText(
        # #     f"<b>🎉 Cập nhật phiên bản mới v{version}</b>")
        # # self.version_name.setText(
        # #     f"<span>📋 Tên phiên bản: {version_name}</span>")
        dialog = UI_UpdateDialog(update_info, self)
        dialog.exec()

        # Hiển thị box phiên bản khi có update
        # self.version_box.setVisible(True)
    def _on_no_update(self):
        """Xử lý khi không có update"""

        if self.is_manual_check:
            # Chỉ hiển thị MessageBox khi check thủ công, không hiển thị khi auto-check
            QMessageBox.information(
                self, "Thông báo", f"✅ Bạn đang sử dụng phiên bản mới nhất (v{self.version})")
            # Reset flag sau khi xử lý
            # self.is_manual_check = False

        else:
            #    # Khi auto-check, chỉ hiển thị trong log
            self.append_log(
                "✅ Phiên bản hiện tại là mới nhất (auto-check)", "info"
            )

    def apply_manager_key(self):

        if self.input_code.text() == "HTPRO":
            create_license()
            if __import__("os").path.exists("license.lic"):
                status, data = check_license()
                if not status:
                    self.group_box.setVisible(True)
                else:
                    self.group_box.setVisible(False)
        else:
            QMessageBox.warning(
                self, "Thông báo", "Sai mã kích hoạt")

    def append_log(self, message, level=""):
        current_time = QTime.currentTime().toString("HH:mm:ss")
        message = f"[{current_time}] {message}"
        item = QListWidgetItem(message)
        if level == "info":
            item.setForeground(QColor("#05df60"))
        elif level == "warning":
            item.setForeground(QColor("orange"))
        elif level == "error":
            item.setForeground(QColor("red"))
        elif level == "blue":
            item.setForeground(QColor("#4a5568"))
        self.output_list.addItem(item)
        self.output_list.scrollToBottom()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
