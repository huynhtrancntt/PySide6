"""
TranslatePro - Text to Speech Application
Optimized version with improved structure and performance
"""

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QScrollArea, QFrame, QTextEdit, QPlainTextEdit, QProgressBar,
    QMainWindow, QTabWidget, QStatusBar, QLineEdit, QGroupBox, QComboBox,
    QSlider, QMessageBox, QFileDialog, QListWidget, QListWidgetItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QRect, Signal, QObject, QThread, QUrl, QTime, QEvent
from PySide6.QtGui import QAction, QIntValidator, QColor
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import sys
import traceback
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, List, Tuple, Any
from ui_setting import _init_addStyle
try:
    import edge_tts
except ImportError:
    edge_tts = None


class AppConfig:
    """Application configuration constants"""
    WINDOW_TITLE = "J2TEAM - Text to Speech (v1.2.0)"
    MIN_WINDOW_SIZE = (700, 500)  # Reduced for better responsiveness
    DEFAULT_WINDOW_SIZE = (1000, 700)

    HISTORY_PANEL_WIDTH = 350

    # Color scheme
    COLORS = {
        'success': '#4CAF50',    # Xanh lá - thành công
        'warning': '#FF9800',    # Vàng cam - cảnh báo
        'error': '#F44336',      # Đỏ - lỗi
        'info': '#2196F3',       # Xanh dương - thông tin
        'primary': '#9C27B0',    # Tím - chính
    }

    # Styles
    # MAIN_STYLE = "background-color: #1a1c24; color: white; font-size: 13px;"
    TOAST_STYLE = """
        QWidget { background-color: #101828; border: 1px solid rgba(0,227,150,.6); border-radius: 8px; }
        QLabel { color: white; font-weight: bold; font-size: 12px; }
        QPushButton { background: transparent; color: #888; border: none; font-size: 14px; }
        QPushButton:hover { color: white; }
        QProgressBar { background-color: transparent; border: none; height: 3px; }
        QProgressBar::chunk { background-color: #00e396; border-radius: 1px; }
    """
    BUTTON_STYLE = """
        QPushButton{background:#2b2d3a;border:1px solid #444;border-radius:6px;padding:6px;font-size:12px;} 
        QPushButton:hover{background:#3a3d4f;}
    """


class BaseHistoryItem(QFrame):
    """Base class for history items with common functionality"""
    selected = Signal(str)

    def __init__(self, text: str, timestamp: str, lang: str = "vi-VN", meta: Optional[dict] = None):
        super().__init__()
        self._text = text
        self._timestamp = timestamp
        self._lang = lang
        self._meta = meta or {}
        self._setup_ui()

    def _setup_ui(self):
        """Override in subclasses"""
        raise NotImplementedError

    def mousePressEvent(self, event):
        """Handle mouse click to select item"""
        self.selected.emit(self._text)
        super().mousePressEvent(event)


class TTSHistoryItem(BaseHistoryItem):
    """History item for TTS tab"""

    def _setup_ui(self):
        self.setStyleSheet("""
            QFrame { background-color: #1e1e2f; border: 1px solid #2f3144; border-radius: 10px; padding: 8px; }
            QLabel { color: #eaeaf0; }
            QPushButton { background: #26283a; color: #cbd0ff; border: 1px solid #3a3d55; border-radius: 6px; padding: 4px 8px; }
            QPushButton:hover { background: #323554; }
        """)

        layout = QVBoxLayout(self)

        # Preview text
        preview = QLabel(self._text)
        preview.setWordWrap(True)
        layout.addWidget(preview)

        # Bottom row with metadata and buttons
        bottom_layout = QHBoxLayout()

        # Metadata pill
        pill = QLabel(f"{self._timestamp} • {self._lang}")
        pill.setStyleSheet(
            "QLabel{background:#23263a; color:#aeb3ff; border:1px solid #39406a; border-radius:6px; padding:2px 6px;}")
        bottom_layout.addWidget(pill)
        bottom_layout.addStretch()

        # Action buttons
        self.btn_play = QPushButton("▶")
        self.btn_save = QPushButton("💾")
        self.btn_delete = QPushButton("🗑️")

        for btn in (self.btn_play, self.btn_save, self.btn_delete):
            btn.setFixedWidth(34)
            bottom_layout.addWidget(btn)

        layout.addLayout(bottom_layout)

        # Connect signals
        self.btn_play.clicked.connect(lambda: self.selected.emit(self._text))


class ConvertHistoryItem(BaseHistoryItem):
    """History item for Convert tab"""

    def _setup_ui(self):
        status = self._meta.get("status", "Draft")
        value = self._meta.get("value", self._text)

        self.setStyleSheet("""
            QFrame { background-color: #182127; border: 1px solid #27424f; border-radius: 10px; padding: 8px; }
            QLabel { color: #e2f1f8; }
            QPushButton { background: #20303a; color: #d2ecff; border: 1px solid #365868; border-radius: 6px; padding: 4px 8px; }
            QPushButton:hover { background: #294150; }
        """)

        layout = QVBoxLayout(self)

        # Header with title and status
        header_layout = QHBoxLayout()
        title = QLabel("Cấu hình")

        # Status chip with dynamic styling
        status_chip = QLabel(status)
        chip_style = self._get_status_chip_style(status)
        status_chip.setStyleSheet(chip_style)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(status_chip)
        layout.addLayout(header_layout)

        # Value display
        value_label = QLabel(value)
        value_label.setStyleSheet(
            "QLabel{background:#121820; border:1px dashed #3a5666; border-radius:6px; padding:6px;}")
        value_label.setWordWrap(True)
        layout.addWidget(value_label)

        # Bottom row with timestamp and buttons
        bottom_layout = QHBoxLayout()
        timestamp_label = QLabel(self._timestamp)
        timestamp_label.setStyleSheet("QLabel{color:#a9d1e6;}")
        bottom_layout.addWidget(timestamp_label)
        bottom_layout.addStretch()

        self.btn_edit = QPushButton("✎")
        self.btn_delete = QPushButton("🗑️")

        for btn in (self.btn_edit, self.btn_delete):
            btn.setFixedWidth(34)
            bottom_layout.addWidget(btn)

        layout.addLayout(bottom_layout)

    def _get_status_chip_style(self, status: str) -> str:
        """Get appropriate style for status chip"""
        status_lower = status.lower()
        if status_lower == "applied":
            return "QLabel { padding:2px 8px; border-radius:999px; color:#0e2a0f; background:#8ff19b; font-weight:600; }"
        elif status_lower == "auto":
            return "QLabel { padding:2px 8px; border-radius:999px; color:#262a0e; background:#e9f18f; font-weight:600; }"
        else:  # Draft
            return "QLabel { padding:2px 8px; border-radius:999px; color:#0c2a1d; background:#8ef1c5; font-weight:600; }"


class HistoryPanel(QWidget):
    """Improved history panel with better performance and UX"""

    def __init__(self, title_text: str = "Lịch sử",
                 item_factory: Optional[Callable] = None,
                 on_item_selected: Optional[Callable] = None,
                 close_callback: Optional[Callable] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedWidth(AppConfig.HISTORY_PANEL_WIDTH)

        self.item_factory = item_factory
        self.on_item_selected = on_item_selected
        self.close_callback = close_callback

        self._setup_ui(title_text)
        self.hide()

    def _setup_ui(self, title_text: str):
        """Setup the history panel UI"""
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        self.title = QLabel(title_text)
        self.title.setStyleSheet("color: white; font-weight: bold;")

        close_btn = QPushButton("✕")
        close_btn.setFixedWidth(30)
        close_btn.setStyleSheet(
            "color: white; background: transparent; border: none;")
        close_btn.clicked.connect(self.close_panel)

        header_layout.addWidget(self.title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)

        # Scrollable content area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        container = QWidget()
        self.history_layout = QVBoxLayout(container)
        self.history_layout.addStretch()
        self.scroll.setWidget(container)
        layout.addWidget(self.scroll)

    def add_history(self, text: str, lang: str = "vi-VN", meta: Optional[dict] = None):
        """Add a new history item"""
        timestamp = datetime.now().strftime("%H:%M %d/%m/%Y")

        if self.item_factory:
            item = self.item_factory(text, timestamp, lang, meta or {})
            self._connect_item_signals(item)

            # Insert before the stretch
            insert_index = max(0, self.history_layout.count() - 1)
            self.history_layout.insertWidget(insert_index, item)

    def _connect_item_signals(self, item):
        """Connect item selection signal if available"""
        if self.on_item_selected and hasattr(item, "selected"):
            try:
                item.selected.connect(self.on_item_selected)
            except Exception:
                pass  # Fail silently if connection fails

    def clear_history(self):
        """Clear all history items"""
        self._clear_history_silent()

    def _clear_history_silent(self):
        """Clear all history items without showing toast"""
        while self.history_layout.count() > 1:
            item = self.history_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def show_with_animation(self, parent_width: int):
        """Show panel without animation"""
        self.show()
        top, height = self._calculate_geometry()
        end_x = parent_width - self.width()
        self.setGeometry(end_x, top, self.width(), height)

    def close_panel(self):
        """Close panel without animation"""
        self.hide()

        if self.close_callback:
            self.close_callback()

    def dock_right(self):
        """Dock panel to the right side of parent"""
        if not self.parent():
            return

        parent = self.parent()
        top, height = self._calculate_geometry()
        x = parent.width() - self.width()
        self.setGeometry(x, top, self.width(), height)

    def _calculate_geometry(self) -> Tuple[int, int]:
        """Calculate top position and height for the panel"""
        top = 0
        parent = self.parent()

        if hasattr(parent, "menuBar") and parent.menuBar():
            top = parent.menuBar().height()

        height = parent.height() - top
        return top, height


class ClickToCloseOverlay(QWidget):
    """Overlay to detect clicks outside of panels"""
    clicked_outside = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Widget)
        self.setStyleSheet("background: rgba(0,0,0,0.25);")
        self.hide()

    def mousePressEvent(self, event):
        """Handle mouse press to emit clicked_outside signal"""
        self.clicked_outside.emit()
        event.accept()


