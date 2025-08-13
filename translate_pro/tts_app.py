import asyncio
import time
from pathlib import Path
import edge_tts


def try_pygame_play(path: Path) -> bool:
    try:
        import pygame
        import os
        os.environ.setdefault(
            "SDL_AUDIODRIVER", "directsound")  # ổn định Windows
        pygame.mixer.init()
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        return True
    except Exception as e:
        print("[pygame] lỗi:", e)
        return False


async def main():
    TEXT = "Xin chào! Đây là giọng nói tiếng Việt từ edge-tts."
    VOICE = "vi-VN-HoaiMyNeural"
    out = Path("out.mp3").resolve()

    # tạo file mp3 bằng edge-tts
    await edge_tts.Communicate(TEXT, VOICE).save(str(out))
    print("Đã lưu:", out)

    # phát bằng pygame
    if try_pygame_play(out):
        print("✅ Phát OK")
    else:
        print("❌ Không phát được")

if __name__ == "__main__":
    asyncio.run(main())

# pip install edge-tts
# pip install pygame
# pip install pyinstaller
# pyinstaller --onefile --name=tts_app --noconsole --hidden-import=pygame --hidden-import=edge_tts  tts_app.py

# pyinstaller --onefile --name=tts_app --noconsole ^
#   --hidden-import=pygame --hidden-import=edge_tts ^
#   --collect-all edge_tts ^
#   tts_app.py
