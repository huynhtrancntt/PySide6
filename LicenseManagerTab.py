from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGroupBox, QSizePolicy,
    QTabWidget
)
from PySide6.QtCore import Qt
import sys


class LicenseTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # GroupBox license
        group_box = QGroupBox("Quản lý License")
        # group_box.setMaximumWidth(800)
        group_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        group_layout = QVBoxLayout()

        info_label = QLabel(
            '<b>Trạng thái License:</b> ✅ Hợp lệ | '
            '<b>Loại:</b> AI360PRO | '
            '<b>Hết hạn:</b> 2025-08-11 | '
            '<b>Lượt còn:</b> 200'
        )
        info_label.setWordWrap(True)
        group_layout.addWidget(info_label)

        input_layout = QHBoxLayout()
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Nhập mã kích hoạt tại đây")
        self.input_code.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        btn_activate = QPushButton("Kích hoạt")
        btn_activate.setFixedWidth(80)

        input_layout.addWidget(self.input_code)
        input_layout.addWidget(btn_activate)

        group_layout.addLayout(input_layout)
        group_box.setLayout(group_layout)

        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: white;
                border: 1px solid #555;
                margin-top: 10px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
        """)

        # Căn giữa theo chiều ngang
        center_layout = QVBoxLayout()
        self.title1 = QLabel("Quản lý phần Top")
        layout.addWidget(self.title1)
        # center_layout.addStretch()
        center_layout.addWidget(group_box)
        center_layout.addStretch()

        layout.addLayout(center_layout)
        layout.addStretch()

        self.title2 = QLabel("Quản lý phần mềm")

        layout.addWidget(self.title2)


class OtherTab(QWidget):

    def __init__(self, v):

        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel(f"Đây là Tab {v} - Nội dung khác")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý phần mềm")
        self.setMinimumSize(700, 300)
        self.setStyleSheet(
            "background-color: #2b2b2b; font-size: 14px; color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Tạo tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(LicenseTab(), "License")
        self.tabs.addTab(OtherTab(1), "Vieo Downloader")
        self.tabs.addTab(OtherTab(2), "Text to Speech")
        self.tabs.addTab(OtherTab(3), "Dịch thuật")
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                font-weight: bold;
                color: white;
                margin-top: 10px;
                border: none;
                padding: 8px;
                border-bottom: 1px solid #555;
            }
            QTabBar::tab:selected {
               border-bottom: 1px solid #FF0000;
            }
                                """)

        # self.tabs.addTab(OtherTab(4), "Khác 3")
        self.title = QLabel("Quản lý phần mềm")
        layout.addWidget(self.tabs)
        layout.addWidget(self.title)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
