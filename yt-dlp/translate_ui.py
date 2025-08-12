# file: translate_ui.py
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QComboBox, QPushButton, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt
from deep_translator import GoogleTranslator

LANGS = [
    ("Tự phát hiện", "auto"),
    ("Tiếng Việt", "vi"),
    ("Tiếng Anh", "en"),
    ("Tiếng Nhật", "ja"),
    ("Tiếng Trung", "zh-CN"),
    ("Tiếng Hàn", "ko"),
    ("Tiếng Pháp", "fr"),
    ("Tiếng Đức", "de"),
    ("Tiếng Tây Ban Nha", "es"),
    ("Tiếng Bồ Đào Nha", "pt"),
    ("Tiếng Thái", "th"),
]


def code_by_name(name: str) -> str:
    for n, c in LANGS:
        if n == name:
            return c
    return "auto"


class TranslateUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Dịch (Python · PySide6)")
        self.setMinimumSize(900, 600)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)

        # Hàng chọn ngôn ngữ
        row_lang = QHBoxLayout()
        self.src_combo = QComboBox()
        self.tgt_combo = QComboBox()
        self.src_combo.addItems([n for n, _ in LANGS])
        self.tgt_combo.addItems([n for n, _ in LANGS])
        self.src_combo.setCurrentText("Tự phát hiện")
        self.tgt_combo.setCurrentText("Tiếng Việt")

        swap_btn = QPushButton("↔ Đổi chiều")
        swap_btn.clicked.connect(self.swap_lang)

        row_lang.addWidget(QLabel("Nguồn:"))
        row_lang.addWidget(self.src_combo, 2)
        row_lang.addWidget(QLabel("→"))
        row_lang.addWidget(QLabel("Đích:"))
        row_lang.addWidget(self.tgt_combo, 2)
        row_lang.addWidget(swap_btn)

        # Ô nhập & kết quả
        row_edit = QHBoxLayout()
        left = QVBoxLayout()
        right = QVBoxLayout()

        left.addWidget(QLabel("Nhập văn bản:"))
        self.src_text = QTextEdit()
        self.src_text.setPlaceholderText("Dán hoặc gõ nội dung cần dịch…")
        left.addWidget(self.src_text)

        right.addWidget(QLabel("Kết quả dịch:"))
        self.out_text = QTextEdit()
        self.out_text.setReadOnly(True)
        right.addWidget(self.out_text)

        row_edit.addLayout(left, 1)
        row_edit.addLayout(right, 1)

        # Hàng điều khiển
        row_ctrl = QHBoxLayout()
        self.btn_translate = QPushButton("Dịch ngay")
        self.btn_translate.clicked.connect(self.translate_now)

        copy_btn = QPushButton("Copy kết quả")
        copy_btn.clicked.connect(self.copy_result)

        clear_btn = QPushButton("Xóa")
        clear_btn.clicked.connect(self.clear_all)

        row_ctrl.addStretch()
        row_ctrl.addWidget(self.btn_translate)
        row_ctrl.addWidget(copy_btn)
        row_ctrl.addWidget(clear_btn)

        # Dòng nhập nhanh đổi ngôn ngữ đích
        quick_row = QHBoxLayout()
        self.quick_tgt = QLineEdit()
        self.quick_tgt.setPlaceholderText(
            "Nhập mã ngôn ngữ đích (vd: en, vi, ja…) rồi Enter")
        self.quick_tgt.returnPressed.connect(self.set_target_code)
        quick_row.addWidget(QLabel("Mã đích:"))
        quick_row.addWidget(self.quick_tgt)

        # Ghép Layout
        root.addLayout(row_lang)
        root.addLayout(row_edit)
        root.addLayout(row_ctrl)
        root.addLayout(quick_row)

        # Style nhẹ
        self.setStyleSheet("""
        QLabel { font-size: 14px; }
        QTextEdit, QLineEdit { font-size: 14px; }
        QPushButton { padding: 8px 16px; font-weight: 600; }
        """)

    def swap_lang(self):
        s = self.src_combo.currentText()
        t = self.tgt_combo.currentText()
        # không cho "Tự phát hiện" làm đích
        if s == "Tự phát hiện":
            QMessageBox.information(self, "Thông báo",
                                    "Không thể đặt 'Tự phát hiện' làm ngôn ngữ đích.")
            return
        self.src_combo.setCurrentText(t)
        self.tgt_combo.setCurrentText(s)

    def set_target_code(self):
        code = self.quick_tgt.text().strip()
        if not code:
            return
        # tìm tên theo code
        found = None
        for name, c in LANGS:
            if c.lower() == code.lower():
                found = name
                break
        if found:
            self.tgt_combo.setCurrentText(found)
        else:
            QMessageBox.warning(self, "Sai mã",
                                f"Không tìm thấy mã ngôn ngữ: {code}")
        self.quick_tgt.clear()

    def translate_now(self):
        text = self.src_text.toPlainText().strip()
        if not text:
            QMessageBox.information(
                self, "Thiếu nội dung", "Hãy nhập văn bản cần dịch.")
            return
        src = code_by_name(self.src_combo.currentText())
        tgt = code_by_name(self.tgt_combo.currentText())
        if tgt == "auto":
            QMessageBox.information(self, "Thông báo",
                                    "Ngôn ngữ đích không thể là 'Tự phát hiện'. Hãy chọn ngôn ngữ cụ thể.")
            return
        self.btn_translate.setEnabled(False)
        self.btn_translate.setText("Đang dịch…")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            translated = GoogleTranslator(
                source=src, target=tgt).translate(text)
            self.out_text.setPlainText(translated)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi dịch", f"Không thể dịch:\n{e}")
        finally:
            QApplication.restoreOverrideCursor()
            self.btn_translate.setEnabled(True)
            self.btn_translate.setText("Dịch ngay")

    def copy_result(self):
        result = self.out_text.toPlainText().strip()
        if result:
            QApplication.clipboard().setText(result)
            QMessageBox.information(
                self, "Đã copy", "Đã sao chép kết quả vào clipboard.")
        else:
            QMessageBox.information(self, "Trống", "Chưa có kết quả để copy.")

    def clear_all(self):
        self.src_text.clear()
        self.out_text.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TranslateUI()
    w.show()
    sys.exit(app.exec())
