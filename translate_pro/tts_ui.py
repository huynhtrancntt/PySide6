import sys
import os
import json
import asyncio
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import (
    QThread, Signal, QObject, Qt, QUrl, QPoint, QTimer
)
from PySide6.QtGui import QDesktopServices, QAction
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QComboBox, QMessageBox, QFileDialog,
    QListWidget, QListWidgetItem, QMenu, QSlider, QFrame,
    QMainWindow, QTabWidget, QProgressBar, QGroupBox, QFormLayout, QLineEdit, QSplitter
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

import edge_tts
import pygame
try:
    from ui_setting import _init_addStyle  # có thì dùng, không có thì bỏ qua
except Exception:
    def _init_addStyle(*args, **kwargs): ...
os.environ.setdefault("SDL_AUDIODRIVER", "directsound")


# ========================= Helpers =========================
def human_size(num_bytes: int) -> str:
    """Đổi bytes -> chuỗi kích thước dễ đọc"""
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for u in units:
        if size < 1024.0 or u == units[-1]:
            return f"{size:.0f} {u}" if u == "B" else f"{size:.2f} {u}"
        size /= 1024.0


def human_duration(sec: float | None) -> str:
    """Đổi số giây -> chuỗi hh:mm:ss ngắn gọn"""
    if sec is None or sec <= 0:
        return "?"
    sec = int(round(sec))
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if h > 0:
        return f"{h}h{m:02d}m{s:02d}s"
    if m > 0:
        return f"{m}m{s:02d}s"
    return f"{s}s"


def mmss(ms: int) -> str:
    """Đổi milliseconds -> m:ss"""
    if ms <= 0:
        return "0:00"
    sec = ms // 1000
    m = sec // 60
    s = sec % 60
    return f"{m}:{s:02d}"


def audio_duration_seconds(path: Path) -> float | None:
    """Ưu tiên mutagen, fallback pygame để lấy duration file audio"""
    try:
        from mutagen import File as MutagenFile  # type: ignore
        mf = MutagenFile(str(path))
        if mf is not None and getattr(mf, "info", None):
            dur = getattr(mf.info, "length", None)
            if dur:
                return float(dur)
    except Exception:
        pass
    try:
        snd = pygame.mixer.Sound(str(path))
        return float(snd.get_length())
    except Exception:
        return None


# ========================= AppBus (kênh chia sẻ) =========================
class AppBus(QObject):
    """Bus signal dùng chung giữa các widget"""
    append_output = Signal(str)     # log dùng chung
    set_progress = Signal(int)      # progress dùng chung
    add_history_path = Signal(str)  # thêm item lịch sử
    toggle_history = Signal(bool)   # bật/tắt panel lịch sử (phải)


# ========================= Worker Edge TTS =========================
class EdgeTTSWorker(QObject):
    """Worker chạy trong thread để gọi edge-tts"""
    finished = Signal()
    error = Signal(str)
    status = Signal(str)
    progress = Signal(int)
    file_ready = Signal(str)

    def __init__(self, text: str, lang_code: str, gender: str, rate: int, save_path: Path | None = None):
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


