# asciiv

**asciiv** is a lightweight, cross-platform command-line interface (CLI) tool that plays video files directly in your terminal using ASCII art. It comes as a standalone binary with all dependencies packaged, featuring audio synchronization and playback controls.

## Features

- **ASCII Rendering**: Converts video frames to ASCII characters in real-time.
- **Audio Support**: Synchronized audio playback.
- **Customization**:
  - Adjustable video scaling to fit different terminal sizes.
  - Variable playback speed (slow motion or fast forward).
  - Volume control.
  - Custom ASCII character sets for rendering.
- **Looping**: Option to loop video playback continuously.
- **Cross-Platform**: Designed to work on Windows, macOS, and Linux.

## Built With

While **asciiv** requires no external dependencies to run, it is built using these powerful open-source technologies:

- **FFmpeg**: High-performance audio processing.
- **OpenCV**: Video frame extraction.
- **Pygame**: Audio playback.
- **Typer**: CLI interface.

## Installation

1. **Download**: Get the latest release for your operating system.
2. **Run**: Open your terminal and navigate to the folder containing the binary.

   *Optional*: Add the folder to your system's PATH to run `asciiv` from anywhere.

## Usage

Run the tool from the command line.

### Basic Syntax

```bash
asciiv [VIDEO_PATH] [OPTIONS]
```

### Arguments

- `VIDEO_PATH`: (Required) The path to the video file you want to play.

### Options

| Option | Default | Description |
| :--- | :--- | :--- |
| `--scale FLOAT` | `1.0` | Scale factor for the video size relative to terminal width. |
| `--speed FLOAT` | `1.0` | Playback speed multiplier (e.g., `2.0` for 2x, `0.5` for half speed). |
| `--volume FLOAT` | `1.0` | Audio volume level between `0.0` (mute) and `1.0` (max). |
| `--loop` | `False` | Enable to play the video continuously in a loop. |
| `--charset TEXT` | `" ░▒▓█"` | String of characters to use for ASCII rendering (ordered from dark to light). |
| `--disable-audio` | `False` | Disable audio playback entirely. |
| `--help` | | Show the help message and exit. |

## Examples

**1. Play a video with default settings:**
```bash
asciiv video.mp4
```

**2. Play at 50% size and loop continuously:**
```bash
asciiv video.mp4 --scale 0.5 --loop
```

**3. Play at 2x speed with volume set to 50%:**
```bash
asciiv video.mp4 --speed 2.0 --volume 0.5
```

**4. Use a custom character set for rendering:**
```bash
asciiv video.mp4 --charset " .:-=+*#%@"
```

## Controls

- **Stop Playback**: Press `Ctrl+C` to exit the player safely.

## Troubleshooting

- **"Error: FFmpeg not installed"**: Ensure FFmpeg is installed and added to your system PATH, or place the executable in a `bin/` folder within the project directory.
- **Flickering**: The tool uses ANSI escape codes to reset the cursor. Ensure your terminal emulator supports standard ANSI codes.