import sys
import json
import os
import time
from pathlib import Path
from typing import List, Dict

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QComboBox, QPushButton, QLineEdit, QMessageBox, QListWidget, QListWidgetItem,
    QCheckBox, QFileDialog, QSplitter, QFrame, QToolButton
)
from PySide6.QtCore import Qt, QTimer, QSettings, QSize
from PySide6.QtGui import QKeySequence, QShortcut

from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
import pyttsx3

DetectorFactory.seed = 0  # langdetect ổn định hơn

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
    ("Tiếng Nga", "ru"),
    ("Tiếng Ý", "it"),
]

HOME = Path.home()
DATA_DIR = HOME / ".translate_pro"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_PATH = DATA_DIR / "history.json"


def code_by_name(name: str) -> str:
    for n, c in LANGS:
        if n == name:
            return c
    return "auto"


def name_by_code(code: str) -> str:
    for n, c in LANGS:
        if c.lower() == code.lower():
            return n
    return code


class TTS:
    """Bọc đơn giản cho pyttsx3 (offline)."""

    def __init__(self):
        self.engine = pyttsx3.init()
        # bạn có thể tinh chỉnh voice mặc định tại đây nếu cần
        # for v in self.engine.getProperty('voices'): print(v.id)
        self.engine.setProperty('rate', 180)

    def speak(self, text: str):
        if not text.strip():
            return
        self.engine.stop()
        self.engine.say(text)
        self.engine.runAndWait()