# ========================= HistoryPanel (kiểu bạn yêu cầu) =========================
class HistoryPanel(QWidget):
    """
    Panel lịch sử dạng cột phải, rộng cố định 300.
    Ẩn/hiện bằng bus.toggle_history(bool).
    """
    playRequested = Signal(Path)

    def __init__(self, close_callback=None, toast_callback=None, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)
        # self.setStyleSheet("background-color: #12131c;")
        self.toast_callback = toast_callback

        self.audio_root = Path.cwd() / "audio"

        # --- UI ---
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 10, 10, 10)

        # Thanh tiêu đề + nút đóng
        bar = QHBoxLayout()
        title = QLabel("📜 Lịch sử chuyển đổi")
        bar.addWidget(title)
        bar.addStretch(1)
        btn_close = QPushButton("✕")
        btn_close.setFixedWidth(28)
        btn_close.clicked.connect(
            lambda: close_callback() if close_callback else None)
        bar.addWidget(btn_close)
        lay.addLayout(bar)

        # Danh sách lịch sử
        self.lst = QListWidget()
        self.lst.setSelectionMode(QListWidget.SingleSelection)
        self.lst.itemDoubleClicked.connect(self._on_play_selected)
        self.lst.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lst.customContextMenuRequested.connect(self._on_context_menu)
        lay.addWidget(self.lst, 1)

        # Hàng nút thao tác
        rowb = QHBoxLayout()
        self.btn_play = QPushButton("▶️ Phát")
        self.btn_del = QPushButton("🗑️ Xóa")
        self.btn_open_root = QPushButton("📂 Thư mục")
        for b in (self.btn_play, self.btn_del, self.btn_open_root):
            rowb.addWidget(b)
        self.btn_play.clicked.connect(self._on_play_selected)
        self.btn_del.clicked.connect(self._delete_selected)
        self.btn_open_root.clicked.connect(self._open_root)
        lay.addLayout(rowb)

        self.refresh()

    # ===== API =====
    def refresh(self):
        """Nạp lại danh sách mp3 theo thời gian mới nhất"""
        self.lst.clear()
        if not self.audio_root.exists():
            return
        files = []
        for p in self.audio_root.rglob("*.mp3"):
            try:
                files.append((p.stat().st_mtime, p))
            except FileNotFoundError:
                pass
        files.sort(key=lambda t: t[0], reverse=True)
        for _, p in files:
            self._add_item(p, False)

    def add_item_top(self, p: Path):
        """Thêm item mới lên đầu"""
        self._add_item(p, True)

    # ===== Internals =====
    def _add_item(self, p: Path, insert_top: bool):
        if not p.exists():
            return
        try:
            st = p.stat()
            mtime_str = datetime.fromtimestamp(
                st.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            size_str = human_size(st.st_size)
            dur_str = human_duration(audio_duration_seconds(p))
        except Exception:
            mtime_str = size_str = dur_str = "?"
        text = f"{p.name}\n{mtime_str} · {dur_str} · {size_str}"
        it = QListWidgetItem(text)
        it.setData(Qt.UserRole, str(p))
        if insert_top:
            self.lst.insertItem(0, it)
            self.lst.setCurrentItem(it)
        else:
            self.lst.addItem(it)

    def _current_path(self) -> Path | None:
        it = self.lst.currentItem()
        if not it:
            QMessageBox.information(self, "Chú ý", "Hãy chọn một file.")
            return None
        p = Path(it.data(Qt.UserRole))
        if not p.exists():
            QMessageBox.warning(self, "Không tìm thấy",
                                f"File không còn tồn tại:\n{p}")
            self.refresh()
            return None
        return p

    def _on_play_selected(self):
        p = self._current_path()
        if p:
            self.playRequested.emit(p)

    def _delete_selected(self):
        p = self._current_path()
        if not p:
            return
        ret = QMessageBox.question(self, "Xác nhận", f"Xóa {p.name} và .txt kèm theo?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret != QMessageBox.Yes:
            return
        try:
            for ext in (".mp3", ".txt"):
                f = p.with_suffix(ext)
                if f.exists():
                    f.unlink(missing_ok=True)
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi xóa", str(e))

    def _open_root(self):
        root = self.audio_root
        if os.name == "nt":
            os.startfile(root)  # type: ignore[attr-defined]
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(root)))

    def _on_context_menu(self, pos: QPoint):
        it = self.lst.itemAt(pos)
        if not it:
            return
        self.lst.setCurrentItem(it)
        menu = QMenu(self)
        menu.addAction("▶️ Phát", self._on_play_selected)
        menu.addAction("📂 Mở thư mục chứa",
                       lambda: self._open_containing_dir(Path(it.data(Qt.UserRole))))
        menu.addSeparator()
        menu.addAction("🗑️ Xóa (kèm .txt)", self._delete_selected)
        menu.exec(self.lst.mapToGlobal(pos))

    def _open_containing_dir(self, p: Path):
        folder = p.parent
        if os.name == "nt":
            try:
                os.startfile(folder)  # type: ignore[attr-defined]
            except Exception:
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))


