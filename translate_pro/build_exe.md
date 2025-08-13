pyinstaller --onefile --name=TTS_UI ^
--noconsole ^
--hidden-import=ui_setting ^
--hidden-import=edge_tts ^
--hidden-import=pygame ^
--hidden-import=PySide6 ^
tts_ui.py
