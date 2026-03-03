import cv2
import time
import shutil
import sys
import signal
import os; os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
import typer
import subprocess # nosec b404
import tempfile
from types import FrameType
from typing import Optional

app = typer.Typer()

DEFAULT_ASCII_CHARS = " .:-=+*#%@"

playback_stopped = False

def handle_sigint(signal_number: int, frame: Optional[FrameType]) -> None:
    """
    Signal handler for SIGINT (Ctrl+C) that gracefully stops video playback.

    Sets the module-level ``playback_stopped`` flag, which the main playback
    loop checks on every iteration. This allows the loop to exit cleanly so
    that audio and temporary files can be properly cleaned up before the
    process terminates.

    :param signal_number: The signal number received (always ``signal.SIGINT``).
    :param frame: The current stack frame at the time the signal was delivered.
    """
    global playback_stopped
    playback_stopped = True

signal.signal(signal.SIGINT, handle_sigint)

def frame_to_ascii(video_frame, target_width: int, ascii_chars: str) -> str:
    """
    Convert a single BGR video frame into an ASCII art string.

    Resizes the frame to ``target_width`` columns (preserving aspect ratio with
    a 0.5 vertical correction to account for terminal character height), converts
    it to grayscale, then maps each pixel's brightness linearly onto a character
    from ``ascii_chars``. The first character of ``ascii_chars`` is treated as
    the background/dark character and is always rendered as a plain space so
    that unlit areas remain empty in the terminal.

    :param video_frame: A BGR image array as returned by ``cv2.VideoCapture.read()``.
    :param target_width: Desired output width in characters.
    :param ascii_chars: Ordered string of characters from darkest to brightest.
    :return: A multi-line string where each line represents one row of the frame.
    """
    target_height = int(video_frame.shape[0] * (target_width / video_frame.shape[1]) * 0.5)
    resized = cv2.resize(video_frame, (target_width, target_height))
    grayscale = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    n = len(ascii_chars)
    dark_char = ascii_chars[0]
    rows = [
        "".join(
            " " if (ch := ascii_chars[int(brightness) * n // 256]) == dark_char else ch
            for brightness in pixel_row
        )
        for pixel_row in grayscale
    ]
    return "\n".join(rows)

def move_cursor() -> None:
    """
    Move the terminal cursor to the home position (top-left corner).

    Uses the ANSI escape code ``\\033[H``. Writing the next frame from the
    home position overwrites the previous one in-place, avoiding a full
    screen clear and reducing flicker during playback.
    """
    sys.stdout.write("\033[H")
    sys.stdout.flush()

def clear_screen() -> None:
    """
    Clear the entire terminal screen using the ANSI erase-display escape code.

    Called once before playback begins and once after it ends to ensure the
    terminal is in a clean state.
    """
    sys.stdout.write("\033[2J")
    sys.stdout.flush()

def extract_audio(ffmpeg_executable: str, source_video_path: str, playback_speed: float) -> str:
    """
    Extract and speed-adjust the audio track from a video file using FFmpeg.

    Creates a temporary WAV file (44100 Hz, stereo, 16-bit PCM) and applies
    one or more chained ``atempo`` filters to match the requested playback speed.
    The ``atempo`` filter is constrained to the range [0.5, 2.0], so speeds
    outside that range are achieved by stacking multiple filters.

    :param ffmpeg_executable: Absolute path to the FFmpeg binary.
    :param source_video_path: Path to the source video file.
    :param playback_speed: Speed multiplier (e.g. ``2.0`` for double speed).
    :return: Absolute path to the temporary WAV file. The caller is responsible
             for deleting it when no longer needed.
    :raises subprocess.CalledProcessError: If FFmpeg exits with a non-zero status.
    """
    file_descriptor, audio_output_path = tempfile.mkstemp(suffix=".wav")
    os.close(file_descriptor)

    audio_filters: list[str] = []
    current_speed_factor = playback_speed
    while current_speed_factor > 2.0:
        audio_filters.append("atempo=2.0")
        current_speed_factor /= 2.0
    while current_speed_factor < 0.5:
        audio_filters.append("atempo=0.5")
        current_speed_factor *= 2.0
    audio_filters.append(f"atempo={current_speed_factor}")

    subprocess.run( # nosec b603
        [
            ffmpeg_executable,
            "-y",
            "-i", source_video_path,
            "-vn",
            "-filter:a", ",".join(audio_filters),
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "-ac", "2",
            audio_output_path,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    return audio_output_path

def resolve_ffmpeg() -> str:
    """
    Locate the FFmpeg executable required for audio extraction.

    Search order:
    1. A ``bin/`` subdirectory relative to this script (or the frozen executable
       directory when running as a PyInstaller bundle).
    2. The system ``PATH``, via ``shutil.which``.

    :return: Absolute path to the FFmpeg executable.
    :raises typer.Exit: Exits with code 1 if FFmpeg cannot be found.
    """
    executable_name = "ffmpeg.exe" if sys.platform.startswith("win") else "ffmpeg"

    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    local_bin_path = os.path.join(base_path, "bin", executable_name)
    if os.path.isfile(local_bin_path):
        return local_bin_path

    system_bin_path = shutil.which("ffmpeg")
    if system_bin_path:
        return system_bin_path

    print("Error: FFmpeg not found. Install it via your package manager or place it in the bin/ folder.")
    raise typer.Exit(1)

@app.command(epilog="Some terminals can 'zoom in and out' using Ctrl+Plus/Minus. Zooming out may improve quality at the cost of performance.")
def play(
    video: str = typer.Argument(..., help="The path to the video file you want to play."),
    scale: float = typer.Option(1.0, help="Scale factor for the video size relative to terminal width."),
    speed: float = typer.Option(1.0, help="Playback speed multiplier (e.g., 2.0 for 2x speed)."),
    volume: float = typer.Option(1.0, help="Audio volume level between 0.0 (mute) and 1.0 (max)."),
    loop: bool = typer.Option(False, help="Enable to play the video continuously in a loop."),
    charset: str = typer.Option(DEFAULT_ASCII_CHARS, help="String of characters to use for ASCII rendering."),
    disable_audio: bool = typer.Option(False, help="Disable audio playback entirely."),
) -> None:
    """
    Play a video file in the terminal using ASCII characters.

    Each video frame is resized to fit the terminal width, converted to
    grayscale, and rendered as ASCII art. Audio is extracted to a temporary
    WAV file via FFmpeg and played back in sync using pygame. Pass
    ``--disable-audio`` to skip audio entirely (no FFmpeg required in that case).
    Press Ctrl+C at any time to stop playback and clean up resources.
    """
    temporary_audio_path: Optional[str] = None

    if not disable_audio:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
        ffmpeg_exe = resolve_ffmpeg()
        temporary_audio_path = extract_audio(ffmpeg_exe, video, speed)
        pygame.mixer.music.load(temporary_audio_path)
        pygame.mixer.music.play()

    video_capture = cv2.VideoCapture(video)
    if not video_capture.isOpened():
        print("Error: Could not open video file.")
        raise typer.Exit(1)

    video_framerate = video_capture.get(cv2.CAP_PROP_FPS) or 24.0
    seconds_per_frame = (1.0 / video_framerate) / speed

    terminal_width, _ = shutil.get_terminal_size()
    ascii_width = max(10, int(terminal_width * scale))

    clear_screen()
    playback_start_time = time.perf_counter()
    current_frame_index = 0

    while not playback_stopped:
        read_successful, video_frame = video_capture.read()
        if not read_successful:
            if loop:
                video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                current_frame_index = 0
                if not disable_audio:
                    pygame.mixer.music.play()
                playback_start_time = time.perf_counter()
                continue
            break

        ascii_art_string = frame_to_ascii(video_frame, ascii_width, charset)
        move_cursor()
        sys.stdout.write(ascii_art_string)
        sys.stdout.flush()

        target_time = current_frame_index * seconds_per_frame
        elapsed_time = time.perf_counter() - playback_start_time
        sleep_duration = target_time - elapsed_time
        if sleep_duration > 0:
            time.sleep(sleep_duration)

        current_frame_index += 1

    video_capture.release()
    if not disable_audio:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    clear_screen()

    if temporary_audio_path and os.path.exists(temporary_audio_path):
        os.remove(temporary_audio_path)

if __name__ == "__main__":
    app()
