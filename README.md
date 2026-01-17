# AFK Journey Automation

## Overview
AFK Journey Automation is a Python project designed to automate various tasks in the game AFK Journey. This project uses **advanced scale-invariant feature matching** to work reliably across different screen resolutions, DPI settings, and display configurations.

## Features
- **Auto Fight** - Automated AFK challenge battles
- **Auto P Fight** - Automated Phatimal challenge battles
- **Auto Fight Friends** - Automated friend challenge battles
- **Auto P Fight Friends** - Automated friend Phatimal challenge battles
- **Faction Challenge** - Automated faction challenge battles
- **Multi-Monitor Support** - Automatically detects and handles multiple monitors
- **Debug Mode** - Visual debugging to see exactly what's being detected

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/afk-journey-automation.git
   cd afk-journey-automation
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Make sure AFK Journey is running on your screen.

2. Run the application:
   ```bash
   python src/main.py
   ```
   
   **Enable debug mode** for detailed matching logs:
   ```bash
   python src/main.py --debug
   ```
   
   Or with the compiled executable:
   ```cmd
   AFK-Journey-Automation.exe --debug
   ```

3. Select your language (EN/CN) from the dropdown.

4. Click on the desired automation function to start. To start the automation, you must enter the battle page first.

5. Click "Stop Automation" to stop the running automation.

**Note**: For detailed debug mode documentation, see [DEBUG_MODE.md](DEBUG_MODE.md).

## Multi-Resolution & DPI Support

This automation uses **SIFT (Scale-Invariant Feature Transform)** and **AKAZE** feature matching to work reliably across:

- ✅ Different screen resolutions (1080p, 1440p, 4K, etc.)
- ✅ Windows DPI scaling (100%, 125%, 150%, 200%, etc.)
- ✅ Windowed or fullscreen game modes
- ✅ Multiple monitors with different DPIs
- ✅ Extreme UI stretching or aspect ratio changes

### How Feature Matching Works

Instead of looking for exact pixel matches, the system:

1. **Detects distinctive features** in both the template and screenshot (corners, edges, patterns)
2. **Matches features** using sophisticated algorithms (SIFT/AKAZE)
3. **Validates matches** using geometric consistency (homography + RANSAC)
4. **Adapts to scale** - automatically handles any size difference

### Adaptive Validation

The system uses a **sliding scale for validation** to prevent false positives:

| Match Count | Inlier Ratio Required | Purpose |
|-------------|----------------------|---------|
| 10-14 matches | **70%** | Strict - prevents false positives with few matches |
| 15-19 matches | **65%** | Medium - balanced confidence |
| 20+ matches | **60%** | Standard - sufficient statistical confidence |

This ensures reliable detection while supporting extreme DPI scaling and UI stretching.

## Testing & Debugging

### Visual Debugger (Recommended)

The visual debugger is the best way to verify matching works on your system:

```bash
python debug_visual_matching.py
```

**What it does:**
- Takes a screenshot of your game
- Tests matching for all UI elements
- Shows detailed statistics (match count, inlier ratio, scale factors)
- **Saves annotated images** showing exactly what was detected
- Creates `debug_output/` folder with visual results

**Output includes:**
- Feature matches visualization with connecting lines
- Bounding boxes showing detected regions
- Validation results (PASSED/FAILED with reasons)
- Scale and aspect ratio information

**Check the output:**
```
debug_output/
├── original_screenshot.png       # Your game screen
├── EN_fight_sift_detected.png    # Detected location
├── EN_fight_sift_matches.png     # Feature match visualization
└── ... (more for each template)
```

### Understanding Debug Output

```
Testing EN/fight.png...
  Template size: (120, 240)
  ✓ SIFT - Template features: 150, Screenshot features: 5000
  ✓ Best ratio: 0.245, Avg: 0.712
  ✓ SIFT good matches: 35
  ✓ Inliers: 33/35 (94.3%)
  ℹ Scale: 1.25x (width), 1.25x (height)
  ℹ Aspect ratio change: 1.00x
  ✓ Match validation: PASSED (94.3% ≥ 60% for 20+ matches)
```

- **Good matches**: Features that passed Lowe's ratio test (< 0.65)
- **Inliers**: Matches that fit the geometric transformation
- **Scale**: Size difference between template and detected region (informational only)
- **Validation**: Whether the match is accepted (based on inlier ratio)

## Troubleshooting

### Automation Not Clicking Correctly

1. **Run the debug script first**: `python debug_visual_matching.py`
2. Check `debug_output/` folder for visual results
3. If validation shows "FAILED", the UI element wasn't detected
4. If validation shows "PASSED" but coordinates seem wrong, check your monitor setup

### Enable Debug Logs

For real-time debugging during automation:

```bash
python src/main.py --debug
```

This shows detailed logs for every template match attempt, including:
- Template sizes and pixel counts
- Adaptive thresholds being used
- Keypoint detection results
- Match counts and inlier ratios
- Click coordinate calculations
- Monitor offset adjustments

See [DEBUG_MODE.md](DEBUG_MODE.md) for complete debug mode documentation.

### Multi-Monitor Issues

The tool automatically detects your monitor setup. If clicks are going to the wrong screen:

1. Make sure the game is on your primary monitor, OR
2. Check the monitor detection in the debug output

### False Positives or Missed Detections

The adaptive validation system should handle most cases. If you're getting:

- **False positives**: The image has too few distinct features - try using a different template region
- **Missed detections**: The template might be from a different language/version - check `assets/EN/` or `assets/CN/`

## Building from Source

To build a standalone executable:

```bash
# Install build dependencies
pip install pyinstaller

# Run build script
build.bat

# Output will be in dist/AFK-Journey-Automation.exe
```

For detailed build and release instructions, see [RELEASE.md](RELEASE.md).

## Project Structure

```
afk-journey-automation/
├── src/
│   ├── main.py                     # Entry point with GUI
│   └── automation/
│       ├── screenshot.py           # Multi-monitor screenshot handling
│       ├── image_matching.py       # SIFT/AKAZE feature matching
│       ├── click_simulation.py     # Click with monitor offset handling
│       └── game_automation.py      # Game-specific automation logic
├── assets/
│   ├── EN/                         # English UI templates
│   └── CN/                         # Chinese UI templates
├── debug_visual_matching.py        # Visual debugging tool
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Requirements

- Python 3.8+
- Windows OS
- AFK Journey game client
- opencv-python, numpy, pywin32, mss (see requirements.txt)

## Author

Authored by ylx

## License

This project is licensed under the MIT License.
