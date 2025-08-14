from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QScrollArea, QFrame, QTextEdit, QPlainTextEdit, QProgressBar,
    QMainWindow, QTabWidget, QStatusBar, QLineEdit
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, Signal, QObject
from PySide6.QtGui import QAction, QIntValidator
import sys
from datetime import datetime


# ======================= Toast =======================
class ToastMessage(QWidget):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 60)
        self.setParent(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Widget)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
        QWidget { background-color: #101828; border: 1px solid rgba(0,227,150,.6); border-radius: 10px; }
        QLabel { color: white; font-weight: bold; font-size: 14px; }
        QPushButton { background: transparent; color: #888; border: none; font-size: 16px; }
        QPushButton:hover { color: white; }
        QProgressBar { background-color: transparent; border: none; height: 3px; }
        QProgressBar::chunk { background-color: #00e396; border-radius: 1px; }
        """)
        top = QHBoxLayout()
        top.setContentsMargins(10, 5, 10, 5)
        self.label = QLabel("✅ " + message)
        self.close_btn = QPushButton("✕")
        self.close_btn.clicked.connect(self.close)
        top.addWidget(self.label)
        top.addStretch()
        top.addWidget(self.close_btn)
        root = QVBoxLayout(self)
        root.addLayout(top)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(4)
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        root.addWidget(self.progress)

        self.setWindowOpacity(0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.start()

        self.progress_value = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(20)

    def _tick(self):
        self.progress_value += 1
        self.progress.setValue(self.progress_value)
        if self.progress_value >= 100:
            self.timer.stop()
            fade_out = QPropertyAnimation(self, b"windowOpacity")
            fade_out.setDuration(500)
            fade_out.setStartValue(1)
            fade_out.setEndValue(0)
            fade_out.finished.connect(self.close)
            fade_out.start()


# ======================= History Items =======================
class HistoryItemTab1(QFrame):
    selected = Signal(str)

    def __init__(self, text, timestamp, lang="vi-VN", meta=None):
        super().__init__()
        self._text = text
        self.setStyleSheet("""
            QFrame { background-color: #1e1e2f; border: 1px solid #2f3144; border-radius: 10px; padding: 8px; }
            QLabel { color: #eaeaf0; }
            QPushButton { background: #26283a; color: #cbd0ff; border: 1px solid #3a3d55; border-radius: 6px; padding: 4px 8px; }
            QPushButton:hover { background: #323554; }
        """)
        lay = QVBoxLayout(self)
        preview = QLabel(text)
        preview.setWordWrap(True)
        lay.addWidget(preview)

        bottom = QHBoxLayout()
        pill = QLabel(f"{timestamp} • {lang}")
        pill.setStyleSheet(
            "QLabel{background:#23263a; color:#aeb3ff; border:1px solid #39406a; border-radius:6px; padding:2px 6px;}")
        bottom.addWidget(pill)
        bottom.addStretch()

        self.btn_play = QPushButton("▶")
        self.btn_save = QPushButton("💾")
        self.btn_del = QPushButton("🗑️")
        for b in (self.btn_play, self.btn_save, self.btn_del):
            b.setFixedWidth(34)
        bottom.addWidget(self.btn_play)
        bottom.addWidget(self.btn_save)
        bottom.addWidget(self.btn_del)
        lay.addLayout(bottom)

        self.btn_play.clicked.connect(lambda: self.selected.emit(self._text))

    def mousePressEvent(self, e):
        self.selected.emit(self._text)
        super().mousePressEvent(e)


class HistoryItemTab2(QFrame):
    def __init__(self, text, timestamp, lang="vi-VN", meta=None):
        super().__init__()
        status = (meta or {}).get("status", "Draft")
        value = (meta or {}).get("value", text)
        self.setStyleSheet("""
            QFrame { background-color: #182127; border: 1px solid #27424f; border-radius: 10px; padding: 8px; }
            QLabel { color: #e2f1f8; }
            QPushButton { background: #20303a; color: #d2ecff; border: 1px solid #365868; border-radius: 6px; padding: 4px 8px; }
            QPushButton:hover { background: #294150; }
        """)
        lay = QVBoxLayout(self)

        top = QHBoxLayout()
        title = QLabel("Cấu hình")
        chip = QLabel(status)
        chip.setStyleSheet(
            "QLabel { padding:2px 8px; border-radius:999px; color:#0c2a1d; background:#8ef1c5; font-weight:600; }")
        if status.lower() == "applied":
            chip.setStyleSheet(
                "QLabel { padding:2px 8px; border-radius:999px; color:#0e2a0f; background:#8ff19b; font-weight:600; }")
        elif status.lower() == "auto":
            chip.setStyleSheet(
                "QLabel { padding:2px 8px; border-radius:999px; color:#262a0e; background:#e9f18f; font-weight:600; }")
        top.addWidget(title)
        top.addStretch()
        top.addWidget(chip)
        lay.addLayout(top)

        val = QLabel(value)
        val.setStyleSheet(
            "QLabel{background:#121820; border:1px dashed #3a5666; border-radius:6px; padding:6px;}")
        val.setWordWrap(True)
        lay.addWidget(val)

        bottom = QHBoxLayout()
        t = QLabel(timestamp)
        t.setStyleSheet("QLabel{color:#a9d1e6;}")
        bottom.addWidget(t)
        bottom.addStretch()
        self.btn_edit = QPushButton("✎")
        self.btn_del = QPushButton("🗑️")
        for b in (self.btn_edit, self.btn_del):
            b.setFixedWidth(34)
        bottom.addWidget(self.btn_edit)
        bottom.addWidget(self.btn_del)
        lay.addLayout(bottom)


# ======================= History Panel =======================
class HistoryPanel(QWidget):
    def __init__(self, title_text="Lịch sử", item_factory=None, on_item_selected=None,
                 close_callback=None, toast_callback=None, parent=None):
        super().__init__(parent)
        self.setFixedWidth(330)
        self.setStyleSheet("background-color: #12131c;")
        self.item_factory = item_factory
        self.on_item_selected = on_item_selected
        self.close_callback = close_callback
        self.toast_callback = toast_callback

        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        self.title = QLabel(title_text)
        self.title.setStyleSheet("color: white; font-weight: bold;")
        close_btn = QPushButton("✕")
        close_btn.setFixedWidth(30)
        close_btn.setStyleSheet(
            "color: white; background: transparent; border: none;")
        close_btn.clicked.connect(self.close_panel)
        header.addWidget(self.title)
        header.addStretch()
        header.addWidget(close_btn)
        layout.addLayout(header)

        self.clear_btn = QPushButton("🗑️ Xóa tất cả")
        self.clear_btn.setStyleSheet(
            "background-color: #8a0000; color: white; border-radius: 4px; padding: 4px;")
        self.clear_btn.clicked.connect(self.handle_clear_all)
        layout.addWidget(self.clear_btn)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        container = QWidget()
        self.history_layout = QVBoxLayout(container)
        self.history_layout.addStretch()
        self.scroll.setWidget(container)
        layout.addWidget(self.scroll)
        self.hide()

    def _wire_select_signal(self, item):
        if self.on_item_selected and hasattr(item, "selected"):
            try:
                item.selected.connect(self.on_item_selected)
            except Exception:
                pass

    def add_history(self, text, lang="vi-VN", meta=None):
        now = datetime.now().strftime("%H:%M %d/%m/%Y")
        factory = self.item_factory or (lambda *a, **k: QLabel(str(text)))
        item = factory(text, now, lang, meta or {})
        self._wire_select_signal(item)
        idx = self.history_layout.count() - 1
        self.history_layout.insertWidget(idx, item)

    def preload(self, items_with_meta):
        while self.history_layout.count() > 1:
            it = self.history_layout.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()
        for text, meta in items_with_meta:
            self.add_history(text, meta=meta or {})

    def handle_clear_all(self):
        while self.history_layout.count() > 1:
            it = self.history_layout.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()
        if self.toast_callback:
            self.toast_callback("Đã xóa lịch sử")

    def _calc_top_and_height(self):
        top = 0
        parent = self.parent()
        if hasattr(parent, "menuBar"):
            top = parent.menuBar().height()
        return top, parent.height() - top

    def dock_right(self):
        parent = self.parent()
        top, h = self._calc_top_and_height()
        x = parent.width() - self.width()
        self.setGeometry(x, top, self.width(), h)

    def show_with_animation(self, parent_width):
        self.show()
        top, h = self._calc_top_and_height()
        start_x = parent_width
        end_x = parent_width - self.width()
        self.setGeometry(start_x, top, self.width(), h)
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(start_x, top, self.width(), h))
        self.anim.setEndValue(QRect(end_x, top, self.width(), h))
        self.anim.start()

    def close_panel(self):
        parent_width = self.parent().width()
        top, h = self._calc_top_and_height()
        start_x = self.x()
        end_x = parent_width
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(250)
        self.anim.setStartValue(QRect(start_x, top, self.width(), h))
        self.anim.setEndValue(QRect(end_x, top, self.width(), h))
        self.anim.finished.connect(self.hide)
        self.anim.start()
        if self.close_callback:
            self.close_callback()


# ======================= Overlay =======================
class ClickToCloseOverlay(QWidget):
    clicked_outside = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Widget)
        self.setStyleSheet("background: rgba(0,0,0,0.25);")
        self.hide()

    def mousePressEvent(self, e):
        self.clicked_outside.emit()
        e.accept()


# ======================= HistoryFeature =======================
class HistoryFeature(QObject):
    request_show_history = Signal()
    request_hide_history = Signal()

    def __init__(self, *, parent_main, hist_title, item_factory, toast_cb,
                 on_item_selected=None, preload_list=None):
        super().__init__(parent_main)
        self.btn = QPushButton("🕘 Lịch sử")
        self.btn.setStyleSheet(
            "background-color:#2b2d3a; border:1px solid #444; border-radius:6px; padding:6px;")
        self.btn.clicked.connect(self.request_show_history.emit)
        self.panel = HistoryPanel(
            title_text=hist_title,
            item_factory=item_factory,
            on_item_selected=on_item_selected,
            close_callback=self._on_panel_closed,
            toast_callback=toast_cb,
            parent=parent_main
        )
        if preload_list:
            self.panel.preload(preload_list)

    def _on_panel_closed(self):
        self.request_hide_history.emit()


# ======================= TabBase (logic-only) =======================
class TabBase:
    def __init__(self, parent_main, toast_cb):
        self.parent_main = parent_main
        self.toast_cb = toast_cb
        self.history: HistoryFeature | None = None

    def enable_history(self, *, hist_title, item_factory, on_item_selected=None, preload_list=None) -> HistoryFeature:
        self.history = HistoryFeature(
            parent_main=self.parent_main,
            hist_title=hist_title,
            item_factory=item_factory,
            toast_cb=self.toast_cb,
            on_item_selected=on_item_selected,
            preload_list=preload_list
        )
        return self.history

    def append_history(self, text, *, lang="vi-VN", meta=None):
        if self.history:
            self.history.panel.add_history(text, lang=lang, meta=meta or {})

    def has_history(self) -> bool:
        return self.history is not None

    def current_panel(self):
        return self.history.panel if self.history else None


# ======================= UIToolbarTab (base chỉ có toolbar) =======================
class UIToolbarTab(QWidget):
    def __init__(self, parent_main, *, toast_cb):
        super().__init__()
        self.logic = TabBase(parent_main, toast_cb)
        root = QVBoxLayout(self)
        self.toolbar = QHBoxLayout()
        root.addLayout(self.toolbar)
        root.addStretch()

    @property
    def history(self):
        return self.logic.history

    def add_toolbar_widget(self, w):
        self.toolbar.insertWidget(self.toolbar.count(), w)


# ======================= TTSTab (QPlainTextEdit) =======================
# ======================= TTSTab (QPlainTextEdit) =======================
class TTSTab(UIToolbarTab):
    def __init__(self, parent_main, toast_cb):
        super().__init__(parent_main, toast_cb=toast_cb)

        root = self.layout()  # QVBoxLayout từ UIToolbarTab

        # --- History: bật trước để lấy hist.btn ---
        hist = self.logic.enable_history(
            hist_title="Lịch sử TTSTab",
            item_factory=lambda text, ts, lang, meta: HistoryItemTab1(
                text, ts, lang, meta),
            preload_list=[("TTSTab • Demo 1", None),
                          ("TTSTab • Demo 2", None)],
            on_item_selected=self._pick_history
        )

        # --- Header trên cùng: trái (tiêu đề), phải (nút Lịch sử) ---
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        title = QLabel("TTSTab")
        title.setStyleSheet("font-weight:600;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(hist.btn)  # ⬅️ nút lịch sử ở góc phải trên cùng
        header.addWidget(hist.btn)  # ⬅️ nút lịch sử ở góc phải trên cùng
        root.insertLayout(0, header)

        # --- Body: ô nhập văn bản ---
        body = QVBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        self.text_input = QPlainTextEdit()
        self.text_input.setPlaceholderText(
            "TTSTab • Nhập văn bản (QPlainTextEdit)…")
        body.addWidget(self.text_input)
        root.insertLayout(1, body)

        # --- Toolbar của tab: để nút Chuyển đổi (không để nút lịch sử ở đây nữa) ---
        self.btn_convert = QPushButton("🔁 Chuyển đổi (TTSTab)")
        self.btn_convert.setStyleSheet(
            "background-color:#4CAF50; padding:8px; color:white;")
        self.btn_convert.clicked.connect(self.on_convert_clicked)
        self.toolbar.addWidget(self.btn_convert)
        # (KHÔNG thêm hist.btn vào self.toolbar nữa)

    def on_convert_clicked(self):
        txt = self.text_input.toPlainText().strip() or "(trống)"
        self.logic.append_history(txt)
        pm = self.logic.parent_main
        if hasattr(pm, "text_log"):
            pm.text_log.append("[TTSTab] " + txt[:60])
        if self.logic.toast_cb:
            self.logic.toast_cb("Đã lưu (TTSTab)")

    def _pick_history(self, text: str):
        self.text_input.setPlainText(text)
        self.text_input.setFocus()
        if self.history:
            self.history.request_hide_history.emit()


# ======================= ConvertTab (QTextEdit) + nút tiến trình + Set tiến trình + bố cục lịch sử riêng =======================
class ConvertTab(UIToolbarTab):
    def __init__(self, parent_main, toast_cb):
        super().__init__(parent_main, toast_cb=toast_cb)
        # body chính
        body = QVBoxLayout()
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "ConvertTab • Nhập văn bản (QTextEdit)…")
        body.addWidget(self.text_input)

        # —— Cụm điều khiển tiến trình ngay trong tab ——
        ctrl = QHBoxLayout()
        self.btn_start = QPushButton("▶ Bắt đầu")
        self.btn_pause = QPushButton("⏸ Tạm dừng")
        self.btn_resume = QPushButton("⏯ Tiếp tục")
        self.btn_stop = QPushButton("⏹ Huỷ")
        for b in (self.btn_start, self.btn_pause, self.btn_resume, self.btn_stop):
            b.setStyleSheet(
                "QPushButton{background:#2b2d3a;border:1px solid #444;border-radius:6px;padding:6px;} QPushButton:hover{background:#3a3d4f;}")

        # Kết nối tới MainWindow progress
        pm = self.logic.parent_main
        self.btn_start.clicked.connect(pm.on_start)
        self.btn_pause.clicked.connect(pm.on_pause)
        self.btn_resume.clicked.connect(pm.on_resume)
        self.btn_stop.clicked.connect(pm.on_stop)

        ctrl.addWidget(self.btn_start)
        ctrl.addWidget(self.btn_pause)
        ctrl.addWidget(self.btn_resume)
        ctrl.addWidget(self.btn_stop)
        ctrl.addStretch()

        # —— Ô “Set tiến trình” ——
        self.progress_input = QLineEdit()
        self.progress_input.setPlaceholderText("0–100")
        self.progress_input.setFixedWidth(80)
        self.progress_input.setValidator(QIntValidator(0, 100, self))
        self.btn_set_progress = QPushButton("Set tiến trình")
        self.btn_set_progress.setStyleSheet(
            "QPushButton{background:#32405a;border:1px solid #44597c;border-radius:6px;padding:6px;} QPushButton:hover{background:#3b4e6e;}")
        self.btn_set_progress.clicked.connect(self._on_set_progress)

        ctrl.addWidget(QLabel("Tiến trình:"))
        ctrl.addWidget(self.progress_input)
        ctrl.addWidget(self.btn_set_progress)
        body.addLayout(ctrl)

        # —— Hàng Lịch sử RIÊNG (label trái, nút phải) ——
        hist_row = QHBoxLayout()
        hist_row.addWidget(QLabel("Lịch sử chuyển đổi"))
        hist_row.addStretch()

        hist = self.logic.enable_history(
            hist_title="Lịch sử Chuyển đổi",
            item_factory=lambda text, ts, lang, meta: HistoryItemTab2(
                text, ts, lang, meta),
            preload_list=[("Convert • Mục A", None),
                          ("Convert • Mục B", None)],
            on_item_selected=self._pick_history
        )
        hist_row.addWidget(hist.btn)
        body.addLayout(hist_row)

        # —— Nút Convert riêng của tab ——
        convert_row = QHBoxLayout()
        self.btn_convert = QPushButton("🔁 Chuyển đổi (ConvertTab)")
        self.btn_convert.setStyleSheet(
            "background-color:#4CAF50; padding:8px; color:white;")
        self.btn_convert.clicked.connect(self.on_convert_clicked)
        convert_row.addWidget(self.btn_convert)
        convert_row.addStretch()
        body.addLayout(convert_row)

        # gắn body vào giao diện tab
        self.layout().insertLayout(0, body)

    def _on_set_progress(self):
        txt = self.progress_input.text().strip()
        if txt == "":
            self.logic.toast_cb("Nhập giá trị 0–100")
            return
        try:
            val = int(txt)
        except ValueError:
            self.logic.toast_cb("Giá trị không hợp lệ")
            return
        val = max(0, min(100, val))
        pm = self.logic.parent_main
        pm._progress_value = val
        pm.progress_bar.setValue(val)
        # Nếu đang chạy và set tới 100 -> coi như xong
        if pm._progress_timer.isActive() and val >= 100:
            pm._progress_timer.stop()
            pm.status.showMessage("Hoàn tất!")
            pm.text_log.append("[Progress] Hoàn tất (set từ ConvertTab)")
            pm.btn_start.setEnabled(True)
            pm.btn_pause.setEnabled(False)
            pm.btn_resume.setEnabled(False)
            pm.btn_stop.setEnabled(False)
        else:
            pm.status.showMessage(f"Đã set tiến trình: {val}%")
            pm.text_log.append(f"[Progress] Set {val}% (ConvertTab)")

    def on_convert_clicked(self):
        txt = self.text_input.toPlainText().strip() or "(trống)"
        self.logic.append_history(txt)
        pm = self.logic.parent_main
        if hasattr(pm, "text_log"):
            pm.text_log.append("[ConvertTab] " + txt[:60])
        if self.logic.toast_cb:
            self.logic.toast_cb("Đã lưu (ConvertTab)")

    def _pick_history(self, text: str):
        self.text_input.setPlainText(text)
        self.text_input.setFocus()
        if self.history:
            self.history.request_hide_history.emit()


# ======================= NoHistoryTab (không có history) =======================
class NoHistoryTab(UIToolbarTab):
    def __init__(self, parent_main, toast_cb):
        super().__init__(parent_main, toast_cb=toast_cb)
        body = QVBoxLayout()
        body.addWidget(
            QLabel("Tab này không có lịch sử. Bạn có thể đặt UI tuỳ ý."))
        self.layout().insertLayout(0, body)

    @property
    def history(self):
        return None


# ======================= MainWindow =======================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J2TEAM - Text to Speech (v1.1.1)")
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(
            "background-color: #1a1c24; color: white; font-size: 13px;")

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        self.tab_tts = TTSTab(
            self, self.show_toast_message)      # QPlainTextEdit
        # QTextEdit + progress controls + set progress
        self.tab_convert = ConvertTab(self, self.show_toast_message)
        self.tab_nohist = NoHistoryTab(self, self.show_toast_message)
        self._tabs = [self.tab_tts, self.tab_convert, self.tab_nohist]

        self.tabs.addTab(self.tab_tts,     "TTSTab")
        self.tabs.addTab(self.tab_convert, "ConvertTab")
        self.tabs.addTab(self.tab_nohist,  "NoHistory")

        # Progress + Log (ngoài tabs)
        box = QWidget()
        v = QVBoxLayout(box)
        title = QLabel("Tiến trình (ngoài tab)")
        title.setStyleSheet("font-size:15px; font-weight:600;")
        v.addWidget(title)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        v.addWidget(self.progress_bar)

        row = QHBoxLayout()
        self.btn_start = QPushButton("▶ Bắt đầu")
        self.btn_pause = QPushButton("⏸ Tạm dừng")
        self.btn_resume = QPushButton("⏯ Tiếp tục")
        self.btn_stop = QPushButton("⏹ Huỷ")
        for b in (self.btn_start, self.btn_pause, self.btn_resume, self.btn_stop):
            b.setStyleSheet(
                "QPushButton{background:#2b2d3a;border:1px solid #444;border-radius:6px;padding:6px;} QPushButton:hover{background:#3a3d4f;}")
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_start.clicked.connect(self.on_start)
        self.btn_pause.clicked.connect(self.on_pause)
        self.btn_resume.clicked.connect(self.on_resume)
        self.btn_stop.clicked.connect(self.on_stop)
        for b in (self.btn_start, self.btn_pause, self.btn_resume, self.btn_stop):
            row.addWidget(b)
        row.addStretch()
        v.addLayout(row)

        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setPlaceholderText("Log hệ thống/tiến trình…")
        self.text_log.setStyleSheet(
            "QTextEdit{background:#151720;border:1px solid #2a2d3a;}")
        v.addWidget(self.text_log)
        root.addWidget(box)

        # Overlay
        self.overlay = ClickToCloseOverlay(self)
        self.overlay.clicked_outside.connect(self._close_current_tab_history)

        # Nút X nổi (tuỳ chọn)
        self.close_history_btn = QPushButton("✕", self)
        self.close_history_btn.setFixedSize(28, 28)
        self.close_history_btn.setStyleSheet("""
            QPushButton { background-color: #2b2d3a; color: white; border: 1px solid #444; border-radius: 14px; font-weight: bold; }
            QPushButton:hover { background-color: #3a3d4f; }
        """)
        self.close_history_btn.clicked.connect(self._close_current_tab_history)
        self.close_history_btn.hide()

        # Status + menu
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Sẵn sàng")
        self._create_menubar()

        # Progress timer
        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._tick_progress)
        self._progress_value = 0
        self._paused = False

        # Đổi tab -> đóng panel nếu đang mở
        self.tabs.currentChanged.connect(
            lambda _: self._close_current_tab_history())

        # Kết nối history signals
        self._wire_history_signals()

        self._active_toast = None

    def _wire_history_signals(self):
        for t in self._tabs:
            h = getattr(t, "history", None)
            if h:
                h.request_show_history.connect(self._open_current_tab_history)
                h.request_hide_history.connect(self._close_current_tab_history)

    def _create_menubar(self):
        mb = self.menuBar()
        file_menu = mb.addMenu("&File")
        act_exit = QAction("Exit", self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)
        view_menu = mb.addMenu("&View")
        act_toggle = QAction("Hiện/Ẩn lịch sử tab hiện tại", self)
        act_toggle.triggered.connect(self._toggle_current_tab_history)
        view_menu.addAction(act_toggle)
        act_close_hist = QAction("Đóng lịch sử (Esc)", self)
        act_close_hist.setShortcut("Esc")
        act_close_hist.triggered.connect(self._close_current_tab_history)
        view_menu.addAction(act_close_hist)

    # ---- Helpers ----
    def _current_tab(self):
        return self.tabs.currentWidget()

    def _current_panel(self):
        """Lấy panel lịch sử của tab hiện tại (nếu có). An toàn cho mọi trường hợp."""
        tab = self.tabs.currentWidget()
        if tab is None:
            return None

        panel = None
        # Kiểu mới: tab.history (HistoryFeature) -> panel
        try:
            h = getattr(tab, "history", None)
            if h is not None:
                panel = getattr(h, "panel", None)
        except Exception:
            panel = None

        # Kiểu cũ (nếu có tab nào dùng): tab.history_panel
        if panel is None:
            panel = getattr(tab, "history_panel", None)

        return panel

    def _set_tabs_enabled(self, enabled: bool):
        if hasattr(self, "tabs"):
            self.tabs.setEnabled(enabled)
        running = self._progress_timer.isActive()
        paused = self._paused
        if hasattr(self, "btn_start"):
            self.btn_start.setEnabled(enabled and not running)
        if hasattr(self, "btn_pause"):
            self.btn_pause.setEnabled(enabled and running and not paused)
        if hasattr(self, "btn_resume"):
            self.btn_resume.setEnabled(enabled and running and paused)
        if hasattr(self, "btn_stop"):
            self.btn_stop.setEnabled(enabled and running)

    # ---- History open/close ----
    def _toggle_current_tab_history(self):
        panel = self._current_panel()
        if not panel:
            return
        (self._open_current_tab_history if panel.isHidden()
         else self._close_current_tab_history)()

    def _open_current_tab_history(self):
        panel = self._current_panel()
        if not panel:
            return
        # đóng panel tab khác
        for t in self._tabs:
            h = getattr(t, "history", None)
            if h and h.panel is not panel and not h.panel.isHidden():
                h.panel.close_panel()
        panel.dock_right()
        panel.show_with_animation(self.width())
        self._set_tabs_enabled(False)
        self._show_overlay()
        self.close_history_btn.show()
        self._position_close_history_btn(panel)

    def _close_current_tab_history(self, checked=False):
        """Đóng panel lịch sử (nếu đang mở) và khôi phục UI."""
        panel = self._current_panel()
        try:
            if panel is not None and hasattr(panel, "isHidden") and not panel.isHidden():
                # prefer animation close từ panel
                if hasattr(panel, "close_panel"):
                    panel.close_panel()
                else:
                    panel.hide()
        except Exception:
            # fallback cực an toàn
            try:
                if panel:
                    panel.hide()
            except Exception:
                pass

        # Khôi phục UI
        self._set_tabs_enabled(True)
        if hasattr(self, "close_history_btn"):
            self.close_history_btn.hide()
        if hasattr(self, "_hide_overlay"):
            self._hide_overlay()

    def _show_overlay(self):
        top = self.menuBar().height()
        self.overlay.setGeometry(0, top, self.width(), self.height() - top)
        self.overlay.show()
        self.overlay.raise_()
        p = self._current_panel()
        if p:
            p.raise_()
        self.close_history_btn.raise_()

    def _hide_overlay(self): self.overlay.hide()

    def _position_close_history_btn(self, panel: HistoryPanel):
        if self.close_history_btn.isHidden():
            return
        mb_h = self.menuBar().height()
        x = panel.x() - self.close_history_btn.width() - 8
        y = mb_h + 8
        self.close_history_btn.move(x, y)

    # ---- Toast ----
    def show_toast_message(self, message):
        toast = ToastMessage(message, self)
        self._active_toast = toast
        self._position_toast()
        toast.show()
        toast.raise_()

    def _position_toast(self):
        if self._active_toast and not self._active_toast.isHidden():
            self._active_toast.move(
                self.width()-self._active_toast.width()-20, 20)

    # ---- Progress ----
    def on_start(self):
        self.reset_progress_ui()
        self._progress_timer.start(30)
        self.status.showMessage("Đang chạy tiến trình...")
        self.text_log.append("[Progress] Bắt đầu")
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(True)

    def on_pause(self):
        self._paused = True
        self.status.showMessage("Đã tạm dừng")
        self.text_log.append("[Progress] Tạm dừng")
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(True)

    def on_resume(self):
        self._paused = False
        self.status.showMessage("Tiếp tục chạy")
        self.text_log.append("[Progress] Tiếp tục")
        self.btn_pause.setEnabled(True)
        self.btn_resume.setEnabled(False)

    def on_stop(self):
        self._progress_timer.stop()
        self.status.showMessage("Đã dừng")
        self.text_log.append("[Progress] Dừng")
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(False)

    def _tick_progress(self):
        if self._paused:
            return
        self._progress_value += 1
        self.progress_bar.setValue(self._progress_value)
        if self._progress_value % 10 == 0:
            self.text_log.append(f"[Progress] {self._progress_value}%")
        if self._progress_value >= 100:
            self._progress_timer.stop()
            self.status.showMessage("Hoàn tất!")
            self.text_log.append("[Progress] Hoàn tất")
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(False)
            self.btn_stop.setEnabled(False)

    def reset_progress_ui(self):
        self._progress_value = 0
        self.progress_bar.setValue(0)
        self._paused = False
        self.status.showMessage("Sẵn sàng")
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(False)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        panel = self._current_panel()
        if panel and not panel.isHidden():
            panel.dock_right()
            self._position_close_history_btn(panel)
            self._show_overlay()
        self._position_toast()


# ======================= Run =======================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
