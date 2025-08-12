# app.py - PySide6 Hello App
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox

APP_VERSION = "1.0.0"


class HelloWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hello PySide6")
        layout = QVBoxLayout(self)

        self.label = QLabel("Xin chào! 👋", self)
        self.btn = QPushButton("Xem phiên bản", self)
        self.btn.clicked.connect(self.show_version)

        layout.addWidget(self.label)
        layout.addWidget(self.btn)

    def show_version(self):
        QMessageBox.information(self, "Version", f"Phiên bản: {APP_VERSION}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = HelloWindow()
    w.resize(300, 120)
    w.show()
    sys.exit(app.exec())

# python -m nuitka app.py ^
#   --standalone ^
#   --enable-plugin=pyside6 ^
#   --windows-console-mode=disable ^
#   --output-dir=build ^
#   --onefile
