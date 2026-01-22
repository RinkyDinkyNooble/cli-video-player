import cv2
import time
import shutil
import sys
import signal
import pygame
import typer
import subprocess
import tempfile
import os

app = typer.Typer()

DEFAULT_CHARSET = " ░▒▓█"

stop_flag = False
temp_audio_path = None

def handle_sigint(sig, frame):
    global stop_flag
    stop_flag = True

signal.signal(signal.SIGINT, handle_sigint)

def frame_to_ascii(frame, width, charset):
    height = int(frame.shape[0] * (width / frame.shape[1]) * 0.5)
    resized = cv2.resize(frame, (width, height))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    out = []
    clen = len(charset)
    for row in gray:
        line = []
        for pixel in row:
            idx = int(pixel) * clen // 256
            ch = charset[idx]
            line.append(ch if ch != charset[0] else " ")
        out.append("".join(line))
    return "\n".join(out)

def move_cursor():
    sys.stdout.write("\033[H")
    sys.stdout.flush()

def clear_screen():
    sys.stdout.write("\033[2J")
    sys.stdout.flush()

def extract_audio(ffmpeg_path, video_path, speed):
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    filters = []
    s = speed
    while s > 2.0:
        filters.append("atempo=2.0")
        s /= 2.0
    while s < 0.5:
        filters.append("atempo=0.5")
        s *= 2.0
    filters.append(f"atempo={s}")

    subprocess.run(
        [
            ffmpeg_path,
            "-y",
            "-i", video_path,
            "-vn",
            "-filter:a", ",".join(filters),
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "-ac", "2",
            path,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    return path

def resolve_ffmpeg():
    exe = "ffmpeg.exe" if sys.platform.startswith("win") else "ffmpeg"
    base = os.path.dirname(sys.argv[0])
    candidate = os.path.join(base, exe)
    return candidate if os.path.isfile(candidate) else exe

@app.command()
def play(
    video: str = typer.Argument(...),
    scale: float = typer.Option(1.0),
    speed: float = typer.Option(1.0),
    volume: float = typer.Option(1.0),
    loop: bool = typer.Option(False),
    charset: str = typer.Option(DEFAULT_CHARSET),
    disable_audio: bool = typer.Option(False),
):
    global temp_audio_path

    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))

    if not disable_audio:
        ffmpeg = resolve_ffmpeg()
        temp_audio_path = extract_audio(ffmpeg, video, speed)
        pygame.mixer.music.load(temp_audio_path)
        pygame.mixer.music.play()

    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        print("Error: Could not open video file.")
        raise typer.Exit(1)

    use_fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    frame_time = (1.0 / use_fps) / speed

    cols, _ = shutil.get_terminal_size()
    width = max(10, int(cols * scale))

    clear_screen()
    start = time.perf_counter()
    frame_idx = 0

    while not stop_flag:
        ret, frame = cap.read()
        if not ret:
            if loop:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                frame_idx = 0
                if not disable_audio:
                    pygame.mixer.music.play()
                start = time.perf_counter()
                continue
            break

        ascii_frame = frame_to_ascii(frame, width, charset)
        move_cursor()
        sys.stdout.write(ascii_frame)
        sys.stdout.flush()

        target = frame_idx * frame_time
        elapsed = time.perf_counter() - start
        delay = target - elapsed
        if delay > 0:
            time.sleep(delay)

        frame_idx += 1

    cap.release()
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    clear_screen()

    if temp_audio_path and os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)

if __name__ == "__main__":
    app()