class HistoryFeature(QObject):
    """Feature class to manage history functionality"""
    request_show_history = Signal()
    request_hide_history = Signal()

    def __init__(self, parent_main: QWidget, hist_title: str,
                 item_factory: Callable,
                 on_item_selected: Optional[Callable] = None):
        super().__init__(parent_main)

        # History button
        self.btn = QPushButton("🕘 Lịch sử")
        self.btn.setStyleSheet(
            "background-color:#2b2d3a; border:1px solid #444; border-radius:6px; padding:8px; font-size:12px;")
        self.btn.clicked.connect(self.request_show_history.emit)

        # History panel
        self.panel = HistoryPanel(
            title_text=hist_title,
            item_factory=item_factory,
            on_item_selected=on_item_selected,
            close_callback=self._on_panel_closed,
            parent=parent_main
        )

    def _on_panel_closed(self):
        """Handle panel close event"""
        self.request_hide_history.emit()


class UIToolbarTab(QWidget):
    """Base UI tab with toolbar functionality and tab logic"""

    def __init__(self, parent_main: QWidget):
        super().__init__()
        self.parent_main = parent_main
        self.history: Optional[HistoryFeature] = None

        root_layout = QVBoxLayout(self)
        self.toolbar = QHBoxLayout()
        root_layout.addLayout(self.toolbar)
        root_layout.addStretch()

    def enable_history(self, hist_title: str, item_factory: Callable,
                       on_item_selected: Optional[Callable] = None) -> HistoryFeature:
        """Enable history functionality for this tab"""
        self.history = HistoryFeature(
            parent_main=self.parent_main,
            hist_title=hist_title,
            item_factory=item_factory,
            on_item_selected=on_item_selected
        )
        return self.history

    def append_history(self, text: str, lang: str = "vi-VN", meta: Optional[dict] = None):
        """Add item to history"""
        if self.history:
            self.history.panel.add_history(text, lang=lang, meta=meta or {})

    def has_history(self) -> bool:
        """Check if tab has history enabled"""
        return self.history is not None

    def get_current_panel(self) -> Optional[HistoryPanel]:
        """Get the current history panel"""
        return self.history.panel if self.history else None

    def add_toolbar_widget(self, widget: QWidget):
        """Add widget to toolbar"""
        self.toolbar.insertWidget(self.toolbar.count(), widget)