# ========================= Tab TTS (gộp TTSWindow vào bên trái) =========================
class TTSTab(QWidget):
    """Toàn bộ UI TTS (nhập văn bản, chọn voice, player...) đặt trong 1 tab"""

    def __init__(self, bus: AppBus):
        super().__init__()
        self.bus = bus
        self.worker_thread: QThread | None = None
        self.worker: EdgeTTSWorker | None = None

        self.audio_root = Path.cwd() / "audio"
        self.audio_root.mkdir(parents=True, exist_ok=True)

        # Player Qt
        self.player = QMediaPlayer(self)
        self.audio_out = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_out)

        self._build_ui()
        try:
            _init_addStyle(self)
        except Exception:
            pass

        # Player signals
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.playbackStateChanged.connect(
            self._on_playback_state_changed)

    def _build_ui(self):
        root = QVBoxLayout(self)

        # soạn văn bản + lựa chọn
        left = QVBoxLayout()
        left.addWidget(QLabel("Nội dung cần nói:"))
        self.txt = QTextEdit(placeholderText="Nhập văn bản tại đây…")
        self.txt.setPlainText("Xin chào! Đây là giọng nói tiếng Việt.")
        left.addWidget(self.txt)

        row = QHBoxLayout()
        row.addWidget(QLabel("Ngôn ngữ:"))
        self.cmb_lang = QComboBox()
        for label, code in [
            ("Vietnamese (vi)", "vi"), ("English US (en-US)", "en-US"),
            ("English UK (en-GB)", "en-GB"), ("Japanese (ja)", "ja"),
            ("Korean (ko)", "ko"), ("Chinese (zh-CN)", "zh-CN"),
            ("French (fr-FR)", "fr-FR"), ("German (de-DE)", "de-DE"),
            ("Spanish (es-ES)", "es-ES"),
        ]:
            self.cmb_lang.addItem(label, code)
        self.cmb_lang.setCurrentIndex(0)
        row.addWidget(self.cmb_lang)

        row.addWidget(QLabel("Giới tính:"))
        self.cmb_gender = QComboBox()
        self.cmb_gender.addItems(["Female", "Male", "Any"])
        self.cmb_gender.setCurrentText("Female")
        row.addWidget(self.cmb_gender)

        row.addWidget(QLabel("Tốc độ:"))
        self.sld_rate = QSlider(Qt.Horizontal)
        self.sld_rate.setRange(50, 250)
        self.sld_rate.setValue(150)
        self.sld_rate.setTickInterval(10)
        # show mốc nhỏ để kéo mượt
        self.sld_rate.setTickPosition(QSlider.TicksBelow)
        self.sld_rate.setSingleStep(1)
        self.sld_rate.setPageStep(10)
        self.sld_rate.setFixedWidth(160)
        row.addWidget(self.sld_rate)

        self.lbl_rate_val = QLabel("150")
        self.sld_rate.valueChanged.connect(
            lambda v: self.lbl_rate_val.setText(str(v)))
        row.addWidget(self.lbl_rate_val)
        left.addLayout(row)

        # cụm nút điều khiển
        btns = QHBoxLayout()
        self.btn_say = QPushButton("▶️ Phát")
        self.btn_save = QPushButton("💾 Lưu")
        self.btn_stop = QPushButton("⏹️ Dừng")
        btns.addWidget(self.btn_say)
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_stop)
        left.addLayout(btns)

        # Nút bật/tắt panel lịch sử (bên phải)
        self.btn_toggle_history = QPushButton("📜 Lịch sử (bên phải)")
        self.btn_toggle_history.setCheckable(True)
        self.btn_toggle_history.toggled.connect(self.bus.toggle_history)
        left.addWidget(self.btn_toggle_history)

        self.lbl_status = QLabel("Sẵn sàng.")
        left.addWidget(self.lbl_status)
        root.addLayout(left)

        # thanh player đơn giản
        player_bar = QHBoxLayout()
        self.player_panel = QFrame()
        pnl = QHBoxLayout(self.player_panel)
        pnl.setContentsMargins(8, 8, 8, 8)

        self.btn_player_play = QPushButton("⏵")
        self.btn_player_play.setFixedWidth(36)
        self.btn_player_play.clicked.connect(self._toggle_play_pause)
        pnl.addWidget(self.btn_player_play)

        self.lbl_time_cur = QLabel("0:00")
        self.lbl_time_tot = QLabel("/ 0:00")
        pnl.addWidget(self.lbl_time_cur)

        self.sld_position = QSlider(Qt.Horizontal)
        self.sld_position.setRange(0, 0)
        self.sld_position.sliderPressed.connect(self._position_slider_pressed)
        self.sld_position.sliderReleased.connect(
            self._position_slider_released)
        self.sld_position.sliderMoved.connect(self._position_slider_moved)
        pnl.addWidget(self.sld_position, stretch=1)
        pnl.addWidget(self.lbl_time_tot)

        self.lbl_vol = QLabel("🔊")
        pnl.addWidget(self.lbl_vol)
        self.sld_volume = QSlider(Qt.Horizontal)
        self.sld_volume.setRange(0, 100)
        self.sld_volume.setValue(80)
        self.sld_volume.setFixedWidth(140)
        self.sld_volume.valueChanged.connect(
            lambda v: self.audio_out.setVolume(v/100.0))
        pnl.addWidget(self.sld_volume)

        self.player_panel.hide()  # ẩn cho đến khi có file để play
        player_bar.addWidget(self.player_panel)
        root.addLayout(player_bar)

        # gắn sự kiện
        self.btn_say.clicked.connect(self.on_say)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_stop.clicked.connect(self.on_stop)

        self._seeking = False

    # ===== Worker control =====
    def on_say(self):
        self._start_worker(play_only=True)

    def on_save(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Lưu file âm thanh", "tts_output.mp3", "MP3 Files (*.mp3)")
        if path:
            self._start_worker(play_only=False, save_path=path)

    def on_stop(self):
        self.player.stop()
        self.lbl_status.setText("Đã dừng.")
        self.bus.append_output.emit("Đã dừng phát.")

    def _start_worker(self, play_only=True, save_path=None):
        text = self.txt.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Thiếu nội dung",
                                "Hãy nhập văn bản cần đọc.")
            return
        lang_code = self.cmb_lang.currentData() or "vi"
        gender = self.cmb_gender.currentText()
        if gender == "Any":
            gender = "Female"
        rate = self.sld_rate.value()

        # trạng thái
        self.btn_say.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.lbl_status.setText("Đang xử lý…")

        # báo cho MainWindow hiện progress
        self.bus.set_progress.emit(1)

        self.worker_thread = QThread()
        self.worker = EdgeTTSWorker(
            text, lang_code, gender, rate, save_path=save_path)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.status.connect(self._on_worker_status)
        self.worker.progress.connect(self.bus.set_progress)
        self.worker.error.connect(self._on_error)
        self.worker.finished.connect(self._finished_tts)
        self.worker.file_ready.connect(self._on_file_ready)
        self.worker_thread.start()

    def _on_worker_status(self, msg: str):
        self.lbl_status.setText(msg)
        self.bus.append_output.emit(msg)

    def _on_error(self, msg: str):
        QMessageBox.critical(self, "Lỗi", msg)
        self.bus.append_output.emit("Lỗi: " + msg)

    def _finished_tts(self):
        self.btn_say.setEnabled(True)
        self.btn_save.setEnabled(True)
        # đẩy progress tới 100 để MainWindow tự ẩn
        self.bus.set_progress.emit(100)
        self.bus.append_output.emit("Sẵn sàng.")
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None
            self.worker = None

    def _on_file_ready(self, path_str: str):
        p = Path(path_str)
        self._play_external(p)
        self.bus.add_history_path.emit(str(p))
        self.bus.append_output.emit(f"Đã tạo file: {p.name}")

    # ===== Player helpers =====
    def _play_external(self, p: Path):
        self.player.setSource(QUrl.fromLocalFile(str(p)))
        self.player_panel.show()
        self.player.play()
        self.lbl_status.setText(f"Trình phát: {p.name}")

    def _toggle_play_pause(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def _on_duration_changed(self, dur_ms: int):
        self.sld_position.setRange(0, max(0, dur_ms))
        self.lbl_time_tot.setText(f"/ {mmss(dur_ms)}")

    def _on_position_changed(self, pos_ms: int):
        if not self._seeking:
            self.sld_position.setValue(pos_ms)
        # hiển thị thời gian hiện tại
        self.lbl_status.setText(self.lbl_status.text().split(" | ")[
                                0])  # giữ nguyên status chính

    def _position_slider_pressed(self):
        self._seeking = True

    def _position_slider_released(self):
        self.player.setPosition(self.sld_position.value())
        self._seeking = False

    def _position_slider_moved(self, v: int):
        pass  # có thể hiển thị mm:ss nếu bạn muốn

    def _on_playback_state_changed(self, state):
        self.btn_player_play.setText(
            "⏸" if state == QMediaPlayer.PlayingState else "⏵")


# ========================= Key Manager (dưới tabs) =========================
class KeyManagerWidget(QGroupBox):
    def __init__(self, bus: AppBus, title="Quản lý API Keys", store_path: Path | None = None):
        super().__init__(title)
        self.bus = bus
        self.store_path = store_path or (Path.cwd() / "keys.json")
        lay = QFormLayout(self)
        self.edt_openai = QLineEdit()
        self.edt_openai.setEchoMode(QLineEdit.Password)
        self.edt_azure = QLineEdit()
        self.edt_azure.setEchoMode(QLineEdit.Password)
        self.btn_save = QPushButton("💾 Lưu")
        lay.addRow("OpenAI Key:", self.edt_openai)
        lay.addRow("Azure Key:", self.edt_azure)
        lay.addRow("", self.btn_save)
        self.btn_save.clicked.connect(self.save_keys)
        self.load_keys()

    def load_keys(self):
        if self.store_path.exists():
            try:
                data = json.load(open(self.store_path, "r", encoding="utf-8"))
                self.edt_openai.setText(data.get("openai", ""))
                self.edt_azure.setText(data.get("azure", ""))
                self.bus.append_output.emit("Đã nạp keys.")
            except Exception as e:
                self.bus.append_output.emit(f"Lỗi đọc keys: {e}")

    def save_keys(self):
        try:
            self.store_path.write_text(json.dumps({
                "openai": self.edt_openai.text().strip(),
                "azure": self.edt_azure.text().strip()
            }, ensure_ascii=False, indent=2), encoding="utf-8")
            self.bus.append_output.emit(f"Đã lưu keys → {self.store_path}")
            QMessageBox.information(self, "Thành công", "Đã lưu keys.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
            self.bus.append_output.emit("Lỗi lưu keys: " + str(e))


# ========================= Main Window (menu + tabs trái, HistoryPanel phải) =========================
class MainWindow():
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edge TTS · HistoryPanel (300px)")

        # ----- Menu -----
        # m_file = self.menuBar().addMenu("&File")
        # m_file.addAction("Thoát", self.close)
        # m_help = self.menuBar().addMenu("&Help")
        # m_help.addAction("About", lambda: QMessageBox.information(
        #     self, "About", "Demo TTS với HistoryPanel."))

        # ----- Bus -----
        self.bus = AppBus()
        self.bus.append_output.connect(self._append_output)
        self.bus.set_progress.connect(self._set_progress)
        self.bus.add_history_path.connect(self._on_new_history_item)
        self.bus.toggle_history.connect(self._toggle_history_pane)

        # ----- Splitter trái/phải -----
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        # == Trái: Tab TTS + Key + Output + Progress (chung)
        left = QWidget()
        left_layout = QVBoxLayout(left)

        self.tabs = QTabWidget()
        self.tab_tts = TTSTab(self.bus)
        self.tabs.addTab(self.tab_tts, "TTS")
        dummy = QWidget()
        dummy.setLayout(QVBoxLayout())
        dummy.layout().addWidget(QLabel("Tab khác…"))
        self.tabs.addTab(dummy, "Khác")
        left_layout.addWidget(self.tabs)

        self.key_mgr = KeyManagerWidget(self.bus)
        left_layout.addWidget(self.key_mgr)

        self.output_list = QListWidget()
        left_layout.addWidget(self.output_list)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.hide()  # ✅ ẩn mặc định
        left_layout.addWidget(self.progress)

        splitter.addWidget(left)

        # == Phải: HistoryPanel (rộng cố định 300 – đúng yêu cầu)
        # Ẩn mặc định, khi bus.toggle_history(True) thì show
        self.history = HistoryPanel(
            close_callback=lambda: self._toggle_history_pane(False),
            parent=self
        )
        splitter.addWidget(self.history)
        self.history.hide()  # ✅ ẩn khởi động

        self.la.addWidget(self.history_panel)

        # Kích thước chia cột
        splitter.setSizes([800, 300])

        try:
            _init_addStyle(self)
        except Exception:
            pass

    def show_history_panel(self):
        print("show_history_panel")
        self.main_ui.setDisabled(True)
    # ===== Handlers Bus =====

    def _append_output(self, text: str):
        """Thêm log vào output list"""
        self.output_list.addItem(text)
        self.output_list.scrollToBottom()

    def _set_progress(self, val: int):
        """
        Điều khiển progress dùng chung:
        - Hiện khi 0 < val < 100
        - Ẩn khi hoàn thành (>=100) hoặc reset (<=0)
        """
        val = max(0, min(100, val))
        if 0 < val < 100:
            if not self.progress.isVisible():
                self.progress.show()
        self.progress.setValue(val)
        if val >= 100 or val <= 0:
            # đợi 250ms cho người dùng thấy 100%
            QTimer.singleShot(250, self.progress.hide)

    def _on_new_history_item(self, path_str: str):
        """Thêm item mới vào panel lịch sử (nếu đang mở thì thấy ngay)"""
        self.history.add_item_top(Path(path_str))

    def _toggle_history_pane(self, show: bool):
        """Bật/tắt HistoryPanel theo signal từ tab TTS"""
        self.history.setVisible(show)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(400, 720)
    win.show()
    sys.exit(app.exec())
