import sys
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow

# Run
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # window.hide()  # Ẩn cửa sổ chính ban đầu
    sys.exit(app.exec())
# This will start the application and show the main window.
