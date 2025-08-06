from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QSlider, QLineEdit, QFileDialog, QFrame, QRadioButton, QListWidget, QCheckBox, QMessageBox, QSpacerItem, QSizePolicy, QProgressBar, QMenu, QMenuBar
)
from PySide6.QtCore import Qt
import sys

from PySide6.QtGui import QScreen, QAction, QIcon

from ui_setting import show_about_ui, _init_addStyle
from ui_updatedialog import UI_UpdateDialog
from ui_checkupdate import UI_CheckUpdate

from ui_setting import APP_VERSION, resource_path

import os


class TTSApp(QWidget):
    def __init__(self):
        super().__init__()
        self.version = APP_VERSION  # Placeholder for server connection
        self.setWindowTitle("TTS App Clone")
        self.setMinimumSize(800, 600)
        icon_path = resource_path("ico.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        _init_addStyle(self)
        self.main_layout = QVBoxLayout(self)
        self.init_ui()
        self.update_checker = None
        self.is_manual_check = False

        # Thay đổi thành silent=True
        self._start_update_check()

    def init_ui(self):

        # Menu bar
        self._create_menubar()

        #
        self._create_version_update_ui()
        # URL input
        self._create_url_ui()
        self._create_folder_ui()

        # Chế độ tải
        self.type_video = QComboBox()
        self.type_video.addItems(["Playlist", "Video", "Audio"])
        self.type_video.setObjectName("typeVideo")

        self.chedo = QLabel("Chế độ tải xuống")
        self.chedo_video = QComboBox()
        self.chedo_video.addItems(
            ["❌ Không tải xuống", "🤖 Phụ đề tự động", "📄 Phụ đề có sẵn"])
        self.chedo_video.setObjectName("chedoVideo")

        self.title_language = QLabel("Ngôn ngữ")
        self.language_box = QComboBox()
        self.language_box.addItems(
            ["Tiếng Việt", "Tiếng Anh", "Tiếng Nhật", "Tiếng Trung"])
        self.language_box.setObjectName("languageBox")
        self.language_box.setFixedWidth(150)

        type_layout = QHBoxLayout()
        type_layout.setAlignment(Qt.AlignLeft)
        type_layout.addWidget(self.type_video)
        type_layout.addStretch()  # Thêm stretch để đẩy phần bên phải ra sát
        type_layout.addWidget(self.chedo)
        type_layout.addWidget(self.chedo_video)
        type_layout.addWidget(self.title_language)
        type_layout.addWidget(self.language_box)
        self.main_layout.addLayout(type_layout)

        # Tùy chọn bổ sung
        self._create_options_section()
        # Nút tải xuống và dừng
        self._create_download_section()

        self._create_log_section()
        # Thanh tiến trình
        self._create_progress_section()
        # Giới thiệ  TTS
        # self.main_layout.addWidget(
        #     QLabel("\nCông cụ chuyển văn bản thành giọng nói miễn phí"))

        # file_buttons = QHBoxLayout()
        # for name in ["Mở file văn bản", "Tải nội dung từ URL", "♫ Thêm nhạc nền", "Từ điển"]:
        #     file_buttons.addWidget(QPushButton(name))
        # self.main_layout.addLayout(file_buttons)

        # # Voice
        # voice_layout = QHBoxLayout()
        # voice_layout.addWidget(QLabel("🎙️ Chọn giọng đọc:"))

        # self.language_box = QComboBox()
        # self.language_box.addItems(
        #     ["Vietnamese / Tiếng Việt", "English / Tiếng Anh", "Japanese / Tiếng Nhật", "Chinese / Tiếng Trung"])
        # self.language_box.setCurrentText("Vietnamese / Tiếng Việt")

        # self.voice_box = QComboBox()
        # self.voice_box.addItems(["Kim Chi"])

        # voice_layout.addWidget(self.language_box)
        # voice_layout.addWidget(self.voice_box)
        # self.main_layout.addLayout(voice_layout)

        # # Sliders
        # slider_layout = QHBoxLayout()
        # self.pitch_slider = QSlider(Qt.Horizontal)
        # self.pitch_slider.setValue(50)
        # self.speed_slider = QSlider(Qt.Horizontal)
        # self.speed_slider.setValue(50)
        # slider_layout.addWidget(QLabel("Cao độ giọng nói (Bình thường)"))
        # slider_layout.addWidget(self.pitch_slider)
        # slider_layout.addWidget(QLabel("Tốc độ đọc (Bình thường)"))
        # slider_layout.addWidget(self.speed_slider)
        # self.main_layout.addLayout(slider_layout)

        # # Text
        # self.text_edit = QTextEdit()
        # self.text_edit.setPlaceholderText(
        #     "Nhập hoặc dán văn bản cần chuyển đổi...")
        # self.main_layout.addWidget(self.text_edit)

        # # Bottom
        # bottom_buttons = QHBoxLayout()
        # bottom_buttons.addWidget(QPushButton("➡ Chuyển đổi"))
        # bottom_buttons.addWidget(QPushButton("✔ Đã chuyển đổi"))
        # bottom_buttons.addWidget(QPushButton("⏲ Lịch sử"))
        # self.main_layout.addLayout(bottom_buttons)

    def _create_version_update_ui(self):
        # Version info
        self.version_box = QFrame()
        self.version_box.setObjectName("versionBox")
        self.version_layout = QVBoxLayout(self.version_box)

        self.version_label = QLabel("")
        self.version_label.setStyleSheet("color: #05df60; font-size: 16px;")
        self.version_old = QLabel(
            f"<span>📱 Phiên bản hiện tại: v{APP_VERSION}</span>")
        self.version_name = QLabel()
        self.version_layout.addWidget(self.version_label)
        self.version_layout.addWidget(self.version_old)
        self.version_layout.addWidget(self.version_name)

        buttons = QHBoxLayout()
        btn_install = QPushButton("🚀 Cài đặt tự động")
        self.btn_skip = QPushButton("❌ Bỏ qua")
        self.btn_skip.setObjectName("skipBtn")
        self.btn_skip.clicked.connect(self.skip_update_main)
        buttons.addWidget(btn_install)
        buttons.addWidget(self.btn_skip)
        self.version_layout.addLayout(buttons)

        self.main_layout.addWidget(self.version_box)
        self.version_box.setVisible(False)  # Ban đầu ẩn box phiên bản

    def _create_menubar(self):
        """Tạo thanh menu cho ứng dụng"""
        self.menubar = QMenuBar(self)

        # Menu File
        file_menu = self.menubar.addMenu("📁 File")

        # Action Reset Settings
        reset_action = QAction("🔄 Reset Settings", self)
        # reset_action.triggered.connect(self.reset_settings)
        file_menu.addAction(reset_action)

        file_menu.addSeparator()

        # Action Exit
        exit_action = QAction("❌ Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu Settings
        settings_menu = self.menubar.addMenu("⚙️ Settings")

        # Action Save Current Settings
        save_settings_action = QAction("💾 Save Current Settings", self)
        # save_settings_action.triggered.connect(self.save_settings)
        settings_menu.addAction(save_settings_action)

        # Action Load Default Settings
        load_default_action = QAction("📋 Load Default Settings", self)
        # load_default_action.triggered.connect(self.load_default_settings)
        settings_menu.addAction(load_default_action)

        settings_menu.addSeparator()

        # Action View Settings Info
        info_action = QAction("📊 View Settings Info", self)
        # info_action.triggered.connect(self.show_settings_info)
        settings_menu.addAction(info_action)

        # Menu Help
        help_menu = self.menubar.addMenu("❓ Help")

        # Action Check for Updates
        update_action = QAction("🔄 Check for Updates", self)

        update_action.triggered.connect(self.show_update_dialog)
        help_menu.addAction(update_action)

        help_menu.addSeparator()

        # Action Check Tool Versions
        version_action = QAction("🔧 Check Tool Versions", self)
        # version_action.triggered.connect(self.check_tool_versions)
        help_menu.addAction(version_action)

        help_menu.addSeparator()

        # Action View Log File
        log_action = QAction("📝 View Log File", self)
        # log_action.triggered.connect(self.show_log_file)
        help_menu.addAction(log_action)

        help_menu.addSeparator()

        # Action About
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        # Thêm thanh menu vào layout chính
        self.main_layout.setMenuBar(self.menubar)

    def _create_url_ui(self):
        """Tạo giao diện nhập URL video hoặc văn bản"""
        url_layout = QVBoxLayout()
        url_label = QLabel("🔗 Nhập URL video hoặc văn bản")
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText(
            "Nhập URL video hoặc văn bản tại đây...")
        self.url_input.setObjectName("urlInput")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        self.main_layout.addLayout(url_layout)

    def _create_folder_ui(self):
        """Tạo giao diện nhập tên thư mục tải xuống"""
        # Tạo layout cho phần nhập tên thư mục
        layout_folder = QVBoxLayout()
        folder_title_layout = QHBoxLayout()
        folder_title_layout.addWidget(QLabel("📁 Tên thư mục tải (tuỳ chọn)"))
        self.main_layout.addLayout(folder_title_layout)
        folder_layout = QHBoxLayout()

        self.folder_name_input = QTextEdit()
        self.folder_name_input.setPlaceholderText(
            "Nhập tên thư mục hoặc chọn thư mục...")
        self.folder_name_input.setObjectName("folderNameInput")
        self.folder_name_input.setFixedHeight(38)
        self.folder_button = QPushButton("Open Folder")
        self.folder_button.setObjectName("folderBtn")
        self.folder_button.setToolTip("Chọn thư mục để lưu video")
        # Kết nối nút với hàm chọn thư mục (nếu cần)

        self.folder_button.setFixedWidth(120)
        # self.folder_button.clicked.connect(self.select_folder)

        folder_layout.addWidget(self.folder_name_input)
        folder_layout.addWidget(self.folder_button)

        layout_folder.addLayout(folder_title_layout)
        layout_folder.addLayout(folder_layout)
        self.main_layout.addLayout(layout_folder)

    def _create_options_section(self):
        """Dòng 1: chuyển phụ đề và mp3"""
        row1_layout = QHBoxLayout()
        self.convert_srt = QCheckBox("🔁 Chuyển phụ đề sang .srt")
        self.convert_srt.setChecked(True)
        self.audio_only = QCheckBox("🎵 Tải âm thanh MP3")
        self.include_thumb = QCheckBox("🖼️ Tải ảnh thumbnail")
        self.subtitle_only = QCheckBox("📝 Chỉ tải phụ đề")
        row1_layout.addWidget(self.convert_srt)
        row1_layout.addWidget(self.audio_only)
        row1_layout.addWidget(self.include_thumb)
        row1_layout.addWidget(self.subtitle_only)
        row1_layout.addStretch()

        self.main_layout.addLayout(row1_layout)

    def _create_progress_section(self):
        """Tạo thanh tiến trình"""
        # Dòng 1: Thanh tiến trình
        # row_progress = QHBoxLayout()
        self.progress = QProgressBar()
        self.progress.setVisible(False)  # Ban đầu ẩn thanh tiến trình
        self.progress.setObjectName("progressBar")
        self.progress.setRange(0, 100)  # Thiết lập phạm vi từ
        # row_progress.addWidget(self.progress)
        # Hiển thị văn bản trên thanh tiến trình
        self.progress.setVisible(True)

        self.progress.setValue(70)  # Thiết lập giá trị ban đầu là 0
        self.main_layout.addWidget(self.progress)

    def _create_download_section(self):
        """Dòng 2: Nút tải xuống và nút dừng"""
        row2_layout = QHBoxLayout()
        self.download_button = QPushButton("⬇️ Tải xuống")
        self.download_button.setObjectName("downloadBtn")
        self.stop_button = QPushButton("⏹️ Dừng")
        self.stop_button.setObjectName("stopBtn")

        row2_layout.addWidget(self.download_button)
        row2_layout.addWidget(self.stop_button)

        self.main_layout.addLayout(row2_layout)
        # Nút dừng ban đầu không được kích hoạt
        self.stop_button.setVisible(False)

    def _create_log_section(self):
        """Dòng 3: Nhật ký hoạt động"""
        # Nhật ký hoạt động
        self.output_list = QListWidget()
        self.output_list.setObjectName("logListWidget")
        self.output_list.setWordWrap(True)

        # Tùy chỉnh thanh cuộn
        self.output_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.output_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Chiều cao tối thiểu để hiển thị nội dung log
        self.output_list.setMinimumHeight(120)

        # Thêm vào layout chính
        self.main_layout.addWidget(QLabel("📝 Nhật ký hoạt động"))
        self.main_layout.addWidget(self.output_list)
        self.output_list.addItem("Nhập URL video hoặc văn bản để bắt đầu.")

    # def _create_options_section(self):
    #     """Dòng 2: thumbnail và chỉ phụ đề"""
    #     row2_layout = QVBoxLayout()

    #     row2_layout.addWidget(self.include_thumb)
    #     row2_layout.addWidget(self.subtitle_only)
    #     row2_layout.addStretch()

    #     self.main_layout.addLayout(row2_layout)

    def show_about(self):
        """Hiển thị thông tin về ứng dụng"""
        show_about_ui(self)

    def skip_update_main(self):
        self.version_box.setVisible(False)

    def _start_update_check(self):

        self.update_checker = UI_CheckUpdate()
        self.update_checker.update_available.connect(
            self._on_update_available)
        self.update_checker.error_occurred.connect(
            lambda error: QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra khi kiểm tra cập nhật:\n{error}"))
        self.update_checker.no_update.connect(
            lambda: self._on_no_update(silent=False))
        self.update_checker.start()
        # self.is_manual_check = True  # Đặt cờ là manual check
        # if self.is_manual_check:
        #     self.output_list.addItem("🔄 Đang kiểm tra phiên bản mới manual...")
        # else:
        #     self.output_list.addItem("🔄 Đang kiểm tra phiên bản mới...")

    def show_update_dialog(self):

        self.is_manual_check = True
        self._start_update_check()

        # Tạo dialog cập nhật

        # self.update_checker.no_update.connect(lambda: QMessageBox.information(
        #     self, "Không có cập nhật", "Ứng dụng của bạn đã là phiên bản mới nhất."))
        # dialog = UI_UpdateDialog(self.update_info, self)
        # dialog.exec()

    def _on_update_available(self, update_info):
        self.output_list.addItem("📥 Cập nhật có sẵn:")
        version = update_info.get('version', '1.0.0')
        version_name = update_info.get('name', 'Phiên bản mẫu')

        self.version_label.setText(
            f"<b>🎉 Cập nhật phiên bản mới v{version}</b>")
        self.version_name.setText(
            f"<span>📋 Tên phiên bản: {version_name}</span>")
        dialog = UI_UpdateDialog(update_info, self)
        dialog.exec()

        # Hiển thị box phiên bản khi có update
        self.version_box.setVisible(True)

    def _on_no_update(self, silent):
        """Xử lý khi không có update"""

        if not silent:
            self.output_list.addItem("✅ Bạn đang sử dụng phiên bản mới nhất")

            if self.is_manual_check:
                # Chỉ hiển thị MessageBox khi check thủ công, không hiển thị khi auto-check
                QMessageBox.information(
                    self, "Thông báo", f"✅ Bạn đang sử dụng phiên bản mới nhất (v{self.version})")
            # Reset flag sau khi xử lý
            self.is_manual_check = False

        else:
            # Khi auto-check, chỉ hiển thị trong log
            self.output_list.addItem(
                "✅ Phiên bản hiện tại là mới nhất (auto-check)")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TTSApp()
    window.show()
    sys.exit(app.exec())