class TTSTab(UIToolbarTab):
    """Text-to-Speech tab with improved UI and functionality"""

    def __init__(self, parent_main: QWidget):
        super().__init__(parent_main)
        self._setup_ui()

    def append_history(self, text: str, meta: Optional[dict] = None):
        """Add TTS item to history - only text and meta parameters"""
        if self.history:
            # TTS specific: only text and meta
            self.history.panel.add_history(text, meta=meta or {})

    def _setup_ui(self):
        """Setup the TTS tab UI"""
        root_layout = self.layout()

        # Enable history first to get the button
        hist = self.enable_history(
            hist_title="Lịch sử TTS",
            item_factory=lambda text, ts, lang, meta: TTSHistoryItem(
                text, ts, lang, meta),
            on_item_selected=self._on_history_selected
        )

        # Add demo items using TTSTab's append_history method
        self.append_history("Xin chào, tôi là trợ lý AI", meta={
                            "demo": True, "priority": "high"})
        self.append_history("Hôm nay thời tiết thế nào?", meta={
                            "demo": True, "priority": "normal"})

        # Header with title and history button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        title = QLabel("Nội dung cần nói")
        title.setStyleSheet("font-weight:600; font-size:16px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(hist.btn)

        root_layout.insertLayout(0, header_layout)

        # Main content layout
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Text input area
        # content_layout.addWidget(QLabel("Nội dung cần nói:"))
        self.text_input = QTextEdit(placeholderText="Nhập văn bản tại đây…")
        self.text_input.setPlainText("Xin chào! Đây là giọng nói tiếng Việt.")
        # Make text input responsive
        # self.text_input.setMaximumHeight(120)
        # self.text_input.setMinimumHeight(60)
        content_layout.addWidget(self.text_input)
        content_layout.addStretch()
        # Settings section - split into two rows for better responsiveness
        settings_group = QWidget()
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setContentsMargins(0, 5, 0, 5)

        # First row - Language and Gender
        settings_row1 = QHBoxLayout()
        settings_row1.addWidget(QLabel("Ngôn ngữ:"))
        self.cmb_lang = QComboBox()
        self.cmb_lang.setMinimumWidth(120)
        for label, code in [
            ("Vietnamese (vi)", "vi"), ("English US (en-US)", "en-US"),
            ("English UK (en-GB)", "en-GB"), ("Japanese (ja)", "ja"),
            ("Korean (ko)", "ko"), ("Chinese (zh-CN)", "zh-CN"),
            ("French (fr-FR)", "fr-FR"), ("German (de-DE)", "de-DE"),
            ("Spanish (es-ES)", "es-ES"),
        ]:
            self.cmb_lang.addItem(label, code)
        self.cmb_lang.setCurrentIndex(0)
        settings_row1.addWidget(self.cmb_lang)

        settings_row1.addWidget(QLabel("Giới tính:"))
        self.cmb_gender = QComboBox()
        self.cmb_gender.setMinimumWidth(80)
        self.cmb_gender.addItems(["Female", "Male", "Any"])
        self.cmb_gender.setCurrentText("Female")
        settings_row1.addWidget(self.cmb_gender)
        settings_row1.addStretch()

        # Second row - Speed control
        settings_row1.addWidget(QLabel("Tốc độ:"))
        self.sld_rate = QSlider(Qt.Horizontal)
        self.sld_rate.setRange(50, 200)
        self.sld_rate.setValue(100)
        self.sld_rate.setTickInterval(10)
        self.sld_rate.setTickPosition(QSlider.TicksBelow)
        self.sld_rate.setSingleStep(1)
        self.sld_rate.setPageStep(10)
        # Responsive: min width instead of fixed
        self.sld_rate.setMinimumWidth(50)
        self.sld_rate.setMaximumWidth(200)  # Max width for better layout
        # settings_row2.addWidget(self.sld_rate)
        settings_row1.addWidget(self.sld_rate)
        self.lbl_rate_val = QLabel("1.0")
        self.lbl_rate_val.setMinimumWidth(30)
        self.sld_rate.valueChanged.connect(
            lambda v: self.lbl_rate_val.setText(f"{v/100:.1f}"))
        settings_row1.addWidget(self.lbl_rate_val)

        settings_layout.addLayout(settings_row1)

        content_layout.addWidget(settings_group)

        # Control buttons - responsive layout
        buttons_layout = QHBoxLayout()
        self.btn_say = QPushButton("▶️ Phát")
        self.btn_save = QPushButton("💾 Lưu")
        self.btn_stop = QPushButton("⏹️ Dừng")

        for btn in (self.btn_say, self.btn_save, self.btn_stop):
            btn.setStyleSheet(AppConfig.BUTTON_STYLE)
            btn.setMinimumWidth(80)  # Ensure minimum width for buttons
            btn.setMaximumWidth(120)  # Prevent buttons from being too wide
            buttons_layout.addWidget(btn)

        buttons_layout.addStretch()
        content_layout.addLayout(buttons_layout)

        # Convert button in toolbar
        # self.btn_convert = QPushButton("🔊 Chuyển đổi TTS")
        # self.btn_convert.setStyleSheet(f"""
        #     QPushButton {{
        #         background-color: {AppConfig.COLORS['success']};
        #         color: white;
        #         border: none;
        #         border-radius: 6px;
        #         padding: 8px 16px;
        #         font-weight: bold;
        #         font-size: 13px;
        #     }}
        #     QPushButton:hover {{
        #         background-color: #45a049;
        #     }}
        # """)
        # self.btn_convert.clicked.connect(self._on_convert_clicked)
        # self.toolbar.addWidget(self.btn_convert)

        # Status label
        self.lbl_status = QLabel("Sẵn sàng.")
        self.lbl_status.setStyleSheet(
            "color: #888; font-size: 12px; padding: 5px;")
        content_layout.addWidget(self.lbl_status)

        # Audio player panel (initially hidden)
        self._setup_player_panel(content_layout)

        root_layout.insertLayout(1, content_layout)

        # Connect events
        self.btn_say.clicked.connect(self._on_say_clicked)
        self.btn_save.clicked.connect(self._on_save_clicked)
        self.btn_stop.clicked.connect(self._on_stop_clicked)

        self._seeking = False

        # Update status bar - now it's guaranteed to exist
        self.parent_main.status.showMessage("TTS Tab sẵn sàng")

    def _setup_player_panel(self, parent_layout: QVBoxLayout):
        """Setup audio player panel"""
        self.player_panel = QFrame()
        self.player_panel.setObjectName("PlayerPanel")
        player_layout = QHBoxLayout(self.player_panel)
        # player_layout.setContentsMargins(8, 8, 8, 8)

        # Play/pause button
        self.btn_player_play = QPushButton("⏵")
        self.btn_player_play.setObjectName("PlayerPlay")
        self.btn_player_play.setFixedSize(32, 32)
        # self.btn_player_play.setStyleSheet("""
        #     QPushButton {
        #         background: #151b2b;            /* nền tối */
        #          border: 1px solid rgba(255,255,255,0.06);
        #         color: white;

        #         border-radius: 18px;
        #         font-size: 16px;
        #         font-weight: bold;
        #         min-width: 32px;
        #         min-height: 32px;
        #     }
        #     QPushButton:hover {
        #         background-color: #45a049;
        #     }
        # """)
        self.btn_player_play.clicked.connect(self._toggle_play_pause)
        player_layout.addWidget(self.btn_player_play)

        # Time labels
        self.lbl_time_cur = QLabel("0:00")
        self.lbl_time_cur.setObjectName("PlayerTimeCur")
        # self.lbl_time_cur.setStyleSheet("color: #ccc; font-size: 11px;")
        player_layout.addWidget(self.lbl_time_cur)

        # Position slider
        self.sld_position = QSlider(Qt.Horizontal)
        self.sld_position.setObjectName("PlayerSeek")
        self.sld_position.setRange(0, 0)
        # self.sld_position.setStyleSheet("""
        #     QSlider::groove:horizontal {
        #         height: 6px;
        #         background: #3a3d4f;
        #         border-radius: 3px;
        #     }
        #     QSlider::handle:horizontal {
        #         background: #4CAF50;
        #         width: 16px;
        #         height: 16px;
        #         border-radius: 8px;
        #         margin: -5px 0;
        #     }
        #     QSlider::sub-page:horizontal {
        #         background: #4CAF50;
        #         border-radius: 3px;
        #     }
        # """)
        self.sld_position.sliderPressed.connect(self._position_slider_pressed)
        self.sld_position.sliderReleased.connect(
            self._position_slider_released)
        self.sld_position.sliderMoved.connect(self._position_slider_moved)
        player_layout.addWidget(self.sld_position, stretch=1)

        self.lbl_time_tot = QLabel("/ 0:00")
        self.lbl_time_tot.setStyleSheet("color: #ccc; font-size: 11px;")
        player_layout.addWidget(self.lbl_time_tot)

        # Volume controls
        self.lbl_vol = QLabel("🔊")
        player_layout.addWidget(self.lbl_vol)

        self.sld_volume = QSlider(Qt.Horizontal)
        self.sld_volume.setObjectName("PlayerVol")
        self.sld_volume.setRange(0, 100)
        self.sld_volume.setValue(80)
        self.sld_volume.setFixedWidth(100)
        self.sld_volume.valueChanged.connect(self._on_volume_changed)
        player_layout.addWidget(self.sld_volume)

        self.player_panel.hide()  # Initially hidden
        parent_layout.addWidget(self.player_panel)

    def _on_volume_changed(self, value: int):
        """Handle volume slider change"""
        if hasattr(self, 'audio_output'):
            self.audio_output.setVolume(value / 100.0)

    def _start_worker(self, play_only=True, save_path=None):
        try:
            text = self.text_input.toPlainText().strip()
            if not text:
                QMessageBox.warning(self, "Thiếu nội dung",
                                    "Hãy nhập văn bản cần đọc.")
                return False

            # Check if worker is already running
            if hasattr(self, 'worker_thread') and self.worker_thread and self.worker_thread.isRunning():
                self.lbl_status.setText("Worker đã đang chạy, vui lòng chờ...")
                return False

            lang_code = self.cmb_lang.currentData() or "vi"
            gender = self.cmb_gender.currentText()
            if gender == "Any":
                gender = "Female"
            rate = self.sld_rate.value()
            print(f"lang_code: {lang_code}, gender: {gender}, rate: {rate}")

            # Update UI state safely
            self.btn_say.setEnabled(False)
            self.btn_save.setEnabled(False)
            self.lbl_status.setText("Đang xử lý…")
            self.parent_main.status.showMessage("Đang xử lý…")

            # Show progress bar when starting in TTS tab
            if hasattr(self.parent_main, '_show_progress_bar'):
                self.parent_main._show_progress_bar()

            # Update progress bar safely
            try:
                if hasattr(self.parent_main, "_progress_value"):
                    self.parent_main._progress_value = 1
                    self.parent_main.progress_bar.setValue(1)
            except Exception as e:
                print(f"Warning: Cannot update progress bar: {e}")

            # Create and configure worker thread
            self.worker_thread = QThread()
            self.worker = EdgeTTSWorker(
                text, lang_code, gender, rate, save_path=save_path)
            self.worker.moveToThread(self.worker_thread)

            # Connect signals
            self.worker_thread.started.connect(self.worker.run)
            self.worker.status.connect(self._on_worker_status)
            self.worker.progress.connect(self._on_worker_progress)
            self.worker.error.connect(self._on_worker_error)
            self.worker.finished.connect(self._on_worker_finished)
            self.worker.file_ready.connect(self._on_file_ready)

            # Start thread
            self.worker_thread.start()
            return True

        except Exception as e:
            self.lbl_status.setText(f"Lỗi khởi tạo worker: {str(e)}")
            # Re-enable buttons on error
            self.btn_say.setEnabled(True)
            self.btn_save.setEnabled(True)
            QMessageBox.critical(
                self, "Lỗi", f"Không thể khởi tạo TTS worker:\n{str(e)}")
            return False

    def _on_worker_status(self, msg: str):
        """Handle worker status updates"""
        self.lbl_status.setText(msg)
        if hasattr(self.parent_main, "_add_log_item"):
            self.parent_main._add_log_item(f"[TTS] {msg}")

    def _on_worker_progress(self, value: int):
        """Handle worker progress updates"""
        if hasattr(self.parent_main, "_progress_value"):
            self.parent_main._progress_value = value
            self.parent_main.progress_bar.setValue(value)

    def _on_worker_error(self, msg: str):
        """Handle worker errors"""
        QMessageBox.critical(self, "Lỗi TTS", msg)
        self.lbl_status.setText(f"Lỗi: {msg}")
        if hasattr(self.parent_main, "_add_log_item"):
            self.parent_main._add_log_item(f"[TTS Error] {msg}", level="error")

    def _on_worker_finished(self):
        """Handle worker completion"""
        try:
            # Re-enable UI buttons
            self.btn_say.setEnabled(True)
            self.btn_save.setEnabled(True)

            # Reset progress safely
            try:
                if hasattr(self.parent_main, "_progress_value"):
                    self.parent_main._progress_value = 100
                    self.parent_main.progress_bar.setValue(100)
                    self.parent_main.status.showMessage("Đã hoàn thành")
            except Exception as e:
                print(f"Warning: Cannot update progress bar: {e}")

            # Cleanup worker thread safely
            try:
                if hasattr(self, 'worker_thread') and self.worker_thread:
                    if self.worker_thread.isRunning():
                        self.worker_thread.quit()
                        self.worker_thread.wait(3000)  # Wait max 3 seconds
                    self.worker_thread.deleteLater()
                    self.worker_thread = None

                if hasattr(self, 'worker') and self.worker:
                    self.worker.deleteLater()
                    self.worker = None

            except Exception as e:
                print(f"Warning: Error during worker cleanup: {e}")

        except Exception as e:
            print(f"Error in _on_worker_finished: {e}")
            # Ensure buttons are still enabled even if other operations fail
            self.btn_say.setEnabled(True)
            self.btn_save.setEnabled(True)
        finally:
            # Hide progress bar after completion in TTS tab (keep log visible)
            if hasattr(self.parent_main, '_hide_progress_bar'):
                # Add a small delay to allow user to see completion
                def hide_progress_and_keep_log():
                    self.parent_main._hide_progress_bar()
                    # Ensure log stays visible
                    if hasattr(self.parent_main, 'output_list') and self.parent_main.output_list:
                        self.parent_main.output_list.setVisible(True)

                # Hide after 2 seconds
                QTimer.singleShot(2000, hide_progress_and_keep_log)

    def _on_file_ready(self, file_path: str):
        """Handle when audio file is ready"""
        path = Path(file_path)
        self.lbl_status.setText(f"Hoàn thành: {path.name}")

        # Add to history
        self.append_history(self.text_input.toPlainText().strip(),
                            meta={"file_path": str(path), "timestamp": datetime.now().isoformat()})

        # Auto-play the generated audio
        self._play_audio_file(path)

        if hasattr(self.parent_main, "_add_log_item"):
            self.parent_main._add_log_item(
                f"[TTS] Đã tạo file: {path.name}", level="info")

    def _play_audio_file(self, file_path: Path):
        """Play the generated audio file"""
        try:
            # Check if file exists
            if not file_path.exists():
                raise FileNotFoundError(f"File không tồn tại: {file_path}")

            # Initialize media player if not exists
            if not hasattr(self, 'media_player') or self.media_player is None:
                self.media_player = QMediaPlayer(self)
                self.audio_output = QAudioOutput(self)
                self.media_player.setAudioOutput(self.audio_output)

                # Connect player signals safely
                try:
                    self.media_player.durationChanged.connect(
                        self._on_duration_changed)
                    self.media_player.positionChanged.connect(
                        self._on_position_changed)
                    self.media_player.playbackStateChanged.connect(
                        self._on_playback_state_changed)
                except Exception as e:
                    print(f"Warning: Cannot connect media player signals: {e}")

            # Set volume from slider safely
            try:
                if hasattr(self, 'audio_output') and self.audio_output:
                    volume = self.sld_volume.value() / 100.0
                    self.audio_output.setVolume(volume)
            except Exception as e:
                print(f"Warning: Cannot set volume: {e}")

            # Load and play
            file_url = QUrl.fromLocalFile(str(file_path.resolve()))
            self.media_player.setSource(file_url)
            self.media_player.play()

            # Show player panel
            if hasattr(self, 'player_panel'):
                self.player_panel.show()

            self.lbl_status.setText(f"Đang phát: {file_path.name}")

        except FileNotFoundError as e:
            error_msg = f"File không tồn tại: {file_path.name}"
            self.lbl_status.setText(error_msg)
            QMessageBox.warning(self, "Lỗi file", str(e))
        except Exception as e:
            error_msg = f"Không thể phát file: {str(e)}"
            self.lbl_status.setText(error_msg)
            QMessageBox.critical(self, "Lỗi phát âm thanh",
                                 f"Không thể phát file âm thanh:\n{str(e)}")
            print(f"Audio playback error: {e}")

    def _on_duration_changed(self, duration_ms: int):
        """Handle media duration change"""
        self.sld_position.setRange(0, duration_ms)
        minutes = duration_ms // 60000
        seconds = (duration_ms % 60000) // 1000
        self.lbl_time_tot.setText(f"/ {minutes}:{seconds:02d}")

    def _on_position_changed(self, position_ms: int):
        """Handle media position change"""
        if not self._seeking:
            self.sld_position.setValue(position_ms)
        minutes = position_ms // 60000
        seconds = (position_ms % 60000) // 1000
        self.lbl_time_cur.setText(f"{minutes}:{seconds:02d}")

    def _on_playback_state_changed(self, state):
        """Handle playback state change"""
        if state == QMediaPlayer.PlayingState:
            self.btn_player_play.setText("⏸")
        else:
            self.btn_player_play.setText("⏵")

    def _on_convert_clicked(self):
        """Handle convert button click"""
        text = self.text_input.toPlainText().strip()
        if not text:
            return

        # Start TTS conversion
        self._start_worker(play_only=True)

        # Add to history with TTS metadata
        self.append_history(
            text, meta={"type": "TTS", "timestamp": datetime.now().isoformat()})

        # Log to main window if available
        if hasattr(self.parent_main, "_add_log_item"):
            self.parent_main._add_log_item(
                f"[TTS] {text[:60]}{'...' if len(text) > 60 else ''}")

    def _on_say_clicked(self):
        """Handle say button click"""
        try:
            text = self.text_input.toPlainText().strip()
            if not text:
                QMessageBox.warning(self, "Thiếu nội dung",
                                    "Hãy nhập văn bản cần đọc.")
                return

            # Prevent multiple clicks
            if hasattr(self, 'worker_thread') and self.worker_thread and self.worker_thread.isRunning():
                QMessageBox.information(
                    self, "Đang xử lý", "Hệ thống đang xử lý yêu cầu trước. Vui lòng chờ...")
                return

            # Update UI safely
            self.lbl_status.setText("Đang chuyển đổi giọng nói...")

            # Start worker
            self._start_worker(play_only=True)

            # Log to main window
            if hasattr(self.parent_main, "output_list"):
                self.parent_main._add_log_item(
                    f"[TTS Play] {text[:40]}{'...' if len(text) > 40 else ''}")

            # Add to history after successful start
            self.append_history(
                text, meta={"type": "Play", "timestamp": datetime.now().isoformat()})

        except Exception as e:
            self.lbl_status.setText(f"Lỗi: {str(e)}")
            QMessageBox.critical(
                self, "Lỗi TTS", f"Không thể bắt đầu chuyển đổi:\n{str(e)}")
            # Re-enable buttons on error
            self.btn_say.setEnabled(True)
            self.btn_save.setEnabled(True)

    def _on_save_clicked(self):
        """Handle save button click"""
        text = self.text_input.toPlainText().strip()
        if not text:
            return

        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu file âm thanh",
            f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
            "MP3 Files (*.mp3);;All Files (*)"
        )

        if file_path:
            self.lbl_status.setText("Đang lưu file âm thanh...")
            if hasattr(self.parent_main, "output_list"):
                self.parent_main._add_log_item(
                    f"[TTS Save] {text[:40]}{'...' if len(text) > 40 else ''}")

            # Start worker with save path
            self._start_worker(play_only=False, save_path=file_path)

            # Add to history
            self.append_history(text, meta={
                                "type": "Save", "file_path": file_path, "timestamp": datetime.now().isoformat()})

    def _on_stop_clicked(self):
        print("Stop button clicked")
        """Handle stop button click"""
        # Stop media player if exists
        if hasattr(self, 'media_player'):
            self.media_player.stop()
            self.player_panel.hide()

        # Stop worker if running
        if hasattr(self, 'worker_thread') and self.worker_thread and self.worker_thread.isRunning():
            if self.worker:
                self.worker_thread.requestInterruption()
                self.worker_thread.quit()
                self.worker_thread.wait()
                self.worker_thread = None
                self.worker = None

            # Re-enable buttons
            self.btn_say.setEnabled(True)
            self.btn_save.setEnabled(True)

        self.lbl_status.setText("Đã dừng.")
        if hasattr(self.parent_main, "_add_log_item"):
            self.parent_main._add_log_item("[TTS] Đã dừng phát âm thanh")

    def _toggle_play_pause(self):
        """Toggle play/pause for audio player"""
        try:
            if hasattr(self, 'media_player') and self.media_player:
                current_state = self.media_player.playbackState()
                if current_state == QMediaPlayer.PlayingState:
                    self.media_player.pause()
                    self.lbl_status.setText("Đã tạm dừng phát")
                elif current_state == QMediaPlayer.PausedState:
                    self.media_player.play()
                    self.lbl_status.setText("Đang phát âm thanh")
                else:
                    # Stopped state - try to play from beginning
                    self.media_player.play()
                    self.lbl_status.setText("Đang phát âm thanh")
            else:
                self.lbl_status.setText("Chưa có file âm thanh để phát")
                QMessageBox.warning(self, "Lỗi phát âm thanh",
                                    "Không có file âm thanh để phát.")
        except Exception as e:
            self.lbl_status.setText(f"Lỗi khi phát âm thanh: {str(e)}")
            QMessageBox.critical(self, "Lỗi phát âm thanh",
                                 f"Không thể phát âm thanh:\n{str(e)}")

    def _position_slider_pressed(self):
        """Handle position slider press"""
        self._seeking = True

    def _position_slider_released(self):
        """Handle position slider release"""
        self._seeking = False
        if hasattr(self, 'media_player'):
            self.media_player.setPosition(self.sld_position.value())

    def _position_slider_moved(self, value: int):
        """Handle position slider movement"""
        if self._seeking:
            # Update time display while seeking
            minutes = value // 60000
            seconds = (value % 60000) // 1000
            self.lbl_time_cur.setText(f"{minutes}:{seconds:02d}")

    def _on_history_selected(self, text: str):
        """Handle history item selection"""
        self.text_input.setPlainText(text)
        self.text_input.setFocus()

        # Hide history panel
        # if self.history:
        #     self.history.request_hide_history.emit()


