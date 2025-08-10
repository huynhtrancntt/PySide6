from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGroupBox, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
import sys


class LicenseManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý License")
        self.setMinimumSize(600, 200)
        self.setStyleSheet(
            "background-color: #2b2b2b; font-size: 14px; color: white;")
        self.init_ui()

    def init_ui(self):
        # Layout chính dàn theo chiều dọc
        main_layout = QVBoxLayout(self)

        # GroupBox giới hạn chiều rộng
        group_box = QGroupBox("Quản lý License")
        # group_box.setMaximumWidth(800)
        # group_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        group_layout = QVBoxLayout()

        # Label trạng thái
        info_label = QLabel(
            '<b>Trạng thái License:</b> ✅ Hợp lệ | '
            '<b>Loại:</b> AI360PRO | '
            '<b>Hết hạn:</b> 2025-08-11 | '
            '<b>Lượt còn:</b> 200'
        )
        info_label.setWordWrap(True)
        group_layout.addWidget(info_label)

        # Layout nhập mã kích hoạt
        input_layout = QHBoxLayout()
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Nhập mã kích hoạt tại đây")
        # self.input_code.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        btn_activate = QPushButton("Kích hoạt")
        # btn_activate.setFixedWidth(80)
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

        # Dùng layout bao ngoài để căn giữa theo chiều ngang, nhưng đẩy lên top
        top_layout = QHBoxLayout()
        # top_layout.addStretch()
        top_layout.addWidget(group_box)
        # top_layout.addStretch()

        main_layout.addLayout(top_layout)
        main_layout.addStretch()  # đẩy layout group_box lên top


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LicenseManager()
    window.show()
    sys.exit(app.exec())
