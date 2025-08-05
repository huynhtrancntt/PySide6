from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QMessageBox, QLineEdit, QListWidget, QProgressBar, QSizePolicy
)
from PySide6.QtGui import QFont
import sys
import requests


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thông báo cập nhật")

        # Thiết lập kích thước tối thiểu
        self.setMinimumSize(500, 200)
        self.setStyleSheet("background-color: #1a202c; color: #e2e8f0;")
        self._Ui()
        # main_layout = QVBoxLayout(self)
        # # Phiên bản
        # version_label = QLabel("Cập nhật phiên bản mới 1.1.2")
        # version_label.setFont(QFont("Arial", 14, QFont.Bold))
        # version_label.setStyleSheet("color: #00FF99")
        # main_layout.addWidget(version_label)
        # # Nhập dòng
        # label = QLabel("Some text : ")
        # line_edit = QLineEdit()
        # line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # h_layout_1 = QHBoxLayout()
        # h_layout_1.addWidget(label)
        # h_layout_1.addWidget(line_edit)
        # main_layout.addLayout(h_layout_1)

        # # Nút ngang
        # h_layout_2 = QHBoxLayout()
        # h_layout_2.addWidget(QPushButton("One"))
        # h_layout_2.addWidget(QPushButton("Two"))
        # h_layout_2.addWidget(QPushButton("Three"))
        # main_layout.addLayout(h_layout_2)

        # # Nhập URL
        # url_layout = QHBoxLayout()
        # url_label = QLabel("📋 Nhập URL video:")
        # url_label.setFixedWidth(150)
        # self.url_input = QLineEdit()
        # self.url_input.setPlaceholderText("https://example.com/video-url")
        # url_layout.addWidget(url_label)
        # url_layout.addWidget(self.url_input)
        # main_layout.addLayout(url_layout)

        # release_label = QLabel("Ngày phát hành: 15/03/2025")
        # release_label.setStyleSheet("color: #FFFFFF")
        # main_layout.addWidget(release_label)
        # button_popup = QPushButton("🔔 Thông báo cập nhật")
        # button_popup.setStyleSheet("color: #FFCC00; background-color: #333333")
        # button_popup.setFont(QFont("Arial", 12, QFont.Bold))
        # button_popup.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # button_popup.clicked.connect(self.start_progress)
        # main_layout.addWidget(button_popup)
        # # Thông báo cập nhật
        # update_label = QLabel(
        #     "🔔 Phần mềm chuyển văn bản thành giọng nói miễn phí. Phần mềm chuyển giọng nói thành văn bản. <a style='color: #00FF99' href='https://store.j2team.org'>Xem chi tiết</a>")
        # update_label.setStyleSheet("color: #FFCC00; font-weight: bold ")
        # update_label.setAlignment(Qt.AlignCenter)
        # update_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # update_label.setWordWrap(True)
        # update_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        # update_label.setFont(QFont("Arial", 12, QFont.Bold))
        # update_label.setOpenExternalLinks(True)
        # # update_label.setTextFormat(Qt.RichText)
        # main_layout.addWidget(update_label)
        # # Mô tả cập nhật
        # description_label = QLabel(
        #     "📖 Mô tả cập nhật: Bản cập nhật này bao gồm các tính năng mới và cải tiến hiệu suất.")
        # description_label.setStyleSheet("color: #FFFFFF")
        # description_label.setFont(QFont("Arial", 10))
        # main_layout.addWidget(description_label)

        # # Tính năng mới
        # features = [
        #     "Tính năng Pro: OpenAI TTS (BYOK)",
        #     "Cải thiện trạng Pro",
        #     "Một số tối ưu và tính chỉnh khác"
        # ]
        # for feature in features:
        #     label = QLabel("• " + feature)
        #     label.setStyleSheet("color: #66FFCC")
        #     main_layout.addWidget(label)

        # # Nút điều khiển
        # button_layout = QHBoxLayout()
        # install_button = QPushButton("⬇️ Tải về và cài đặt")
        # skip_button = QPushButton("❌ Bỏ qua")
        # install_button.clicked.connect(self.install_clicked)
        # skip_button.clicked.connect(self.skip_clicked)
        # button_layout.addWidget(install_button)
        # button_layout.addWidget(skip_button)
        # main_layout.addLayout(button_layout)

        # # Nút bắt đầu cập nhật
        # self.button_start = QPushButton("▶ Bắt đầu cập nhật")
        # self.button_start.clicked.connect(self.start_progress)
        # main_layout.addWidget(self.button_start)

        # # Label cảnh báo
        # warning_label = QLabel(
        #     "⚠️ Tải từ nguồn chính thức: https://store.j2team.org")
        # warning_label.setStyleSheet(
        #     "color: yellow; background-color: #333333; padding: 5px;")
        # main_layout.addWidget(warning_label)

        # # Progress bar
        # self.progress_bar = QProgressBar()
        # self.progress_bar.setRange(0, 100)
        # self.progress_bar.setValue(0)
        # self.progress_bar.setVisible(False)
        # self.progress_bar.setFormat("Đang tải cập nhật... %p%")

        # main_layout.addWidget(self.progress_bar)

        # # Danh sách kết quả
        # self.output_list = QListWidget()
        # self.output_list.setMinimumHeight(150)
        # self.output_list.setWordWrap(True)
        # self.output_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.output_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # main_layout.addWidget(self.output_list)

        # Style toàn bộ
        self.setStyleSheet("""
            QListWidget {
                background-color: #2d3748;
                color: #e2e8f0;
                border: 2px solid #4a5568;
                border-radius: 6px;
                font-family: Consolas;
                font-size: 12px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid #4a5568;
            }
            QListWidget::item:hover {
                background-color: #4a5568;
            }
            QListWidget::item:selected {
                background-color: #4299e1;
                color: white;
            }
                           
                           QProgressBar {
                border: 2px solid #4299e1;
                border-radius: 6px;
                text-align: center;
                height: 20px;
                background-color: #fff;
                color: #495057;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4299e1;
                border-radius: 4px;
            }
                           
        """)

    def _Ui(self):
        # self.setWindowTitle("Thông báo cập nhật")
        # self.setMinimumSize(500, 500)

        main_layout = QVBoxLayout(self)
        # Phiên bản
        version_label = QLabel("Cập nhật phiên bản mới 1.1.2")
        version_label.setFont(QFont("Arial", 14, QFont.Bold))
        version_label.setStyleSheet("color: #00FF99")
        main_layout.addWidget(version_label)
        # Nhập dòng
        label = QLabel("Some text : ")
        line_edit = QLineEdit()
        line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_popup = QPushButton("🔔 Update")
        btn_popup.setStyleSheet(
            "width: 100px; color: #FFCC00; background-color: #00FF99")
        btn_popup.setFont(QFont("Arial", 12, QFont.Bold))
        h_layout_1 = QHBoxLayout()
        h_layout_1.addWidget(label)
        h_layout_1.addWidget(line_edit)
        h_layout_1.addWidget(btn_popup)
        main_layout.addLayout(h_layout_1)

        # Nút ngang
        self.output_list = QListWidget()
        self.output_list.setMinimumHeight(150)
        self.output_list.setWordWrap(True)
        self.output_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.output_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_layout.addWidget(self.output_list)

    def install_clicked(self):
        self.output_list.addItem(
            "🔗 URL đã được xử lý: https://example.com/video")
        url = self.url_input.text()
        if url:
            QMessageBox.information(self, "Cài đặt", f"Đang xử lý URL: {url}")
        else:
            QMessageBox.warning(self, "Thiếu URL", "Vui lòng nhập URL video!")

    def skip_clicked(self):
        self.output_list.clear()
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "Bỏ qua", "Đã bỏ qua cập nhật.")

    def start_progress(self):
        self.output_list.addItem("🔄 Đang tải xuống bản cập nhật...")
        file_id = "1UYD05VutTzExD8BRsLu44zRJbjiCnXEr"
        output = "file_dung.zip"
        self.download_with_progress(file_id, output)

    def download_with_progress(self, file_id, output_path):
        self.output_list.addItem("🔄 Bắt đầu tải xuống...")

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        return
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                chunk_size = 8192
                downloaded = 0

                with open(output_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            percent = int(downloaded * 100 / total_size)
                            self.progress_bar.setValue(percent)
                            self.output_list.addItem(
                                f"📦 Đang tải: {percent}% ({downloaded}/{total_size} bytes)")
                            QApplication.processEvents()

            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("✅ Tải hoàn tất!")
            self.output_list.addItem(f"✅ Đã tải xong: {output_path}")
        except Exception as e:
            self.output_list.addItem(f"❌ Lỗi khi tải: {str(e)}")


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec())
