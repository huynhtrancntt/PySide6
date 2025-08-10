from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QScrollArea, QFrame, QTextEdit, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect
import sys
from datetime import datetime


class ToastMessage(QWidget):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 60)
        self.setParent(parent)
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.Widget)  # ✅ bên trong cửa sổ
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setStyleSheet("""
        QWidget {
            background-color: #101828;
            border: 1px solid rgba(0, 227, 150, 0.6); /* viền xanh nhạt */
            border-radius: 10px;
        }
        QLabel {
            color: white;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton {
            background: transparent;
            color: #888;
            border: none;
            font-size: 16px;
        }
        QPushButton:hover {
            color: white;
        }
        QProgressBar {
            background-color: transparent;
            border: none;
            height: 3px;
        }
        QProgressBar::chunk {
            background-color: #00e396;
            border-radius: 1px;
        }
    """)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)

        self.label = QLabel("✅ " + message)
        self.close_btn = QPushButton("✕")
        self.close_btn.clicked.connect(self.close)

        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.close_btn)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(layout)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(4)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(
            "QProgressBar::chunk { background-color: #becc71; }")

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


class HistoryItem(QFrame):
    def __init__(self, text, timestamp, lang="vi-VN"):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #1e1e2f;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 6px;
            }
            QLabel {
                color: white;
            }
        """)
        layout = QVBoxLayout()
        preview = QLabel(text)
        preview.setWordWrap(True)

        bottom = QHBoxLayout()
        time_label = QLabel(f"{timestamp} • {lang}")
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedWidth(30)
        delete_btn.setStyleSheet(
            "color: red; background: transparent; border: none;")

        bottom.addWidget(time_label)
        bottom.addStretch()
        bottom.addWidget(delete_btn)

        layout.addWidget(preview)
        layout.addLayout(bottom)
        self.setLayout(layout)


class HistoryPanel(QWidget):
    def __init__(self, close_callback=None, toast_callback=None, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)
        self.setStyleSheet("background-color: #12131c;")
        self.close_callback = close_callback
        self.toast_callback = toast_callback

        layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        title = QLabel("Lịch sử chuyển đổi")
        title.setStyleSheet("color: white; font-weight: bold;")
        close_btn = QPushButton("✕")
        close_btn.setFixedWidth(30)
        close_btn.setStyleSheet(
            "color: white; background: transparent; border: none;")
        close_btn.clicked.connect(self.close_panel)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)

        layout.addLayout(header_layout)

        clear_btn = QPushButton("🗑️ Xóa tất cả")
        clear_btn.setStyleSheet(
            "background-color: #8a0000; color: white; border-radius: 4px; padding: 4px;")
        clear_btn.clicked.connect(self.handle_clear_all)
        layout.addWidget(clear_btn)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.history_layout = QVBoxLayout(container)

        now = datetime.now().strftime("%H:%M %d/%m/%Y")
        for _ in range(100):
            item = HistoryItem(
                f"J2TEAM Community là nhóm cộng đồng dành cho người dùng Samsung... {_}",
                now
            )
            self.history_layout.addWidget(item)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        self.hide()

    def handle_clear_all(self):
        if self.toast_callback:
            self.toast_callback("Đã xóa lịch sử")

    def show_with_animation(self, parent_width):
        self.show()
        start_x = parent_width
        end_x = parent_width - self.width()
        self.setGeometry(start_x, 0, self.width(), self.parent().height())

        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(start_x, 0, self.width(), self.height()))
        self.anim.setEndValue(QRect(end_x, 0, self.width(), self.height()))
        self.anim.start()

    def close_panel(self):
        parent_width = self.parent().width()
        start_x = self.x()
        end_x = parent_width

        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(start_x, 0, self.width(), self.height()))
        self.anim.setEndValue(QRect(end_x, 0, self.width(), self.height()))
        self.anim.finished.connect(self.hide)
        self.anim.start()

        if self.close_callback:
            self.close_callback()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J2TEAM - Text to Speech (v1.1.1)")
        self.setMinimumSize(800, 500)
        self.setStyleSheet(
            "background-color: #1a1c24; color: white; font-size: 13px;")

        self.main_layout = QHBoxLayout(self)

        self.main_ui = QWidget()
        main_ui_layout = QVBoxLayout(self.main_ui)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Nhập văn bản để chuyển đổi...")

        self.convert_btn = QPushButton("🔁 Chuyển đổi")
        self.convert_btn.setStyleSheet(
            "background-color: #4CAF50; padding: 8px; color: white;")
        self.convert_btn.clicked.connect(self.show_history_panel)

        main_ui_layout.addWidget(self.text_input)
        main_ui_layout.addWidget(self.convert_btn)
        main_ui_layout.addStretch()

        self.history_panel = HistoryPanel(
            close_callback=self.hide_history_panel,
            toast_callback=self.show_toast_message,
            parent=self
        )

        self.main_layout.addWidget(self.main_ui)
        self.main_layout.addWidget(self.history_panel)

    def show_history_panel(self):
        self.main_ui.setDisabled(True)
        self.history_panel.show_with_animation(self.width())

    def hide_history_panel(self):
        self.main_ui.setDisabled(False)

    def show_toast_message(self, message):
        toast = ToastMessage(message, self)

        toast.move(self.width() - toast.width() - 20, 20)  # 🔁 Top-right
        toast.show()
        toast.raise_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
