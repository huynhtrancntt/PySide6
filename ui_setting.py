# File: Ui_setting.py
from PySide6.QtWidgets import QMessageBox
import sys
import os

# Version of the application
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/huynhtrancntt/auto_update/main/update.json"
APP_VERSION = "1.6.0"  # Placeholder for actual version, replace with your app's version
ABOUT_TEMPLATE = """
<h3>🎬 HT DownloadVID v{version}</h3>
<p><b>Ứng dụng download video và phụ đề</b></p>
<p>📅 Phiên bản: {version}</p>
<p>👨‍💻 Phát triển bởi: HT Software</p>
<p>🔧 Sử dụng: yt-dlp + ffmpeg</p>
<br>

<p><b>Tính năng:</b></p>
<ul>
  <li>✅ Download video từ nhiều nền tảng</li>
  <li>✅ Hỗ trợ playlist</li>
  <li>✅ Download phụ đề đa ngôn ngữ</li>
  <li>✅ Chuyển đổi audio sang MP3</li>
  <li>✅ Lưu settings tự động</li>
  <li>✅ Kiểm tra cập nhật tự động</li>
</ul>
"""


def resource_path(relative_path):
    """Trả về đường dẫn chính xác đến resource khi chạy exe hoặc script"""
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def show_about_ui(self):
    about_text = ABOUT_TEMPLATE.format(version=self.version)
    QMessageBox.about(self, "Về ứng dụng", about_text)


def _init_addStyle(self):
    arrow_icon_path = resource_path("down-arrow.png").replace("\\", "/")

    self.setStyleSheet(f"""
        QMenuBar {{
            background-color: #0d2538;
            color: #ffffff;
            font-family: Arial;
            font-size: 14px;
        }}
        QMenu {{
            background-color: #0d2538;
            color: #ffffff;
            font-family: Arial;
            font-size: 14px;
        }}
        QMenu::item {{
            padding: 8px 16px;
        }}   
        QMenu::item:selected {{
            background-color: #1e293b;
            color: #ffffff;
        }}
        QMenu::separator {{
            height: 1px;
            background-color: #334155;
        }}
        QMenu::icon {{
            margin-right: 8px;
        }}
        QMenu::item:disabled {{
            color: #a0aec0;
        }}
        QWidget {{
            background-color: #0f172b;
            color: #e2e8f0;
            font-family: Arial;
            font-size: 14px;
        }}
        QLabel {{
            color: #ffffff;
            background-color: transparent;
            font-weight: normal;
        }}
        QPushButton {{
            background-color: #28a745;
            color: white;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
        }}
        QPushButton:hover {{
            background-color: #218838;
        }}
        QPushButton:disabled {{
            background-color: #6c757d;
        }}
        QPushButton#skipBtn {{
            background-color: #6c757d;
            color: white;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
        }}
        QPushButton#skipBtn:hover {{
            background-color: #545b62;
        }}
        QPushButton#manualDownloadBtn {{
            background-color: #007bff;
            color: white;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
        }}
        QPushButton#manualDownloadBtn:hover {{
            background-color: #0056b3;
        }}
        QTextEdit, QLineEdit, QComboBox {{
            background-color: #1e293b;
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 6px;
        }}
        QFrame#versionBox {{
            background-color: #0d2b32;
            border-radius: 10px;
            padding: 12px;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid #334155;
            border-radius: 50px;
            background-color: transparent;
        }}
        QCheckBox::indicator:checked {{
            background-color: #05ff8f;
        }}
        QComboBox {{
            background-color: #1e293b;
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 6px;   
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: #334155;
            border-left-style: solid;
        }}
        QComboBox::down-arrow {{
            image: url("{arrow_icon_path}");
            width: 16px;
            height: 16px;
        }}
        QSlider::groove:horizontal {{
            background: #334155;
            height: 8px;
            border-radius: 4px;
        }}
        QSlider::sub-page:horizontal {{
            background: #05ff8f;
            height: 8px;
            border-radius: 4px;
        }}
        QSlider::handle:horizontal {{
            background: #05df60;
            height: 16px;
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }}
        QCheckBox {{
            color: #e2e8f0;
            font-size: 14px;
        }}
        QRadioButton {{
            color: #e2e8f0;
            font-size: 14px;
        }}
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 8px;
            background-color: transparent;
        }}
        QRadioButton::indicator:checked {{
            background-color: #05ff8f;
        }}
        QListWidget {{
            background-color: #1e293b;
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 6px;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 12px;
            padding: 6px;
            selection-background-color: #4299e1;
            outline: none;
        }}
        QListWidget::item {{
            padding: 6px 8px;
            border-bottom: 1px solid #4a5568;
            min-height: 20px;
            word-wrap: break-word;
        }}
        QListWidget::item:hover {{
            background-color: #4a5568;
        }}
        QListWidget::item:selected {{
            background-color: #4299e1;
            color: #ffffff;
        }}    
        QProgressBar {{
            border: 2px solid #4299e1;
            border-radius: 6px;
            text-align: center;
            height: 20px;
            background-color: #334155;
            color: #fff;
            font-weight: bold;
        }}
        QProgressBar::chunk {{
            background-color: #4299e1;
            border-radius: 5px;
        }}     
    """)
