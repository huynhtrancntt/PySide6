import requests
from PySide6.QtCore import QThread, Signal

from ui_setting import UPDATE_CHECK_URL, APP_VERSION


class UI_CheckUpdate(QThread,):
    """Kiểm tra cập nhật ứng dụng"""
    """Worker thread để kiểm tra update"""

    update_available = Signal(dict)
    no_update = Signal()
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        """Kiểm tra phiên bản mới"""
        try:
            # Gửi request để lấy thông tin release mới nhất
            response = requests.get(UPDATE_CHECK_URL, timeout=10)

            if response.status_code == 200:
                # print("✅ Kết nối thành công đến server")
                release_data = response.json()
                latest_version = release_data.get(
                    'tag_name', '').replace('v', '')
                release_name = release_data.get('name', '')
                release_notes = release_data.get('body', '')
                # Lấy download URL từ JSON response
                download_url = release_data.get('download_url', '')
                if not download_url:
                    # Fallback nếu không có download_url, có thể thử các key khác
                    download_url = release_data.get('html_url', '')
                    if not download_url:
                        download_url = release_data.get('zipball_url', '')

                # Kiểm tra tính hợp lệ của download URL
                if not download_url or not download_url.startswith(('http://', 'https://')):
                    self.error_occurred.emit(
                        "Không tìm thấy URL download hợp lệ trong response")
                    return

                published_at = release_data.get('published_at', '')
                # So sánh phiên bản
                if self._is_newer_version(latest_version, APP_VERSION):
                    update_info = {
                        'version': latest_version,
                        # 'version': 'v2.0.1',  # Placeholder for actual version
                        'name': release_name,
                        'notes': release_notes,
                        'download_url': download_url,
                        'published_at': published_at
                    }
                    self.update_available.emit(update_info)
                else:
                    self.no_update.emit()
            else:
                self.error_occurred.emit(
                    f"HTTP {response.status_code}: Không thể kết nối đến server")

        except requests.exceptions.Timeout:
            self.error_occurred.emit(
                "Timeout: Không thể kết nối đến server trong thời gian quy định")
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit("Lỗi kết nối: Kiểm tra kết nối internet")
        except Exception as e:
            self.error_occurred.emit(f"Lỗi không xác định: {str(e)}")

    def _is_newer_version(self, latest, current):
        """So sánh 2 phiên bản"""
        try:
            # Chuyển đổi version string thành list số
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]

            # Đảm bảo cả 2 list có cùng độ dài
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))

            # So sánh từng phần
            for i in range(max_len):
                if latest_parts[i] > current_parts[i]:
                    return True
                elif latest_parts[i] < current_parts[i]:
                    return False

            return False  # Bằng nhau
        except:
            return False
