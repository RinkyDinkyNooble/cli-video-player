# asciiv

**asciiv** is a lightweight, command-line interface (CLI) tool that plays video files directly in your terminal using ASCII art.

## Features

- **ASCII Rendering**: Converts video frames to ASCII characters.
- **Audio Support**: Synchronized audio playback with automatic speed adjustment.
- **Customization**:
  - Adjustable video scaling to fit different terminal sizes.
  - Variable playback speed (slow motion or fast forward).
  - Volume control.
  - Custom ASCII character sets for rendering.
- **Looping**: Option to loop video playback continuously.

## Showcase

```bash
asciiv video.mp4
```
![Showcase 1](showcase/showcase1.gif)

```bash
asciiv video.mp4 --charset=" ░▒▓█"
```
![Showcase 2](showcase/showcase2.gif)

Zoomed out with ctrl and minus:
```bash
asciiv video.mp4
```
![Showcase 3](showcase/showcase3.gif)

## Built With
Python 3.12.10
- **FFmpeg**: High-performance audio processing.
- **OpenCV**: Video frame extraction.
- **Pygame**: Audio playback.
- **Typer**: CLI interface.

## Installation

### Windows 10 & 11

1. **Download**: Get the latest release (asciiv-windows.zip)
2. **Extract**: Unzip the downloaded file to your desired location
3. **Run**: Open your terminal in the extracted folder or navigate to that directory
4. **Execute**: 
```bash
.\asciiv.exe --help
   ```

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
| `--charset TEXT` | `" .:-=+*#%@"` | String of characters to use for ASCII rendering (ordered from dark to light). |
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
asciiv video.mp4 --charset " ░▒▓█"
```

## Controls

- **Stop Playback**: Press `Ctrl+C` to exit the player safely.

## Tips

- **Zooming**: Some terminals can 'zoom in and out' using `Ctrl`+`+`/`-`. Zooming out may improve quality at the cost of performance.

## Troubleshooting

- **"Error: FFmpeg not installed"**: Ensure FFmpeg is installed and added to your system PATH, or place the executable in a `bin/` folder within the project directory.
- **Flickering**: The tool uses ANSI escape codes to reset the cursor. Ensure your terminal emulator supports standard ANSI codes.

## License

This project is released under the **CC0 1.0 Universal (Public Domain)** license. See [LICENSE.txt](LICENSE.txt) for details.

### Third-Party Dependencies

This project includes the following third-party libraries, each with their own licenses:

| Package | License | Link |
|---------|---------|------|
| opencv-python | Apache 2.0 | https://github.com/opencv/opencv-python |
| pygame | LGPL | https://www.pygame.org |
| typer | MIT | https://github.com/fastapi/typer |

## FFmpeg Notice

This release bundles FFmpeg binaries, distributed under the LGPL license (see LICENSES/LGPL.txt).

### Using Alternative FFmpeg Builds

You may compile and use your own FFmpeg version:
1. Download or compile FFmpeg from https://github.com/FFmpeg/FFmpeg
2. Place the FFmpeg executable in the `bin/` folder (or update PATH)
3. asciiv will use your version instead

### FFmpeg Source Code

FFmpeg source code is available at: https://github.com/FFmpeg/FFmpeg