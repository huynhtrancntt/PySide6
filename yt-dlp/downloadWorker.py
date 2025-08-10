from PySide6.QtCore import QThread, Signal, QTime

import sys
import os
import re
import subprocess
from ui_setting import resource_path


class DownloadVideo(QThread):
    message_signal = Signal(str, str)
    progress_signal = Signal(int)
    finished_signal = Signal()
    stop_flag = False

    def __init__(self, url, video_index,
                 total_urls, worker_id,
                 video_mode, audio_only,
                 sub_mode, sub_lang, sub_lang_name, include_thumb,
                 subtitle_only, custom_folder_name=""):
        super().__init__()
        self.url = url
        self.video_index = video_index
        self.total_urls = total_urls
        self.worker_id = worker_id
        self.video_mode = video_mode
        self.audio_only = audio_only
        self.sub_mode = sub_mode
        self.sub_lang = sub_lang
        self.sub_lang_name = sub_lang_name
        self.include_thumb = include_thumb
        self.subtitle_only = subtitle_only
        self.custom_folder_name = custom_folder_name
        self.ffmpeg_path = resource_path(os.path.join("data", "ffmpeg.exe"))
        self.ytdlp_path = resource_path(os.path.join("data", "yt-dlp.exe"))
        self.stop_flag = False
        # print(self.url)
        # print(f" video_mode {self.video_mode}")
        # print(f" audio_only {self.audio_only}")
        # print(f" sub_mode {self.sub_mode}")
        # print(f" sub_lang {self.sub_lang}")
        # print(f" sub_lang_name {self.sub_lang_name}")
        # print(f" subtitle_only {self.subtitle_only}")
        # print(f" custom_folder_name {self.custom_folder_name}")

    def run(self):

        message_thread = f"[Thread {self.worker_id}] ({self.video_index}/{self.total_urls}) "
        if self.stop_flag:
            self.message_signal.emit(
                f"{message_thread} ⏹ Đã dừng trước khi bắt đầu.", "")
            self.finished_signal.emit()
            return

        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NO_WINDOW

        self.message_signal.emit(
            f"{message_thread} 🔽 Bắt đầu tải: {self.url}", ""
        )

        # Lấy tiêu đề video
        ytdlp_path = "yt-dlp"

        if os.path.exists(self.ytdlp_path):
            ytdlp_path = self.ytdlp_path

        get_title_cmd = [ytdlp_path, "--encoding",
                         "utf-8", "--get-title", self.url]
        result = subprocess.run(get_title_cmd, capture_output=True,

                                text=True, encoding="utf-8", creationflags=creation_flags)

        title = result.stdout.strip().replace("/", "-").replace("\\", "-")

        self.message_signal.emit(
            f"{message_thread} 🎯 Tiêu đề: {title}", "")

        output_filename = f"{self.video_index:02d}.{title}.%(ext)s"

        output_filename = os.path.join(
            self.custom_folder_name, output_filename)

        download_cmd = [
            ytdlp_path, "--encoding", "utf-8", self.url,
            "--newline",
            "--progress", "--write-auto-sub", "--sub-langs", "vi",
            "--sub-format", "srt/best", "--convert-subs", "srt",
            "-f", "bv*+ba/b", "--merge-output-format", "mp4",
            "--output", output_filename, "--extract-audio",
            "--audio-format", "mp3", "--write-thumbnail",
            "--ignore-errors", "--no-warnings"
        ]

        self.process = subprocess.Popen(
            download_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=creation_flags
        )

        for line in self.process.stdout:
            if self.stop_flag:
                self.process.kill()
                self.process.terminate()
                self.message_signal.emit(
                    f"{message_thread} ⏹ Đã dừng tải video.", "")
                self.finished_signal.emit()
                return

            if line.strip():

                self.message_signal.emit(
                    f"{message_thread} {line.strip()}", "")
                match = re.search(r"\[download\]\s+(\d{1,3}\.\d{1,2})%", line)
                if match:
                    percent = float(match.group(1))
                    self.progress_signal.emit(int(percent))

        self.process.wait()

        self.progress_signal.emit(95)
        video_filename = f"{self.video_index:02d}_{title}.mp4"
        self.message_signal.emit(
            f"{message_thread} ✅ Xong: {video_filename}", "")
        self.finished_signal.emit()

    # def _update_progress_from_line(self, line):
    #     """Cập nhật progress từ output line"""
    #     if "%" in line:
    #         try:
    #             percent_str = line.split(
    #                 "%", 1)[0].split()[-1].replace(".", "").strip()
    #             percent = int(percent_str)
    #             if 0 <= percent <= 100:
    #                 self.progress_signal.emit(percent)
    #         except:
    #             pass