class EdgeTTSWorker(QObject):
    """Worker chạy trong thread để gọi edge-tts"""
    finished = Signal()
    error = Signal(str)
    status = Signal(str)
    progress = Signal(int)
    file_ready = Signal(str)

    def __init__(self, text: str, lang_code: str, gender: str, rate: int, save_path=None):
        super().__init__()
        self.text = text
        self.lang_code = (lang_code or "vi").lower().strip()
        self.gender = (gender or "Female").capitalize()
        self.rate = rate
        self.save_path = Path(save_path) if save_path else None
        self.audio_root = Path.cwd() / "audio"
        self.audio_root.mkdir(parents=True, exist_ok=True)
        self.last_voice = None

    def run(self):
        if edge_tts is None:
            self.error.emit(
                "Edge-TTS library not found. Please install: pip install edge-tts")
            self.finished.emit()
            return

        try:
            asyncio.run(self._run_async())
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

    async def _run_async(self):
        self.status.emit("Đang chọn voice phù hợp…")
        self.progress.emit(10)
        voice = await self._pick_voice(self.lang_code, self.gender)
        self.last_voice = voice
        if not voice:
            raise RuntimeError(
                f"Không tìm thấy voice cho ngôn ngữ '{self.lang_code}'.")

        # Tính rate % theo thang 50..250
        pct = max(-50, min(50, (self.rate - 150)))
        ssml_text = (
            f"<speak version='1.0' xml:lang='{voice.split('-')[0]}'>"
            f"<prosody rate='{pct}%'>{self._escape_ssml(self.text)}</prosody></speak>"
        )

        self.status.emit("Đang tổng hợp giọng nói…")
        self.progress.emit(40)
        tts = edge_tts.Communicate(ssml_text, voice)

        # Lưu: audio/YYYY-MM-DD/tts_YYYYMMDD_HHMMSS.mp3 (tự tránh trùng tên)
        if self.save_path is None:
            day_dir = self.audio_root / datetime.now().strftime("%Y-%m-%d")
            day_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_path = day_dir / f"tts_{timestamp}.mp3"
            idx = 1
            while out_path.exists():
                out_path = day_dir / f"tts_{timestamp}_{idx}.mp3"
                idx += 1
        else:
            out_path = self.save_path

        await tts.save(str(out_path))

        # metadata .txt (text + info)
        try:
            meta_txt = out_path.with_suffix(".txt")
            meta_txt.write_text(
                f"Created: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
                f"Lang: {self.lang_code}\nGender: {self.gender}\n"
                f"Voice: {self.last_voice}\nRate(50-250): {self.rate}\n\n"
                f"----- TEXT -----\n{self.text}", encoding="utf-8"
            )
        except Exception as e:
            self.status.emit(f"Không thể lưu .txt: {e}")

        self.file_ready.emit(str(out_path))
        self.progress.emit(100)
        self.status.emit(f"Đã tạo: {out_path.name}")

    async def _pick_voice(self, lang_code: str, prefer_gender: str) -> str | None:
        """Chọn voice theo locale + ưu tiên gender"""
        voices = await edge_tts.list_voices()
        lang_code = lang_code.lower()
        def match_locale(v): return v.get(
            "Locale", "").lower().startswith(lang_code)
        candidates = [v for v in voices if match_locale(v)]
        if not candidates:
            return None
        for v in candidates:
            if v.get("Gender", "").lower() == prefer_gender.lower():
                return v.get("ShortName")
        return candidates[0].get("ShortName")

    @staticmethod
    def _escape_ssml(text: str) -> str:
        """Escape XML cho SSML"""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class ConvertTab(UIToolbarTab):
    """Convert tab with progress controls and improved functionality"""

    def __init__(self, parent_main: QWidget):
        super().__init__(parent_main)
        self._setup_ui()

    def append_history(self, text: str, config_type: str = "Draft", value: str = "", meta: Optional[dict] = None):
        """Add Convert item to history - 3 parameters plus meta"""
        if self.history:
            # Convert specific: text, config_type, value, and meta
            combined_meta = meta or {}
            combined_meta.update({
                "status": config_type,
                "value": value or text
            })
            self.history.panel.add_history(text, meta=combined_meta)

    def _setup_ui(self):
        """Setup the Convert tab UI"""
        # Main body layout
        body_layout = QVBoxLayout()

        # Text input area
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Nhập văn bản để chuyển đổi...")
        body_layout.addWidget(self.text_input)

        # Progress controls
        self._setup_progress_controls(body_layout)

        # History section
        self._setup_history_section(body_layout)

        # Convert button
        self._setup_convert_button(body_layout)

        # Add body to main layout
        self.layout().insertLayout(0, body_layout)

    def _setup_progress_controls(self, parent_layout: QVBoxLayout):
        """Setup progress control buttons"""
        ctrl_layout = QHBoxLayout()

        # Progress buttons
        self.btn_start = QPushButton("▶ Bắt đầu")
        self.btn_pause = QPushButton("⏸ Tạm dừng")
        self.btn_resume = QPushButton("⏯ Tiếp tục")
        self.btn_stop = QPushButton("⏹ Dừng")

        for btn in (self.btn_start, self.btn_pause, self.btn_resume, self.btn_stop):
            btn.setStyleSheet(AppConfig.BUTTON_STYLE)

        # Connect to main window progress controls
        main_window = self.parent_main
        self.btn_start.clicked.connect(main_window.on_start)
        self.btn_pause.clicked.connect(main_window.on_pause)
        self.btn_resume.clicked.connect(main_window.on_resume)
        self.btn_stop.clicked.connect(main_window.on_stop)

        for btn in (self.btn_start, self.btn_pause, self.btn_resume, self.btn_stop):
            ctrl_layout.addWidget(btn)
        ctrl_layout.addStretch()

        # Progress input controls
        self.progress_input = QLineEdit()
        self.progress_input.setPlaceholderText("0-100")
        self.progress_input.setFixedWidth(80)
        self.progress_input.setValidator(QIntValidator(0, 100, self))

        self.btn_set_progress = QPushButton("Đặt tiến trình")
        self.btn_set_progress.setStyleSheet("""
            QPushButton{background:#32405a;border:1px solid #44597c;border-radius:6px;padding:6px;} 
            QPushButton:hover{background:#3b4e6e;}
        """)
        self.btn_set_progress.clicked.connect(self._on_set_progress)

        ctrl_layout.addWidget(QLabel("Tiến trình:"))
        ctrl_layout.addWidget(self.progress_input)
        ctrl_layout.addWidget(self.btn_set_progress)

        parent_layout.addLayout(ctrl_layout)

    def _setup_history_section(self, parent_layout: QVBoxLayout):
        """Setup history section"""
        hist_layout = QHBoxLayout()
        hist_layout.addWidget(QLabel("Lịch sử chuyển đổi"))
        hist_layout.addStretch()

        # Enable history
        hist = self.enable_history(
            hist_title="Lịch sử Chuyển đổi",
            item_factory=lambda text, ts, lang, meta: ConvertHistoryItem(
                text, ts, lang, meta),
            on_item_selected=self._on_history_selected
        )

        # Add demo items using ConvertTab's append_history method
        self.append_history("Cấu hình A", config_type="Applied", value="Applied config data",
                            meta={"demo": True, "priority": "high"})
        self.append_history("Cấu hình B", config_type="Draft", value="Draft config data",
                            meta={"demo": True, "priority": "normal"})
        hist_layout.addWidget(hist.btn)
        parent_layout.addLayout(hist_layout)

    def _setup_convert_button(self, parent_layout: QVBoxLayout):
        """Setup convert button and UI toggle buttons"""
        convert_layout = QHBoxLayout()

        self.btn_convert = QPushButton("🔄 Chuyển đổi")
        self.btn_convert.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppConfig.COLORS['info']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
        """)
        self.btn_convert.clicked.connect(self._on_convert_clicked)
        convert_layout.addWidget(self.btn_convert)

        convert_layout.addStretch()
        parent_layout.addLayout(convert_layout)

        # UI Toggle Control Panel - Always visible
        toggle_panel = QWidget()
        # toggle_panel.setStyleSheet("""
        #     QWidget {
        #         background-color: #2a2d3a;
        #         border: 1px solid #444;
        #         border-radius: 6px;
        #         padding: 5px;
        #     }
        # """)
        toggle_layout = QHBoxLayout(toggle_panel)
        toggle_layout.setContentsMargins(8, 5, 8, 5)

        toggle_label = QLabel("🎛️ Điều khiển UI:")
        toggle_label.setStyleSheet("color: #FFD700; font-weight: bold;")
        toggle_layout.addWidget(toggle_label)

        self.btn_toggle_progress = QPushButton("🔽 Ẩn Progress Bar")
        self.btn_toggle_progress.setStyleSheet(AppConfig.BUTTON_STYLE)
        self.btn_toggle_progress.clicked.connect(self._toggle_progress_bar)
        toggle_layout.addWidget(self.btn_toggle_progress)

        self.btn_toggle_log = QPushButton("🔽 Ẩn Log")
        self.btn_toggle_log.setStyleSheet(AppConfig.BUTTON_STYLE)
        self.btn_toggle_log.clicked.connect(self._toggle_log)
        toggle_layout.addWidget(self.btn_toggle_log)

        toggle_layout.addStretch()
        parent_layout.addWidget(toggle_panel)

        # Add toggle button for key auth group
        self.btn_toggle_key_auth = QPushButton("🔽 Ẩn Key Auth")
        self.btn_toggle_key_auth.setCheckable(True)
        self.btn_toggle_key_auth.setChecked(True)
        self.btn_toggle_key_auth.clicked.connect(self._toggle_key_auth_group)
        convert_layout.addWidget(self.btn_toggle_key_auth)

    def _on_set_progress(self):
        """Handle set progress button click"""
        text = self.progress_input.text().strip()
        if not text:

            return

        try:
            value = int(text)
        except ValueError:

            return

        value = max(0, min(100, value))
        main_window = self.parent_main

        # Update progress
        main_window._progress_value = value
        main_window.progress_bar.setValue(value)

        # Handle completion
        if main_window._progress_timer.isActive() and value >= 100:
            main_window._progress_timer.stop()
            main_window.status.showMessage("Hoàn thành!")
            main_window._add_log_item(
                "[Progress] Hoàn thành (đặt từ ConvertTab)", level="blue")
            main_window._update_progress_buttons(False)
        else:
            main_window.status.showMessage(f"Đã đặt tiến trình: {value}%")
            main_window._add_log_item(
                f"[Progress] Đặt {value}% (ConvertTab)", level="blue")

    def _on_convert_clicked(self):
        """Handle convert button click"""
        text = self.text_input.toPlainText().strip()
        if not text:
            return

        # Add to history with Convert 3 parameters
        self.append_history(text, config_type="Auto", value=f"Processed: {text[:20]}...",
                            meta={"type": "Convert", "timestamp": datetime.now().isoformat()})

        # Log to main window
        if hasattr(self.parent_main, "_add_log_item"):
            self.parent_main._add_log_item(
                f"[Convert] {text[:60]}{'...' if len(text) > 60 else ''}")

    def _toggle_progress_bar(self):
        """Toggle progress bar visibility"""
        if hasattr(self.parent_main, 'progress_bar') and self.parent_main.progress_bar:
            progress_bar = self.parent_main.progress_bar
            # Also hide/show the progress buttons
            buttons = [self.parent_main.btn_start, self.parent_main.btn_pause,
                       self.parent_main.btn_resume, self.parent_main.btn_stop]

            if progress_bar.isVisible():
                progress_bar.setVisible(False)
                # Hide progress title as well
                if hasattr(self.parent_main, '_progress_title') and self.parent_main._progress_title:
                    self.parent_main._progress_title.setVisible(False)
                # Hide progress buttons
                for btn in buttons:
                    if btn:
                        btn.setVisible(False)
                self.btn_toggle_progress.setText("🔼 Hiện Progress Bar")
                self.parent_main.status.showMessage(
                    "Đã ẩn progress bar và controls")
            else:
                progress_bar.setVisible(True)
                # Show progress title
                if hasattr(self.parent_main, '_progress_title') and self.parent_main._progress_title:
                    self.parent_main._progress_title.setVisible(True)
                # Show progress buttons
                for btn in buttons:
                    if btn:
                        btn.setVisible(True)
                self.btn_toggle_progress.setText("🔽 Ẩn Progress Bar")
                self.parent_main.status.showMessage(
                    "Đã hiện progress bar và controls")

            # Safe layout update
            if hasattr(self.parent_main, '_safe_layout_update'):
                self.parent_main._safe_layout_update()

    def _toggle_log(self):
        """Toggle log area visibility"""
        if hasattr(self.parent_main, 'output_list') and self.parent_main.output_list:
            output_list = self.parent_main.output_list
            if output_list.isVisible():
                output_list.setVisible(False)
                self.btn_toggle_log.setText("🔼 Hiện Log")
                self.parent_main.status.showMessage("Đã ẩn log area")
            else:
                output_list.setVisible(True)
                self.btn_toggle_log.setText("🔽 Ẩn Log")
                self.parent_main.status.showMessage("Đã hiện log area")

            # Safe layout update
            if hasattr(self.parent_main, '_safe_layout_update'):
                self.parent_main._safe_layout_update()

    def _on_history_selected(self, text: str):
        """Handle history item selection"""
        self.text_input.setPlainText(text)
        self.text_input.setFocus()

        if self.history:
            self.history.request_hide_history.emit()

    def _toggle_key_auth_group(self):
        """Toggle key authentication group visibility"""
        print("toggle key auth group")
        # data = self.__dict__
        # Ghi ra file JSON
        with open("self_data.txt", "w", encoding="utf-8") as f:
            f.write(str(self.__dict__))
        # Access key_auth_group from parent_main, not self
        if hasattr(self.parent_main, 'key_auth_group') and self.parent_main.key_auth_group:
            key_group = self.parent_main.key_auth_group
            if key_group.isVisible():
                key_group.setVisible(False)
                self.btn_toggle_key_auth.setText("🔼 Hiện Key Auth")
                self.parent_main.status.showMessage("Đã ẩn Key Auth section")
            else:
                key_group.setVisible(True)
                self.btn_toggle_key_auth.setText("🔽 Ẩn Key Auth")
                self.parent_main.status.showMessage("Đã hiện Key Auth section")

            # Safe layout update
            if hasattr(self.parent_main, '_safe_layout_update'):
                self.parent_main._safe_layout_update()
        else:
            print("key_auth_group not found in parent_main")