class TranslatePro(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Dịch Pro (PySide6)")
        self.setMinimumSize(1100, 650)

        self.tts = TTS()
        self.history: List[Dict] = self.load_history()

        self.debounce = QTimer(self)
        self.debounce.setSingleShot(True)
        self.debounce.setInterval(450)  # ms
        self.debounce.timeout.connect(self.translate_now)

        self._build_ui()
        self._wire_shortcuts()
        self.load_settings()
        self.refresh_history_list()

    # ---------- UI ----------
    def _build_ui(self):
        root = QHBoxLayout(self)

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter)

        # Sidebar: lịch sử
        side = QWidget()
        side_layout = QVBoxLayout(side)
        side_layout.setContentsMargins(8, 8, 8, 8)

        header = QHBoxLayout()
        header.addWidget(QLabel("🕘 Lịch sử"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Tìm trong lịch sử…")
        self.search_box.textChanged.connect(self.refresh_history_list)
        header.addWidget(self.search_box)
        side_layout.addLayout(header)

        self.list_history = QListWidget()
        self.list_history.itemSelectionChanged.connect(self.fill_from_history)
        side_layout.addWidget(self.list_history, 1)

        btn_row = QHBoxLayout()
        self.btn_export = QPushButton("Xuất JSON")
        self.btn_export.clicked.connect(self.export_history)
        self.btn_clear_his = QPushButton("Xóa lịch sử")
        self.btn_clear_his.clicked.connect(self.clear_history)
        btn_row.addWidget(self.btn_export)
        btn_row.addWidget(self.btn_clear_his)
        side_layout.addLayout(btn_row)

        # Main area
        main = QWidget()
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # Hàng ngôn ngữ
        lang_row = QHBoxLayout()
        self.src_combo = QComboBox()
        self.tgt_combo = QComboBox()
        self.src_combo.addItems([n for n, _ in LANGS])
        self.tgt_combo.addItems([n for n, _ in LANGS])
        self.src_combo.setCurrentText("Tự phát hiện")
        self.tgt_combo.setCurrentText("Tiếng Việt")

        swap_btn = QPushButton("↔ Đổi chiều (Ctrl+K)")
        swap_btn.clicked.connect(self.swap_lang)

        self.chk_auto = QCheckBox("Dịch khi gõ")
        self.chk_auto.setChecked(True)

        lang_row.addWidget(QLabel("Nguồn:"))
        lang_row.addWidget(self.src_combo, 2)
        lang_row.addSpacing(6)
        lang_row.addWidget(QLabel("Đích:"))
        lang_row.addWidget(self.tgt_combo, 2)
        lang_row.addSpacing(6)
        lang_row.addWidget(self.chk_auto)
        lang_row.addWidget(swap_btn)

        # Soạn thảo
        editors = QHBoxLayout()
        left_box = QVBoxLayout()
        right_box = QVBoxLayout()

        # Thanh công cụ nhỏ phía trên ô nguồn
        src_bar = QHBoxLayout()
        src_bar.addWidget(QLabel("Nhập văn bản:"))
        self.lbl_src_count = QLabel("0 ký tự")
        src_bar.addStretch()
        btn_paste = QToolButton()
        btn_paste.setText("Dán")
        btn_paste.clicked.connect(self.paste_clipboard)
        btn_open = QToolButton()
        btn_open.setText("Mở .txt")
        btn_open.clicked.connect(self.open_text_file)
        btn_say_src = QToolButton()
        btn_say_src.setText("Đọc")
        btn_say_src.clicked.connect(
            lambda: self.tts.speak(self.src_text.toPlainText()))
        src_bar.addWidget(self.lbl_src_count)
        src_bar.addWidget(btn_paste)
        src_bar.addWidget(btn_open)
        src_bar.addWidget(btn_say_src)

        left_box.addLayout(src_bar)
        self.src_text = QTextEdit()
        self.src_text.setPlaceholderText(
            "Gõ, dán văn bản hoặc kéo-thả file .txt vào đây…")
        self.src_text.textChanged.connect(self.on_src_changed)
        self.src_text.setAcceptDrops(True)
        left_box.addWidget(self.src_text, 1)

        # Thanh công cụ nhỏ phía trên ô kết quả
        out_bar = QHBoxLayout()
        out_bar.addWidget(QLabel("Kết quả dịch:"))
        self.lbl_out_count = QLabel("0 ký tự")
        out_bar.addStretch()
        btn_copy = QToolButton()
        btn_copy.setText("Copy")
        # btn_copy.clicked.connect(self.copy_result)
        btn_save = QToolButton()
        btn_save.setText("Lưu .txt")
        btn_save.clicked.connect(self.save_result_file)
        btn_say_out = QToolButton()
        btn_say_out.setText("Đọc")
        btn_say_out.clicked.connect(
            lambda: self.tts.speak(self.out_text.toPlainText()))
        out_bar.addWidget(self.lbl_out_count)
        out_bar.addWidget(btn_copy)
        out_bar.addWidget(btn_save)
        out_bar.addWidget(btn_say_out)

        right_box.addLayout(out_bar)
        self.out_text = QTextEdit()
        self.out_text.setReadOnly(False)  # cho phép chỉnh tay nếu muốn
        right_box.addWidget(self.out_text, 1)

        editors.addLayout(left_box, 1)
        # đường kẻ dọc
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        editors.addWidget(line)
        editors.addLayout(right_box, 1)

        # Nút hành động
        actions = QHBoxLayout()
        self.btn_translate = QPushButton("Dịch ngay (Ctrl+Enter)")
        self.btn_translate.clicked.connect(self.translate_now)
        self.btn_clipboard = QPushButton("Dịch Clipboard (Ctrl+L)")
        self.btn_clipboard.clicked.connect(self.translate_clipboard)
        self.quick_tgt = QLineEdit()
        self.quick_tgt.setPlaceholderText(
            "Nhập mã ngôn ngữ đích (vi, en, ja…) rồi Enter")
        self.quick_tgt.returnPressed.connect(self.set_target_code)

        self.lbl_detected = QLabel("")  # hiển thị mã ngôn ngữ phát hiện
        self.lbl_detected.setMinimumWidth(130)
        actions.addWidget(self.btn_translate)
        actions.addWidget(self.btn_clipboard)
        actions.addStretch()
        actions.addWidget(QLabel("Mã đích:"))
        actions.addWidget(self.quick_tgt)
        actions.addSpacing(8)
        actions.addWidget(QLabel("Phát hiện:"))
        actions.addWidget(self.lbl_detected)

        # Ghép
        main_layout.addLayout(lang_row)
        main_layout.addLayout(editors, 1)
        main_layout.addLayout(actions)

        splitter.addWidget(side)
        splitter.addWidget(main)
        splitter.setSizes([300, 800])

        # Style nhẹ
        self.setStyleSheet("""
        QLabel { font-size: 14px; }
        QTextEdit, QLineEdit, QComboBox { font-size: 14px; }
        QPushButton, QToolButton { padding: 6px 12px; font-weight: 600; }
        QListWidget { font-size: 13px; }
        """)

    def _wire_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Return"), self,
                  activated=self.translate_now)
        QShortcut(QKeySequence("Ctrl+Enter"), self,
                  activated=self.translate_now)
        QShortcut(QKeySequence("Ctrl+K"), self, activated=self.swap_lang)
        QShortcut(QKeySequence("Ctrl+L"), self,
                  activated=self.paste_clipboard_and_translate)

    # ---------- Settings / History ----------
    def load_settings(self):
        s = QSettings("HT", "TranslatePro")
        self.resize(s.value("size", QSize(1100, 650)))
        self.move(s.value("pos", self.pos()))
        tgt = s.value("tgt_name", "Tiếng Việt")
        if tgt in [n for n, _ in LANGS]:
            self.tgt_combo.setCurrentText(tgt)
        auto = s.value("auto", True, type=bool)
        self.chk_auto.setChecked(auto)

    def save_settings(self):
        s = QSettings("HT", "TranslatePro")
        s.setValue("size", self.size())
        s.setValue("pos", self.pos())
        s.setValue("tgt_name", self.tgt_combo.currentText())
        s.setValue("auto", self.chk_auto.isChecked())

    def load_history(self) -> List[Dict]:
        if HISTORY_PATH.exists():
            try:
                return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
            except Exception:
                pass
        return []

    def save_history(self):
        try:
            HISTORY_PATH.write_text(json.dumps(
                self.history, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            QMessageBox.warning(self, "Không thể lưu lịch sử", str(e))

    def refresh_history_list(self):
        kw = self.search_box.text().strip().lower()
        self.list_history.clear()
        for item in reversed(self.history):  # mới nhất lên đầu
            src = item.get("src_text", "")[:80].replace("\n", " ")
            out = item.get("out_text", "")[:80].replace("\n", " ")
            line = f"{name_by_code(item['src_lang'])}→{name_by_code(item['tgt_lang'])} | {src} ⟶ {out}"
            if kw and kw not in line.lower():
                continue
            it = QListWidgetItem(line)
            it.setData(Qt.UserRole, item)
            self.list_history.addItem(it)

    def add_history(self, src_lang, tgt_lang, src_text, out_text):
        if not src_text.strip() and not out_text.strip():
            return
        self.history.append({
            "ts": time.time(),
            "src_lang": src_lang,
            "tgt_lang": tgt_lang,
            "src_text": src_text,
            "out_text": out_text
        })
        # giữ tối đa 1000 mục
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        self.save_history()
        self.refresh_history_list()

    def fill_from_history(self):
        it = self.list_history.currentItem()
        if not it:
            return
        data = it.data(Qt.UserRole)
        self.src_combo.setCurrentText(name_by_code(data["src_lang"]))
        self.tgt_combo.setCurrentText(name_by_code(data["tgt_lang"]))
        self.src_text.setPlainText(data["src_text"])
        self.out_text.setPlainText(data["out_text"])

    # ---------- Actions ----------
    def on_src_changed(self):
        text = self.src_text.toPlainText()
        self.lbl_src_count.setText(f"{len(text)} ký tự")
        if self.chk_auto.isChecked():
            self.debounce.start()

    def paste_clipboard(self):
        self.src_text.setPlainText(QApplication.clipboard().text())

    def paste_clipboard_and_translate(self):
        self.paste_clipboard()
        self.translate_now()

    def translate_clipboard(self):
        self.paste_clipboard()
        self.translate_now()

    def open_text_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Mở tệp văn bản", str(HOME), "Text (*.txt)")
        if path:
            try:
                txt = Path(path).read_text(encoding="utf-8")
            except UnicodeDecodeError:
                txt = Path(path).read_text(encoding="cp1258", errors="ignore")
            self.src_text.setPlainText(txt)

    def save_result_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Lưu kết quả", str(HOME / "translated.txt"), "Text (*.txt)")
        if path:
            Path(path).write_text(self.out_text.toPlainText(), encoding="utf-8")

    def export_history(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Xuất lịch sử", str(HOME / "history.json"), "JSON (*.json)")
        if path:
            Path(path).write_text(json.dumps(self.history,
                                             ensure_ascii=False, indent=2), encoding="utf-8")

    def clear_history(self):
        if QMessageBox.question(self, "Xác nhận", "Xóa toàn bộ lịch sử?") == QMessageBox.Yes:
            self.history = []
            self.save_history()
            self.refresh_history_list()

    def set_target_code(self):
        code = self.quick_tgt.text().strip()
        if not code:
            return
        found = name_by_code(code)
        if found == code:  # không tìm thấy
            QMessageBox.warning(
                self, "Sai mã", f"Không tìm thấy mã ngôn ngữ: {code}")
        else:
            self.tgt_combo.setCurrentText(found)
        self.quick_tgt.clear()

    def swap_lang(self):
        s = self.src_combo.currentText()
        t = self.tgt_combo.currentText()
        if s == "Tự phát hiện":
            QMessageBox.information(
                self, "Thông báo", "Không thể đặt 'Tự phát hiện' làm đích.")
            return
        self.src_combo.setCurrentText(t)
        self.tgt_combo.setCurrentText(s)
        # đảo nội dung luôn cho tiện
        src = self.src_text.toPlainText()
        out = self.out_text.toPlainText()
        if out.strip():
            self.src_text.setPlainText(out)
            self.out_text.setPlainText(src)

    # ---------- Translate ----------
    def translate_now(self):
        text = self.src_text.toPlainText().strip()
        if not text:
            self.out_text.clear()
            self.lbl_out_count.setText("0 ký tự")
            self.lbl_detected.setText("")
            return

        src = code_by_name(self.src_combo.currentText())
        tgt = code_by_name(self.tgt_combo.currentText())
        if tgt == "auto":
            QMessageBox.information(
                self, "Thông báo", "Ngôn ngữ đích không thể là 'Tự phát hiện'.")
            return

        # phát hiện ngôn ngữ để hiển thị (độc lập quá trình dịch)
        detected_code = ""
        try:
            detected_code = detect(text)
        except Exception:
            detected_code = ""
        self.lbl_detected.setText(detected_code or "—")

        self.btn_translate.setEnabled(False)
        self.btn_translate.setText("Đang dịch…")
        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:
            translated = GoogleTranslator(
                source=src, target=tgt).translate(text)
            self.out_text.setPlainText(translated)
            self.lbl_out_count.setText(f"{len(translated)} ký tự")

            # lấy mã thực tế (nếu src=auto thì dùng cái đã detect)
            real_src = src if src != "auto" else (detected_code or "auto")
            self.add_history(real_src, tgt, text, translated)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi dịch", f"Không thể dịch:\n{e}")
        finally:
            QApplication.restoreOverrideCursor()
            self.btn_translate.setEnabled(True)
            self.btn_translate.setText("Dịch ngay")

    # ---------- Qt events ----------
    def closeEvent(self, event):
        self.save_settings()
        return super().closeEvent(event)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            exts = {".txt"}
            for url in e.mimeData().urls():
                if Path(url.toLocalFile()).suffix.lower() in exts:
                    e.acceptProposedAction()
                    return
        e.ignore()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            p = Path(url.toLocalFile())
            if p.suffix.lower() == ".txt":
                try:
                    txt = p.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    txt = p.read_text(encoding="cp1258", errors="ignore")
                self.src_text.setPlainText(txt)
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TranslatePro()
    w.show()
    sys.exit(app.exec())
