from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, QLabel,
                               QVBoxLayout, QHBoxLayout, QProgressBar)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation
import sys


class ToastMessage(QWidget):
    def __init__(self, message, parent=None, type="success"):
        super().__init__(parent)
        self.setFixedSize(320, 60)
        self.setParent(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Widget)
        self.setAttribute(Qt.WA_TranslucentBackground)

        type_config = {
            "success": {"color": "#22c55e", "icon": "✔", "bg": "#1e293b"},
            "error": {"color": "#ef4444", "icon": "⨉", "bg": "#1e293b"},
            "warning": {"color": "#eab308", "icon": "⚠", "bg": "#1e293b"}
        }

        config = type_config.get(type, type_config["success"])
        color = config["color"]
        icon = config["icon"]
        bg = config["bg"]

        self.setStyleSheet(f"""
            QWidget{{
                background-color: {bg};

            }}
            QLabel {{
                color: white;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton {{
                background: transparent;
                color: #94a3b8;
                border: none;
                font-size: 14px;
            }}
            QPushButton:hover {{
                color: white;
            }}
            QProgressBar {{
                background-color: transparent;
                border: none;
                height: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 1px;
            }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 0)
        layout_widget = QWidget()
        layout_widget.setObjectName("layout_widget")
        # layout_widget.setStyleSheet("background-color: #0f766e;")
        layout_widget.setLayout(layout)

        self.label = QLabel(
            f'<span style="color:{color}; font-size:16px;">{icon}</span>  {message}')
        self.close_btn = QPushButton("✕")
        self.close_btn.clicked.connect(self.close)

        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.close_btn)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 4, 8, 8)
        main_layout.addWidget(layout_widget)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(4)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)

        main_layout.addWidget(self.progress)

        self.setWindowOpacity(0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(20)
        self.progress_value = 0

    def update_progress(self):
        self.progress_value += 1
        self.progress.setValue(self.progress_value)
        if self.progress_value >= 100:
            self.timer.stop()
            self.fade_out = QPropertyAnimation(self, b"windowOpacity")
            self.fade_out.setDuration(500)
            self.fade_out.setStartValue(1)
            self.fade_out.setEndValue(0)
            self.fade_out.finished.connect(self.close)
            self.fade_out.start()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo Toast")
        self.resize(500, 300)

        btn_success = QPushButton("Hiện Toast Thành Công")
        btn_success.clicked.connect(
            lambda: self.show_toast_message("Thành công!", "success"))

        btn_error = QPushButton("Hiện Toast Lỗi")
        btn_error.clicked.connect(
            lambda: self.show_toast_message("Lỗi rồi!", "error"))

        btn_warning = QPushButton("Hiện Toast Cảnh báo")
        btn_warning.clicked.connect(
            lambda: self.show_toast_message("Cẩn thận!", "warning"))

        layout = QVBoxLayout()
        layout.addWidget(btn_success)
        layout.addWidget(btn_error)
        layout.addWidget(btn_warning)

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

    def show_toast_message(self, message, type="success"):
        toast = ToastMessage(message, self, type=type)
        toast.move(self.width() - toast.width() - 20, 20)
        toast.show()
        toast.raise_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