class SimpleTab(UIToolbarTab):
    """Simple tab without history functionality"""

    def __init__(self, parent_main: QWidget):
        super().__init__(parent_main)

        body_layout = QVBoxLayout()

        content_label = QLabel("Đây là tab đơn giản không có lịch sử.")
        content_label.setStyleSheet("font-size: 14px; padding: 20px;")
        content_label.setAlignment(Qt.AlignCenter)

        body_layout.addWidget(content_label)
        self.layout().insertLayout(0, body_layout)


class MainWindow(QMainWindow):
    """Main application window with improved architecture"""

    def __init__(self):
        super().__init__()

        self._closing_history = False  # Prevent recursion in history close
        self._setup_complete = False  # Track setup completion
        self._setup_window()
        self._setup_ui()
        self._setup_progress_system()
        self._setup_connections()

        # Mark setup as complete
        self._setup_complete = True

        # Trigger initial tab state setup
        current_tab = self.tabs.currentIndex()
        self._on_tab_changed(current_tab)

    def _setup_window(self):
        """Setup main window properties"""
        self.setWindowTitle(AppConfig.WINDOW_TITLE)
        # self.setMinimumSize(*AppConfig.MIN_WINDOW_SIZE)
        # self.resize(*AppConfig.DEFAULT_WINDOW_SIZE)  # Set default size
        # self.setStyleSheet(AppConfig.MAIN_STYLE)
        _init_addStyle(self)
        # Center window on screen
        self._center_on_screen()

    def _setup_ui(self):
        """Setup the main UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Menu and status bar FIRST - so tabs can access status bar
        self._setup_menu_and_status()

        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Create tabs - now status bar is available
        self.tab_tts = TTSTab(self)
        self.tab_convert = ConvertTab(self)
        self.tab_simple = SimpleTab(self)

        self._all_tabs = [self.tab_tts, self.tab_convert, self.tab_simple]

        # Add tabs to widget
        self.tabs.addTab(self.tab_tts, "Text to Speech")
        self.tabs.addTab(self.tab_convert, "Convert")
        self.tabs.addTab(self.tab_simple, "Simple")

        # main_layout.addStretch()
        # Progress and log section
        self._setup_progress_ui(main_layout)

        # Overlay and controls
        self._setup_overlay_controls()

        # Initialize button visibility based on lock state
        self._update_tab_buttons_visibility()

        # Ensure progress_widget is visible by default (app starts on Tab 0 - TTS)
        if hasattr(self, 'progress_widget') and self.progress_widget:
            self.progress_widget.setVisible(True)

        # Set initial state for Tab 1: hide progress bar only if locked, show log
        if not self._is_unlocked:
            self._hide_progress_bar()
        else:
            # Add log message for default unlocked state
            self._add_log_item(
                "🎉 Ứng dụng đã sẵn sàng - Tất cả chức năng đã được kích hoạt", level="info")

        if hasattr(self, 'output_list') and self.output_list:
            self.output_list.setVisible(True)

    def _setup_progress_ui(self, parent_layout: QVBoxLayout):
        """Setup progress UI section"""
        self.progress_widget = QWidget()  # Store reference for hide/show
        progress_layout = QVBoxLayout(self.progress_widget)
        progress_layout.addStretch()
        # Key Authentication Group Box
        self._setup_key_auth_group(progress_layout)

        # Title - store reference for toggle
        self._progress_title = QLabel("Tiến trình xử lý")
        self._progress_title.setStyleSheet(
            "font-size: 16px; font-weight: 600; margin-bottom: 10px;")
        progress_layout.addWidget(self._progress_title)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #444;
                border-radius: 6px;
                text-align: center;
                background-color: #2a2d3a;
                height: 20px;
                font-size: 12px;
            }}
            QProgressBar::chunk {{
                background-color: {AppConfig.COLORS['primary']};
                border-radius: 5px;
            }}
        """)
        progress_layout.addWidget(self.progress_bar)

        # Control buttons - responsive layout
        button_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ Bắt đầu")
        self.btn_pause = QPushButton("⏸ Tạm dừng")
        self.btn_resume = QPushButton("⏯ Tiếp tục")
        self.btn_stop = QPushButton("⏹ Dừng")

        for btn in (self.btn_start, self.btn_pause, self.btn_resume, self.btn_stop):
            btn.setStyleSheet(AppConfig.BUTTON_STYLE)
            btn.setMinimumWidth(70)  # Minimum width for progress buttons
            btn.setMaximumWidth(100)  # Prevent buttons from being too wide
            button_layout.addWidget(btn)

        button_layout.addStretch()
        progress_layout.addStretch()
        progress_layout.addLayout(button_layout)

        # Log area
        self.output_list = QListWidget()
        # Make log area responsive - smaller for small screens
        # self.output_list.setMinimumHeight(60)
        # self.output_list.setMaximumHeight(80)
        self.output_list.setAlternatingRowColors(True)
        self.output_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        progress_layout.addWidget(self.output_list)

        parent_layout.addWidget(self.progress_widget)

        # Set size policy to prevent pushing down when hidden
        self.progress_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.progress_bar.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.output_list.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Remove unnecessary addStretch() calls
        # progress_layout.addStretch()  # Removed to prevent pushing
        # button_layout.addStretch()  # Removed to prevent pushing

        # Add stretch only at the end if needed
        progress_layout.addStretch()

    def _setup_key_auth_group(self, parent_layout: QVBoxLayout):
        """Setup key authentication group box"""
        # Group box
        key_group = QGroupBox("🔐 Xác thực truy cập")
        key_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #334155;
                border-radius: 8px;
                margin: 5px 0px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #FFD700;
            }
        """)

        key_layout = QHBoxLayout(key_group)
        # Reduce margins for smaller screens
        key_layout.setContentsMargins(10, 5, 10, 5)

        # Key input - make more compact
        key_label = QLabel("Key:")  # Shortened label
        key_label.setStyleSheet("font-weight: normal; margin-right: 3px;")

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText(
            "Nhập key...")  # Shortened placeholder
        self.key_input.setMinimumWidth(80)   # Smaller minimum width
        # Smaller max width for better layout
        self.key_input.setMaximumWidth(150)
        self.key_input.setStyleSheet("""
            QLineEdit:focus {
                border: 2px solid #FFD700;
            }
        """)
        self.key_input.textChanged.connect(self._on_key_changed)

        # Unlock button
        self.unlock_btn = QPushButton("🔓 Mở khóa")
        self.unlock_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B35;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #E55A2B;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        self.unlock_btn.clicked.connect(self._on_unlock_clicked)

        # Status label - will be set to unlocked state later
        self.key_status = QLabel("🔒 Đã khóa")
        self.key_status.setStyleSheet("color: #FF6B35; font-weight: bold;")

        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_input)
        key_layout.addWidget(self.unlock_btn)
        key_layout.addWidget(self.key_status)
        key_layout.addStretch()

        parent_layout.addWidget(key_group)

        # Initialize unlocked state - default unlocked
        self._is_unlocked = True

        # Set UI to unlocked state
        self.key_input.setText("HT")
        self.key_input.setEnabled(False)
        self.key_status.setText("✅ Đã mở khóa")
        self.key_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
        self.unlock_btn.setText("✅ Đã mở")
        self.unlock_btn.setEnabled(False)

        # Note: _update_tab_buttons_visibility() will be called after UI setup is complete

        # Store reference to key_auth_group for toggling
        self.key_auth_group = key_group
        parent_layout.addWidget(self.key_auth_group)

    def _setup_overlay_controls(self):
        """Setup overlay and close button"""
        # Overlay for clicking outside panels
        self.overlay = ClickToCloseOverlay(self)
        self.overlay.clicked_outside.connect(self._close_current_tab_history)

        # Floating close button
        self.close_history_btn = QPushButton("✕", self)
        self.close_history_btn.setFixedSize(28, 28)
        self.close_history_btn.setStyleSheet("""
            QPushButton { 
                background-color: #2b2d3a; 
                color: white; 
                border: 1px solid #444; 
                border-radius: 14px; 
                font-weight: bold; 
            }
            QPushButton:hover { 
                background-color: #3a3d4f; 
            }
        """)
        self.close_history_btn.clicked.connect(self._close_current_tab_history)
        self.close_history_btn.hide()

    def _setup_menu_and_status(self):
        """Setup menu bar and status bar"""
        # Menu bar
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        exit_action = QAction("Thoát", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")
        toggle_history_action = QAction("Hiện/Ẩn lịch sử", self)
        toggle_history_action.triggered.connect(
            self._toggle_current_tab_history)
        view_menu.addAction(toggle_history_action)

        close_history_action = QAction("Đóng lịch sử (Esc)", self)
        close_history_action.setShortcut("Esc")
        close_history_action.triggered.connect(self._close_current_tab_history)
        view_menu.addAction(close_history_action)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Sẵn sàng")

    def _add_log_item(self, message: str, level=""):
        """Add item to output list with timestamp and color coding"""
        if hasattr(self, 'output_list') and self.output_list:
            current_time = QTime.currentTime().toString("HH:mm:ss")
            message = f"[{current_time}] {message}"
            item = QListWidgetItem(message)
            if level == "info":
                item.setForeground(QColor("#05df60"))
            elif level == "warning":
                item.setForeground(QColor("orange"))
            elif level == "error":
                item.setForeground(QColor("red"))
            elif level == "blue":
                item.setForeground(QColor("#4a5568"))
            self.output_list.addItem(item)
            self.output_list.scrollToBottom()

    def _setup_progress_system(self):
        """Setup progress tracking system"""
        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._update_progress)
        self._progress_value = 0
        self._paused = False

        # Initial button states
        self._update_progress_buttons(False)

    def _on_key_changed(self):
        """Handle key input change"""
        key = self.key_input.text().strip().upper()
        self.unlock_btn.setEnabled(len(key) > 0 and not self._is_unlocked)

        # Auto unlock if correct key is entered and not already unlocked
        if key == "HT" and not self._is_unlocked:
            self._on_unlock_clicked()

    def _on_unlock_clicked(self):
        """Handle unlock button click"""
        # Skip if already unlocked
        if self._is_unlocked:
            return

        key = self.key_input.text().strip().upper()

        if key == "HT":
            self._is_unlocked = True
            self.key_status.setText("✅ Đã mở khóa")
            self.key_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.unlock_btn.setText("✅ Đã mở")
            self.unlock_btn.setEnabled(False)
            self.key_input.setEnabled(False)
            self._update_tab_buttons_visibility()

            # Show progress bar if currently in Tab 1 (TTS)
            current_tab_index = self.tabs.currentIndex()
            if current_tab_index == 0:  # Tab 1 (TTS)
                self._show_progress_bar()
                self.status.showMessage(
                    "Tab TTS - Đã unlock, progress bar hiển thị")

            # Show success message in log
            self._add_log_item(
                "✅ Xác thực thành công! Các chức năng đã được mở khóa.", level="info")
        else:
            # Wrong key
            self.key_status.setText("❌ Key không đúng")
            self.key_status.setStyleSheet("color: #F44336; font-weight: bold;")
            self.key_input.selectAll()
            self.key_input.setFocus()

            # Show error in log
            self._add_log_item(f"❌ Key không đúng: '{key}'", level="error")

    def _update_tab_buttons_visibility(self):
        """Update visibility of buttons in all tabs based on unlock status"""
        # Update tab buttons if they exist
        if hasattr(self, '_all_tabs'):
            for tab in self._all_tabs:
                if hasattr(tab, 'btn_convert'):
                    tab.btn_convert.setEnabled(self._is_unlocked)
                if hasattr(tab, 'btn_start'):
                    tab.btn_start.setEnabled(self._is_unlocked)
                if hasattr(tab, 'btn_pause'):
                    tab.btn_pause.setEnabled(self._is_unlocked)
                if hasattr(tab, 'btn_resume'):
                    tab.btn_resume.setEnabled(self._is_unlocked)
                if hasattr(tab, 'btn_stop'):
                    tab.btn_stop.setEnabled(self._is_unlocked)
                if hasattr(tab, 'btn_set_progress'):
                    tab.btn_set_progress.setEnabled(self._is_unlocked)

        # Also hide main progress buttons if they exist
        if hasattr(self, 'btn_start'):
            self.btn_start.setEnabled(self._is_unlocked)
        if hasattr(self, 'btn_pause'):
            self.btn_pause.setEnabled(self._is_unlocked)
        if hasattr(self, 'btn_resume'):
            self.btn_resume.setEnabled(self._is_unlocked)
        if hasattr(self, 'btn_stop'):
            self.btn_stop.setEnabled(self._is_unlocked)

    def _setup_connections(self):
        """Setup signal connections"""
        # Progress button connections
        self.btn_start.clicked.connect(self.on_start)
        self.btn_pause.clicked.connect(self.on_pause)
        self.btn_resume.clicked.connect(self.on_resume)
        self.btn_stop.clicked.connect(self.on_stop)

        # Tab change connection - with progress visibility logic
        self.tabs.currentChanged.connect(self._on_tab_changed)

        # History connections
        self._connect_history_signals()

    def _safe_layout_update(self, widget=None):
        """Safely update layouts to prevent UI breaking and QPainter errors"""
        try:
            # Defer the update to avoid paint conflicts
            QTimer.singleShot(10, lambda: self._do_layout_update(widget))
        except Exception as e:
            self._add_log_item(
                f"Layout update error: {str(e)}", level="warning")

    def _do_layout_update(self, widget=None):
        """Perform the actual layout update"""
        try:
            # Update specific widget or progress widget
            target_widget = widget or getattr(self, 'progress_widget', None)

            if target_widget and hasattr(target_widget, 'updateGeometry'):
                target_widget.updateGeometry()
                if hasattr(target_widget, 'layout') and target_widget.layout():
                    target_widget.layout().update()

            # Update main window - less aggressive approach
            if self.centralWidget() and hasattr(self.centralWidget(), 'updateGeometry'):
                self.centralWidget().updateGeometry()
                if hasattr(self.centralWidget(), 'layout') and self.centralWidget().layout():
                    self.centralWidget().layout().update()

        except Exception as e:
            self._add_log_item(
                f"Layout update execution error: {str(e)}", level="warning")

    def _hide_progress_bar(self):
        """Hide progress bar and related elements"""
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.setVisible(False)
        if hasattr(self, '_progress_title') and self._progress_title:
            self._progress_title.setVisible(False)

        # Hide progress control buttons
        buttons = [self.btn_start, self.btn_pause,
                   self.btn_resume, self.btn_stop]
        for btn in buttons:
            if btn:
                btn.setVisible(False)

        # Safe layout update
        self._safe_layout_update()

    def _show_progress_bar(self):
        """Show progress bar and related elements"""
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.setVisible(True)
        if hasattr(self, '_progress_title') and self._progress_title:
            self._progress_title.setVisible(True)

        # Show progress control buttons
        buttons = [self.btn_start, self.btn_pause,
                   self.btn_resume, self.btn_stop]
        for btn in buttons:
            if btn:
                btn.setVisible(True)

        # Safe layout update
        self._safe_layout_update()

    def _on_tab_changed(self, tab_index):
        """Handle tab change - manage progress visibility"""
        # Skip if setup not complete (prevents interference with initial state)
        if not getattr(self, '_setup_complete', False):
            return

        # Close history panels
        self._close_current_tab_history()

        # Handle progress section visibility based on tab
        if hasattr(self, 'progress_widget'):
            if tab_index == 2:  # Tab 3 (Simple) - Hide progress section completely
                self.progress_widget.setVisible(False)
                self.status.showMessage("Tab Simple - Đã ẩn progress section")
            else:  # Tab 1 (TTS) or Tab 2 (Convert) - Show progress section
                self.progress_widget.setVisible(True)

                # Reset toggle button states when switching to tab 2
                if tab_index == 1:  # Convert tab
                    # Ensure all elements are visible and buttons show correct text
                    if hasattr(self, 'progress_bar') and self.progress_bar:
                        self.progress_bar.setVisible(True)
                    if hasattr(self, '_progress_title') and self._progress_title:
                        self._progress_title.setVisible(True)
                    if hasattr(self, 'output_list') and self.output_list:
                        self.output_list.setVisible(True)

                    # Show progress control buttons
                    buttons = [self.btn_start, self.btn_pause,
                               self.btn_resume, self.btn_stop]
                    for btn in buttons:
                        if btn:
                            btn.setVisible(True)

                    # Reset Convert tab toggle buttons to default state
                    convert_tab = self._all_tabs[1]
                    if hasattr(convert_tab, 'btn_toggle_progress'):
                        convert_tab.btn_toggle_progress.setText(
                            "🔽 Ẩn Progress Bar")
                    if hasattr(convert_tab, 'btn_toggle_log'):
                        convert_tab.btn_toggle_log.setText("🔽 Ẩn Log")

                    self.status.showMessage(
                        "Tab Convert - Đã hiện progress section")
                # Tab 1 (TTS) - Hide progress bar only if locked, keep log visible
                elif tab_index == 0:
                    self._hide_progress_bar()
                    # if not self._is_unlocked:
                    #     self._hide_progress_bar()
                    #     self.status.showMessage("Tab TTS - Progress bar ẩn (chưa unlock), log hiển thị")
                    # else:
                    #     self.status.showMessage("Tab TTS - Progress bar hiện (đã unlock), log hiển thị")
                    # Keep log visible
                    if hasattr(self, 'output_list') and self.output_list:
                        self.output_list.setVisible(True)

            # Safe layout update after tab change
            self._safe_layout_update()

    def _connect_history_signals(self):
        """Connect history show/hide signals from tabs"""
        for i, tab in enumerate(self._all_tabs):
            if hasattr(tab, 'history') and tab.history:
                tab.history.request_show_history.connect(
                    lambda checked=False, tab_index=i: self._open_tab_history(tab_index))
                tab.history.request_hide_history.connect(
                    lambda checked=False, tab_index=i: self._close_tab_history(tab_index))

    # Progress Control Methods
    def on_start(self):
        """Start progress"""
        self._reset_progress()
        self._progress_timer.start(30)  # Update every 30ms
        self.status.showMessage("Đang xử lý...")
        self._add_log_item("Bắt đầu xử lý", level="blue")
        self._update_progress_buttons(True)

    def on_pause(self):
        """Pause progress"""
        self._paused = True
        self.status.showMessage("Đã tạm dừng")
        self._add_log_item("Tạm dừng", level="warning")
        self._update_progress_buttons(True, paused=True)

    def on_resume(self):
        """Resume progress"""
        self._paused = False
        self.status.showMessage("Tiếp tục xử lý...")
        self._add_log_item("Tiếp tục", level="blue")
        self._update_progress_buttons(True, paused=False)

    def on_stop(self):
        """Stop progress"""
        self._progress_timer.stop()
        self.status.showMessage("Đã dừng")
        self._add_log_item("Dừng xử lý", level="warning")
        self._update_progress_buttons(False)

    def _update_progress(self):
        """Update progress value"""
        if self._paused:
            return

        self._progress_value += 1
        self.progress_bar.setValue(self._progress_value)

        # Log progress periodically
        if self._progress_value % 20 == 0:
            self._add_log_item(
                f"Tiến trình: {self._progress_value}%", level="blue")

        # Complete when reaching 100%
        if self._progress_value >= 100:
            self._progress_timer.stop()
            self.status.showMessage("Hoàn thành!")
            self._add_log_item("Hoàn thành xử lý", level="info")
            self._update_progress_buttons(False)

            # Processing completed
            pass

    def _update_progress_buttons(self, running: bool, paused: bool = False):
        """Update progress button states"""
        self.btn_start.setEnabled(not running)
        self.btn_pause.setEnabled(running and not paused)
        self.btn_resume.setEnabled(running and paused)
        self.btn_stop.setEnabled(running)

    def _reset_progress(self):
        """Reset progress to initial state"""
        self._progress_value = 0
        self.progress_bar.setValue(0)
        self._paused = False

    # History Management Methods

    def _get_current_tab(self) -> Optional[UIToolbarTab]:
        """Get current active tab"""
        try:
            return self.tabs.currentWidget()
        except Exception:
            return None

    def _get_current_panel(self) -> Optional[HistoryPanel]:
        """Get current tab's history panel"""
        tab = self._get_current_tab()
        if not tab or not hasattr(tab, 'history') or not tab.history:
            return None
        return tab.history.panel

    def _get_tab_index(self, target_tab) -> int:
        """Get index of a specific tab"""
        try:
            return self._all_tabs.index(target_tab)
        except (ValueError, AttributeError):
            return -1

    def _toggle_current_tab_history(self):
        """Toggle current tab's history panel"""
        panel = self._get_current_panel()
        if not panel:
            return

        if panel.isHidden():
            self._open_current_tab_history()
        else:
            self._close_current_tab_history()

    def _open_tab_history(self, tab_index: int):
        """Open specific tab's history panel"""
        if tab_index < 0 or tab_index >= len(self._all_tabs):
            return

        tab = self._all_tabs[tab_index]
        if not hasattr(tab, 'history') or not tab.history:
            return

        panel = tab.history.panel
        if not panel:
            return

        # Tab-specific logic
        tab_name = self.tabs.tabText(tab_index)
        print(f"Opening history for {tab_name} (tab {tab_index})")

        if tab_index == 0:  # TTS Tab
            self._add_log_item(
                f"[{datetime.now().strftime('%H:%M:%S')}] 🎤 Mở lịch sử TTS")
        elif tab_index == 1:  # Convert Tab
            self._add_log_item(
                f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Mở lịch sử Convert")
        elif tab_index == 2:  # Simple Tab
            self._add_log_item(
                f"[{datetime.now().strftime('%H:%M:%S')}] 📝 Mở lịch sử Simple")

        # Close other panels first
        for i, other_tab in enumerate(self._all_tabs):
            if (i != tab_index and hasattr(other_tab, 'history') and other_tab.history and
                    other_tab.history.panel != panel and not other_tab.history.panel.isHidden()):
                other_tab.history.panel.hide()

        # Show current panel
        panel.dock_right()
        panel.show_with_animation(self.width())

        # Update UI state
        self._set_tabs_enabled(False)
        self._show_overlay()

    def _close_tab_history(self, tab_index: int):
        """Close specific tab's history panel"""
        if tab_index < 0 or tab_index >= len(self._all_tabs):
            return

        tab = self._all_tabs[tab_index]
        if not hasattr(tab, 'history') or not tab.history:
            return

        panel = tab.history.panel
        if not panel or panel.isHidden():
            return

        # Tab-specific logic
        tab_name = self.tabs.tabText(tab_index)
        print(f"Closing history for {tab_name} (tab {tab_index})")

        if tab_index == 0:  # TTS Tab
            self._add_log_item(
                f"[{datetime.now().strftime('%H:%M:%S')}] 🎤 Đóng lịch sử TTS")
            # TTS specific cleanup
        elif tab_index == 1:  # Convert Tab
            self._add_log_item(
                f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Đóng lịch sử Convert")
            # Convert specific cleanup
        elif tab_index == 2:  # Simple Tab
            self._add_log_item(
                f"[{datetime.now().strftime('%H:%M:%S')}] 📝 Đóng lịch sử Simple")
            # Simple specific cleanup

        # Prevent recursion
        if hasattr(self, '_closing_history') and self._closing_history:
            return

        self._closing_history = True
        try:
            panel.hide()
            self._set_tabs_enabled(True)
            self._hide_overlay()
        finally:
            self._closing_history = False

    def _open_current_tab_history(self):
        """Open current tab's history panel"""
        panel = self._get_current_panel()
        if not panel:
            return

        # Close other panels first
        for tab in self._all_tabs:
            if (hasattr(tab, 'history') and tab.history and
                    tab.history.panel != panel and not tab.history.panel.isHidden()):
                tab.history.panel.hide()  # Direct hide to avoid recursion

        # Show current panel
        panel.dock_right()
        panel.show_with_animation(self.width())

        # Update UI state
        self._set_tabs_enabled(False)
        self._show_overlay()
        # Hide the floating close button, use only panel's X button
        # self.close_history_btn.show()
        # self._position_close_history_btn(panel)

    def _close_current_tab_history(self):
        """Close current tab's history panel"""
        # Prevent recursion
        if hasattr(self, '_closing_history') and self._closing_history:
            return

        self._closing_history = True
        try:
            panel = self._get_current_panel()

            # Close panel if open
            if panel and not panel.isHidden():
                # Close without triggering callback to prevent recursion
                panel.hide()  # Direct hide instead of close_panel()

            # Restore UI state
            self._set_tabs_enabled(True)
            # self.close_history_btn.hide()  # Already hidden
            self._hide_overlay()
        finally:
            self._closing_history = False

    def _set_tabs_enabled(self, enabled: bool):
        """Enable/disable tab switching but keep content interactive"""
        # Only disable tab bar, not the tab content
        self.tabs.tabBar().setEnabled(enabled)

        # Update progress buttons based on current state
        running = self._progress_timer.isActive()
        paused = self._paused
        self._update_progress_buttons(running, paused)

    def _show_overlay(self):
        """Show click-to-close overlay that doesn't block main content"""
        menubar_height = self.menuBar().height()
        panel = self._get_current_panel()

        if panel:
            # Overlay only covers the area not occupied by the panel
            overlay_width = self.width() - panel.width()
            self.overlay.setGeometry(
                0, menubar_height, overlay_width, self.height() - menubar_height)
        else:
            # Fallback: cover entire area
            self.overlay.setGeometry(
                0, menubar_height, self.width(), self.height() - menubar_height)

        self.overlay.show()
        self.overlay.raise_()

        # Ensure panel is on top
        if panel:
            panel.raise_()

    def _hide_overlay(self):
        """Hide overlay"""
        self.overlay.hide()

    def _position_close_history_btn(self, panel: HistoryPanel):
        """Position the floating close button"""
        if self.close_history_btn.isHidden():
            return

        menubar_height = self.menuBar().height()
        x = panel.x() - self.close_history_btn.width() - 8
        y = menubar_height + 8
        self.close_history_btn.move(x, y)

    # Toast Management

    def _center_on_screen(self):
        """Center the window on screen"""
        try:
            from PySide6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.availableGeometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
        except Exception:
            # Fallback: just use default position
            pass

    # Event Handlers
    def resizeEvent(self, event):
        """Handle window resize with safe UI updates"""
        try:
            super().resizeEvent(event)

            # Only reposition if not minimized and panel is visible
            if not self.isMinimized():
                panel = self._get_current_panel()
                if panel and not panel.isHidden():
                    # Use timer to defer repositioning and avoid paint conflicts
                    QTimer.singleShot(
                        50, lambda: self._safe_resize_panel(panel))
        except Exception as e:
            self._add_log_item(
                f"Resize event error: {str(e)}", level="warning")

    def _safe_resize_panel(self, panel):
        """Safely reposition panel after resize"""
        try:
            if panel and not panel.isHidden() and not self.isMinimized():
                panel.dock_right()
                self._show_overlay()
        except Exception as e:
            self._add_log_item(
                f"Panel resize error: {str(e)}", level="warning")

    def changeEvent(self, event):
        """Handle window state changes (minimize/restore)"""
        try:
            super().changeEvent(event)

            # Handle window state changes
            if event.type() == QEvent.Type.WindowStateChange:
                if self.isMinimized():
                    # Hide history panels when minimized to prevent paint issues
                    self._close_current_tab_history()
                elif self.windowState() == Qt.WindowState.WindowNoState:
                    # Window restored - defer UI updates to avoid paint conflicts
                    QTimer.singleShot(100, self._on_window_restored)

        except Exception as e:
            self._add_log_item(
                f"Window state change error: {str(e)}", level="warning")

    def _on_window_restored(self):
        """Handle window restore with safe UI updates"""
        try:
            # Force a safe layout update after restoration
            self._safe_layout_update()
        except Exception as e:
            self._add_log_item(
                f"Window restore error: {str(e)}", level="warning")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application properties
    # app.setApplicationName("TranslatePro")
    # app.setApplicationVersion("1.2.0")
    # app.setOrganizationName("J2TEAM")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    try:
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error in event loop: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
