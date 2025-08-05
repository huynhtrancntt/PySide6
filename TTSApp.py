from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QSlider, QLineEdit, QFileDialog, QFrame, QRadioButton, QListWidget, QCheckBox, QMessageBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
import sys


class TTSApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TTS App Clone")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #0f172b;
                color: #e2e8f0;
                font-family: Arial;
                font-size: 14px;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
                font-weight: normal;
            }
            QPushButton {
                background-color: #05ff8f;
                color: #000;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #03b264;
            }
            QPushButton#skipBtn {
                background-color: #163b4e;
                color: #4994e7;
            }
            QPushButton#skipBtn:hover {
                background-color: #133544;
            }
            QTextEdit, QLineEdit, QComboBox {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px;
            }
            QFrame#versionBox {
                background-color: #0d2b32;
                border-radius: 10px;
                padding: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #334155;
                border-radius: 50px;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #05ff8f;
            }
            QComboBox {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px;   
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #334155;
                border-left-style: solid;
            }
            QComboBox::down-arrow {
                image: url('down-arrow.png');  /* Replace with your down arrow icon */
                width: 16px;
                height: 16px;
            }
            QSlider::groove:horizontal {
                background: #334155;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #05ff8f;
                height: 8px;
             
                              border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #05df60;
                height: 16px;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
            QCheckBox {
                color: #e2e8f0;
                font-size: 14px;
            }
            QRadioButton {
                color: #e2e8f0;
                font-size: 14px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                background-color: transparent;
            }
            QRadioButton::indicator:checked {
                background-color: #05ff8f;
            }
            QListWidget {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 6px;
                font-family: "Consolas", "Monaco", monospace;
                font-size: 12px;
                padding: 6px;
                selection-background-color: #4299e1;
                outline: none;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid #4a5568;
                min-height: 20px;
                word-wrap: break-word;
            }
            QListWidget::item:hover {
                background-color: #4a5568;
            }
            QListWidget::item:selected {
                background-color: #4299e1;
                color: #ffffff;
            }                           
        """)

        self.main_layout = QVBoxLayout(self)
        self.init_ui()

    def init_ui(self):
        # Version info
        version_box = QFrame()
        version_box.setObjectName("versionBox")
        version_layout = QVBoxLayout(version_box)

        version_label = QLabel("<b>Cập nhật phiên bản mới 1.1.2</b>")
        version_label.setStyleSheet("color: #05df60; font-size: 16px;")
        release_label = QLabel(
            "<span style='color:#05ff8f'>Ngày phát hành: 15/03/2025</span>")
        version_layout.addWidget(version_label)
        version_layout.addWidget(release_label)

        feature_list = QLabel("""
        <ul style='color:#05ff8f; list-style-type: disc; padding: 5px;'>
            <li>Chuyển đổi văn bản thành giọng nói (TTS)</li>
            <li>Thêm tính năng chuyển văn bản thành giọng nói (TTS)</li>
            <li>Tính năng Pro: OpenAI TTS (BYOK)</li>
            <li>Cải thiện trạng Pro</li>
            <li>Một số tối ưu và tính chỉnh khác</li>
        </ul>
        """)
        version_layout.addWidget(feature_list)

        buttons = QHBoxLayout()
        btn_install = QPushButton("⬇️ Tải về và cài đặt")
        btn_skip = QPushButton("❌ Bỏ qua")
        btn_skip.setObjectName("skipBtn")
        buttons.addWidget(btn_install)
        buttons.addWidget(btn_skip)
        version_layout.addLayout(buttons)

        self.main_layout.addWidget(version_box)

        # URL input
        url_layout = QVBoxLayout()
        url_label = QLabel("Nhập URL video:")
        url_layout.addWidget(url_label)
        self.main_layout.addLayout(url_layout)

        self.url_edit = QTextEdit()
        self.url_edit.setObjectName("urlEditVideo")
        self.url_edit.setPlaceholderText(
            "Nhập hoặc dán video URL tại đây...\nVí dụ: https://www.example.com/video.mp4")
        self.url_edit.setFixedHeight(120)
        self.main_layout.addWidget(self.url_edit)

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
        self.output_list.addItem("Chào mừng bạn đến với ứng dụng TTS!")
        self.output_list.addItem("Nhập URL video hoặc văn bản để bắt đầu.")

    # def _create_options_section(self):
    #     """Dòng 2: thumbnail và chỉ phụ đề"""
    #     row2_layout = QVBoxLayout()

    #     row2_layout.addWidget(self.include_thumb)
    #     row2_layout.addWidget(self.subtitle_only)
    #     row2_layout.addStretch()

    #     self.main_layout.addLayout(row2_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TTSApp()
    window.show()
    sys.exit(app.exec())
