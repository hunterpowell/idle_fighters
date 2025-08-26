# Bouncing Images Screensaver

A fun screensaver that bounces images around your screen with collision detection and scoring.

## Quick Start

1. **Download the executable** from the releases page, or run the Python script directly
2. **Add your images**:
   - Run the program once and it will create an `images` folder in the same directory
   - Add image files (.png, .jpg, .jpeg, .gif, .bmp)
   - Images are automatically resized to 240x240
3. **Add sound** (optional):
   - replace `taco_baco.mp3` in the same directory for corner hit sounds

## Usage

Run the executable or: `python fighters.py`

- Press **Escape** to exit
- Two images bounce around the screen
- Score 5 points for corner hits, 1 point for winning collisions
- Runs fullscreen with transparent background

## File Structure
```
your-directory/
├── fighters.py
└── images/
    ├── image1.png
    └── image2.jpg
```

## Building Executable

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole fighters.py
```
