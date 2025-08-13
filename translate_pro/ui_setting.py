# File: Ui_setting.py
from PySide6.QtWidgets import QMessageBox
import sys
import os
from pathlib import Path
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


def resource_path(rel: str) -> str:
    if hasattr(sys, "_MEIPASS"):         # PyInstaller
        base = Path(sys._MEIPASS)
    elif "__compiled__" in globals():     # Nuitka onefile
        base = Path(os.path.dirname(sys.argv[0]))
    else:
        base = Path(os.path.abspath("."))
    return str(base / rel)


def show_about_ui(self):
    about_text = ABOUT_TEMPLATE.format(version=self.version)
    QMessageBox.about(self, "Về ứng dụng", about_text)


def _init_addStyle(self):
    arrow_icon_path = resource_path("images/down-arrow.png").replace("\\", "/")

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
        QTabBar::tab {{
                font-weight: bold;
                color: white;
                margin-top: 10px;
                padding: 8px;
                border: none; /* Bỏ toàn bộ viền */
            }}
            QTabBar::tab:selected {{
               border-bottom: 1px solid #28a745;
            }}
            QTabWidget::pane {{
    border: none;       /* Bỏ toàn bộ viền khung */
    outline: none;      /* Bỏ viền focus */
}}
            QGroupBox {{
             border: 1px solid #334155;      /* Màu viền */
            border-radius: 8px;             /* Bo góc */
            margin-top: 10px;               /* Khoảng cách tiêu đề xuống nội dung */
            padding: 10px;                   /* Khoảng cách trong */
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;  /* Vị trí tiêu đề */
                padding: 0 5px;                 /* Khoảng cách giữa chữ và viền */
                /* color: #FFD700;*/                 /* Màu chữ tiêu đề */
            }}

            QPushButton#btn_refresh{{
                background: #151b2b;
            }}
            QPushButton#btn_refresh {{
            background: transparent;
            color: #e5e7eb;
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 16px;
            min-width: 20px;
            min-height: 20px;
        }}
        QPushButton#btn_refresh:hover {{
    background: rgba(255,255,255,0.06);
}}
QPushButton#btn_refresh:pressed {{
    background: rgba(255,255,255,0.10);
}}

/* ----- Player container ----- */
#PlayerPanel {{
    background: #151b2b;            /* nền tối */
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 8px;
}}

/* ----- Nút play/pause tròn, không nền xanh ----- */
QPushButton#PlayerPlay {{
    background: transparent;
    color: #e5e7eb;
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 16px;
    min-width: 32px;
    min-height: 32px;
}}
QPushButton#PlayerPlay:hover {{
    background: rgba(255,255,255,0.06);
}}
QPushButton#PlayerPlay:pressed {{
    background: rgba(255,255,255,0.10);
}}

/* ----- Thanh seek (tiến trình) ----- */
QSlider#PlayerSeek::groove:horizontal {{
    height: 6px;
    background: #2a3042;            /* rãnh xám */
    border: none;
    border-radius: 3px;
}}
QSlider#PlayerSeek::sub-page:horizontal {{
    background: #8b95a7;            /* phần đã chạy */
    border: none;
    border-radius: 3px;
}}
QSlider#PlayerSeek::add-page:horizontal {{
    background: #2a3042;            /* phần chưa chạy */
    border: none;
    border-radius: 3px;
}}
QSlider#PlayerSeek::handle:horizontal {{
    width: 14px;
    margin: -5px 0;                 /* nhô ra giữa rãnh */
    border-radius: 7px;
    background: #cbd5e1;            /* nút kéo xám nhạt */
    border: 2px solid #64748b;      /* viền xám xanh */
}}

/* ----- Thanh volume (nhỏ, gọn) ----- */
QSlider#PlayerVol {{
    max-width: 140px;
}}
QSlider#PlayerVol::groove:horizontal {{
    height: 6px;
    background: #22c55e;
    border: none;
    border-radius: 3px;
}}
QSlider#PlayerVol::sub-page:horizontal {{
    background: #22c55e;            /* xanh lá dịu (có thể đổi) */
    border: none;
    border-radius: 3px;
}}
QSlider#PlayerVol::add-page:horizontal {{
    background: #2a3042;
    border: none;
    border-radius: 3px;
}}
QSlider#PlayerVol::handle:horizontal {{
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
    background: #e2e8f0;
    border: 2px solid #16a34a;      /* viền xanh lá dịu */
}}

/* Nhãn thời gian */
QLabel {{
    color: #e5e7eb;
}}


    """)
