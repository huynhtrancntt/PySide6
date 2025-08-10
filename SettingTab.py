from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QComboBox, QTabWidget, QFormLayout, QGroupBox
)
from PySide6.QtCore import Qt
import sys


class SettingTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()

        # Dịch vụ
        self.service_combo = QComboBox()
        self.service_combo.addItems(
            ["OpenAI (ChatGPT)", "Google Translate", "Other"])
        layout.addRow("Dịch vụ:", self.service_combo)

        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Dán API Key của bạn vào đây")
        layout.addRow("OpenAI API Key:", self.api_key_input)

        # Ngôn ngữ nguồn và đích
        lang_layout = QHBoxLayout()
        self.source_lang = QComboBox()
        self.source_lang.addItems(
            ["Auto Detect", "Vietnamese", "English", "Japanese"])
        self.target_lang = QComboBox()
        self.target_lang.addItems(
            ["English", "Vietnamese", "Japanese", "Chinese"])
        lang_layout.addWidget(self.source_lang)
        lang_layout.addWidget(QLabel("Ngôn ngữ đích:"))
        lang_layout.addWidget(self.target_lang)

        layout.addRow("Ngôn ngữ nguồn:", lang_layout)
        self.setLayout(layout)


class TranslateTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Label group
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

        # Prompt
        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText(
            "Nhập prompt tại đây để định hướng phong cách dịch (ví dụ: Dịch câu sang tiếng Việt theo phong cách cổ trang...)"
        )
        layout.addWidget(QLabel("Prompt Tùy chỉnh cho các mô hình AI:"))
        layout.addWidget(self.prompt_text)

        # Button
        self.translate_button = QPushButton("Dịch văn bản")
        self.translate_button.setStyleSheet(
            "background-color: #2196F3; color: white; padding: 6px;")
        layout.addWidget(self.translate_button)

        self.setLayout(layout)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dịch AI - Giao diện Demo")
        self.setMinimumSize(800, 500)
        self.setStyleSheet(
            "background-color: #2b2b2b; color: white; font-size: 13px;")

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tabs.addTab(SettingTab(), "Cài đặt chung")
        self.tabs.addTab(TranslateTab(), "Dịch Văn bản / Prompt Tùy chỉnh")

        layout.addWidget(self.tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
