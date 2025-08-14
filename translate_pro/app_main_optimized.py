"""
TranslatePro - Text to Speech Application
Optimized version with improved structure and performance
"""

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QScrollArea, QFrame, QTextEdit, QPlainTextEdit, QProgressBar,
    QMainWindow, QTabWidget, QStatusBar, QLineEdit, QGroupBox
)
from PySide6.QtCore import Qt, QTimer, QRect, Signal, QObject
from PySide6.QtGui import QAction, QIntValidator
import sys
import traceback
from datetime import datetime
from typing import Optional, Callable, List, Tuple, Any


class AppConfig:
    """Application configuration constants"""
    WINDOW_TITLE = "J2TEAM - Text to Speech (v1.2.0)"
    MIN_WINDOW_SIZE = (800, 600)
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
    MAIN_STYLE = "background-color: #1a1c24; color: white; font-size: 13px;"
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
        close_btn.setStyleSheet("color: white; background: transparent; border: none;")
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

    def preload_items(self, items_with_meta: List[Tuple[str, Optional[dict]]]):
        """Preload history items"""
        self._clear_history_silent()
        for text, meta in items_with_meta:
            self.add_history(text, meta=meta)

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
                 on_item_selected: Optional[Callable] = None,
                 preload_list: Optional[List[Tuple[str, Optional[dict]]]] = None):
        super().__init__(parent_main)
        
        # History button
        self.btn = QPushButton("🕘 Lịch sử")
        self.btn.setStyleSheet("background-color:#2b2d3a; border:1px solid #444; border-radius:6px; padding:8px; font-size:12px;")
        self.btn.clicked.connect(self.request_show_history.emit)
        
        # History panel
        self.panel = HistoryPanel(
            title_text=hist_title,
            item_factory=item_factory,
            on_item_selected=on_item_selected,
            close_callback=self._on_panel_closed,
            parent=parent_main
        )
        
        if preload_list:
            self.panel.preload_items(preload_list)

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
                      on_item_selected: Optional[Callable] = None,
                      preload_list: Optional[List[Tuple[str, Optional[dict]]]] = None) -> HistoryFeature:
        """Enable history functionality for this tab"""
        self.history = HistoryFeature(
            parent_main=self.parent_main,
            hist_title=hist_title,
            item_factory=item_factory,
            on_item_selected=on_item_selected,
            preload_list=preload_list
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

    def _setup_ui(self):
        """Setup the TTS tab UI"""
        root_layout = self.layout()

        # Enable history first to get the button
        hist = self.enable_history(
            hist_title="Lịch sử TTS",
            item_factory=lambda text, ts, lang, meta: TTSHistoryItem(text, ts, lang, meta),
            preload_list=[("TTS Demo 1", None), ("TTS Demo 2", None)],
            on_item_selected=self._on_history_selected
        )

        # Header with title and history button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        
        title = QLabel("Text to Speech")
        title.setStyleSheet("font-weight:600; font-size:16px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(hist.btn)
        
        root_layout.insertLayout(0, header_layout)

        # Body with text input
        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        
        self.text_input = QPlainTextEdit()
        self.text_input.setPlaceholderText("Nhập văn bản để chuyển đổi thành giọng nói...")
        self.text_input.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2a2d3a;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                min-height: 80px;
            }
        """)
        body_layout.addWidget(self.text_input)
        
        root_layout.insertLayout(1, body_layout)

        # Convert button in toolbar
        self.btn_convert = QPushButton("🔊 Chuyển đổi TTS")
        self.btn_convert.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppConfig.COLORS['success']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        self.btn_convert.clicked.connect(self._on_convert_clicked)
        self.toolbar.addWidget(self.btn_convert)

    def _on_convert_clicked(self):
        """Handle convert button click"""
        text = self.text_input.toPlainText().strip()
        if not text:

            return
            
        # Add to history
        self.append_history(text)
        
        # Log to main window if available
        if hasattr(self.parent_main, "text_log"):
            self.parent_main.text_log.append(f"[TTS] {text[:60]}{'...' if len(text) > 60 else ''}")
        


    def _on_history_selected(self, text: str):
        """Handle history item selection"""
        self.text_input.setPlainText(text)
        self.text_input.setFocus()
        
        # Hide history panel
        # if self.history:
        #     self.history.request_hide_history.emit()


class ConvertTab(UIToolbarTab):
    """Convert tab with progress controls and improved functionality"""
    
    def __init__(self, parent_main: QWidget):
        super().__init__(parent_main)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the Convert tab UI"""
        # Main body layout
        body_layout = QVBoxLayout()
        
        # Text input area
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Nhập văn bản để chuyển đổi...")
        self.text_input.setStyleSheet("""
            QTextEdit {
                background-color: #2a2d3a;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                min-height: 80px;
            }
        """)
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
            item_factory=lambda text, ts, lang, meta: ConvertHistoryItem(text, ts, lang, meta),
            preload_list=[("Convert Demo A", None), ("Convert Demo B", None)],
            on_item_selected=self._on_history_selected
        )
        hist_layout.addWidget(hist.btn)
        parent_layout.addLayout(hist_layout)

    def _setup_convert_button(self, parent_layout: QVBoxLayout):
        """Setup convert button"""
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
            main_window.text_log.append("[Progress] Hoàn thành (đặt từ ConvertTab)")
            main_window._update_progress_buttons(False)
        else:
            main_window.status.showMessage(f"Đã đặt tiến trình: {value}%")
            main_window.text_log.append(f"[Progress] Đặt {value}% (ConvertTab)")

    def _on_convert_clicked(self):
        """Handle convert button click"""
        text = self.text_input.toPlainText().strip()
        if not text:

            return

        # Add to history
        self.append_history(text)
        
        # Log to main window
        if hasattr(self.parent_main, "text_log"):
            self.parent_main.text_log.append(f"[Convert] {text[:60]}{'...' if len(text) > 60 else ''}")
        


    def _on_history_selected(self, text: str):
        """Handle history item selection"""
        self.text_input.setPlainText(text)
        self.text_input.setFocus()
        
        if self.history:
            self.history.request_hide_history.emit()


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
        self._setup_window()
        self._setup_ui()
        self._setup_progress_system()
        self._setup_connections()

    def _setup_window(self):
        """Setup main window properties"""
        self.setWindowTitle(AppConfig.WINDOW_TITLE)
        self.setMinimumSize(*AppConfig.MIN_WINDOW_SIZE)
        self.resize(*AppConfig.DEFAULT_WINDOW_SIZE)  # Set default size
        self.setStyleSheet(AppConfig.MAIN_STYLE)
        
        # Center window on screen
        self._center_on_screen()

    def _setup_ui(self):
        """Setup the main UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Create tabs
        self.tab_tts = TTSTab(self)
        self.tab_convert = ConvertTab(self)
        self.tab_simple = SimpleTab(self)
        
        self._all_tabs = [self.tab_tts, self.tab_convert, self.tab_simple]

        # Add tabs to widget
        self.tabs.addTab(self.tab_tts, "Text to Speech")
        self.tabs.addTab(self.tab_convert, "Convert")
        self.tabs.addTab(self.tab_simple, "Simple")

        # Progress and log section
        self._setup_progress_ui(main_layout)
        
        # Overlay and controls
        self._setup_overlay_controls()
        
        # Menu and status bar
        self._setup_menu_and_status()
        
        # Initialize button visibility based on lock state
        self._update_tab_buttons_visibility()

    def _setup_progress_ui(self, parent_layout: QVBoxLayout):
        """Setup progress UI section"""
        progress_widget = QWidget()
        progress_layout = QVBoxLayout(progress_widget)
        
        # Key Authentication Group Box
        self._setup_key_auth_group(progress_layout)
        
        # Title
        title = QLabel("Tiến trình xử lý")
        title.setStyleSheet("font-size: 16px; font-weight: 600; margin-bottom: 10px;")
        progress_layout.addWidget(title)
        
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
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ Bắt đầu")
        self.btn_pause = QPushButton("⏸ Tạm dừng")
        self.btn_resume = QPushButton("⏯ Tiếp tục")
        self.btn_stop = QPushButton("⏹ Dừng")
        
        for btn in (self.btn_start, self.btn_pause, self.btn_resume, self.btn_stop):
            btn.setStyleSheet(AppConfig.BUTTON_STYLE)
            button_layout.addWidget(btn)
        
        button_layout.addStretch()
        progress_layout.addLayout(button_layout)
        
        # Log area
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setPlaceholderText("Log hệ thống...")
        self.text_log.setStyleSheet("""
            QTextEdit {
                background-color: #151720;
                border: 1px solid #2a2d3a;
                border-radius: 6px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                padding: 8px;
            }
        """)
        self.text_log.setMaximumHeight(100)
        progress_layout.addWidget(self.text_log)
        
        parent_layout.addWidget(progress_widget)

    def _setup_key_auth_group(self, parent_layout: QVBoxLayout):
        """Setup key authentication group box"""
        # Group box
        key_group = QGroupBox("🔐 Xác thực truy cập")
        key_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #444;
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
        
        # Key input
        key_label = QLabel("Nhập key:")
        key_label.setStyleSheet("font-weight: normal; margin-right: 5px;")
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Nhập key để mở khóa...")
        self.key_input.setFixedWidth(150)
        self.key_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2d3a;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
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
        
        # Status label
        self.key_status = QLabel("🔒 Đã khóa")
        self.key_status.setStyleSheet("color: #FF6B35; font-weight: bold;")
        
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_input)
        key_layout.addWidget(self.unlock_btn)
        key_layout.addWidget(self.key_status)
        key_layout.addStretch()
        
        parent_layout.addWidget(key_group)
        
        # Initialize locked state
        self._is_unlocked = False
        # Note: _update_tab_buttons_visibility() will be called after UI setup is complete

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
        toggle_history_action.triggered.connect(self._toggle_current_tab_history)
        view_menu.addAction(toggle_history_action)
        
        close_history_action = QAction("Đóng lịch sử (Esc)", self)
        close_history_action.setShortcut("Esc")
        close_history_action.triggered.connect(self._close_current_tab_history)
        view_menu.addAction(close_history_action)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Sẵn sàng")

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
        self.unlock_btn.setEnabled(len(key) > 0)
        
        # Auto unlock if correct key is entered
        if key == "HT":
            self._on_unlock_clicked()

    def _on_unlock_clicked(self):
        """Handle unlock button click"""
        key = self.key_input.text().strip().upper()
        
        if key == "HT":
            self._is_unlocked = True
            self.key_status.setText("✅ Đã mở khóa")
            self.key_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.unlock_btn.setText("✅ Đã mở")
            self.unlock_btn.setEnabled(False)
            self.key_input.setEnabled(False)
            self._update_tab_buttons_visibility()
            
            # Show success message in log
            self.text_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Xác thực thành công! Các chức năng đã được mở khóa.")
        else:
            # Wrong key
            self.key_status.setText("❌ Key không đúng")
            self.key_status.setStyleSheet("color: #F44336; font-weight: bold;")
            self.key_input.selectAll()
            self.key_input.setFocus()
            
            # Show error in log
            self.text_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Key không đúng: '{key}'")

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
        
        # Tab change connection
        self.tabs.currentChanged.connect(lambda: self._close_current_tab_history())
        
        # History connections
        self._connect_history_signals()

    def _connect_history_signals(self):
        """Connect history show/hide signals from tabs"""
        for i, tab in enumerate(self._all_tabs):
            if hasattr(tab, 'history') and tab.history:
                tab.history.request_show_history.connect(lambda checked=False, tab_index=i: self._open_tab_history(tab_index))
                tab.history.request_hide_history.connect(lambda checked=False, tab_index=i: self._close_tab_history(tab_index))

    # Progress Control Methods
    def on_start(self):
        """Start progress"""
        self._reset_progress()
        self._progress_timer.start(30)  # Update every 30ms
        self.status.showMessage("Đang xử lý...")
        self.text_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Bắt đầu xử lý")
        self._update_progress_buttons(True)

    def on_pause(self):
        """Pause progress"""
        self._paused = True
        self.status.showMessage("Đã tạm dừng")
        self.text_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Tạm dừng")
        self._update_progress_buttons(True, paused=True)

    def on_resume(self):
        """Resume progress"""
        self._paused = False
        self.status.showMessage("Tiếp tục xử lý...")
        self.text_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Tiếp tục")
        self._update_progress_buttons(True, paused=False)

    def on_stop(self):
        """Stop progress"""
        self._progress_timer.stop()
        self.status.showMessage("Đã dừng")
        self.text_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Dừng xử lý")
        self._update_progress_buttons(False)

    def _update_progress(self):
        """Update progress value"""
        if self._paused:
            return
            
        self._progress_value += 1
        self.progress_bar.setValue(self._progress_value)
        
        # Log progress periodically
        if self._progress_value % 20 == 0:
            self.text_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Tiến trình: {self._progress_value}%")
        
        # Complete when reaching 100%
        if self._progress_value >= 100:
            self._progress_timer.stop()
            self.status.showMessage("Hoàn thành!")
            self.text_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Hoàn thành xử lý")
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
            self.text_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🎤 Mở lịch sử TTS")
        elif tab_index == 1:  # Convert Tab  
            self.text_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Mở lịch sử Convert")
        elif tab_index == 2:  # Simple Tab
            self.text_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📝 Mở lịch sử Simple")

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
            self.text_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🎤 Đóng lịch sử TTS")
            # TTS specific cleanup
        elif tab_index == 1:  # Convert Tab
            self.text_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Đóng lịch sử Convert") 
            # Convert specific cleanup
        elif tab_index == 2:  # Simple Tab
            self.text_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📝 Đóng lịch sử Simple")
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
            self.overlay.setGeometry(0, menubar_height, overlay_width, self.height() - menubar_height)
        else:
            # Fallback: cover entire area
            self.overlay.setGeometry(0, menubar_height, self.width(), self.height() - menubar_height)
            
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
        """Handle window resize"""
        super().resizeEvent(event)
        
        # Reposition history panel if open
        panel = self._get_current_panel()
        if panel and not panel.isHidden():
            panel.dock_right()
            # self._position_close_history_btn(panel)  # Not used anymore
            self._show_overlay()
        



def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("TranslatePro")
    app.setApplicationVersion("1.2.0")
    app.setOrganizationName("J2TEAM")
    
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
