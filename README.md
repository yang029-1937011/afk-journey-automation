# AFK Journey Automation

## Overview
AFK Journey Automation is a Python project designed to automate various tasks in the game AFK Journey. This project utilizes image processing and GUI elements to provide an easy-to-use interface for executing automation functions.

## Features
- **Auto Fight** - Automatically battles through stages
- **Auto P Fight** - Automated battles with dual team confirmation
- **Auto Fight Friends** - Automated friend battles
- **Auto P Fight Friends** - Automated friend battles with dual team
- **Faction Challenge** - Automated faction challenge battles
- **Multi-language Support** - Supports EN and CN game clients
- **Auto Monitor Detection** - Automatically detects which monitor the game is on

## Project Structure
```
afk-journey-automation
├── src
│   ├── main.py                  # Entry point with GUI
│   ├── automation
│   │   ├── __init__.py          # Package initialization
│   │   ├── screenshot.py        # Functions for taking screenshots
│   │   ├── image_matching.py    # Functions for image processing and matching
│   │   ├── click_simulation.py  # Functions for simulating mouse clicks
│   │   └── game_automation.py   # Main automation functions for the game
│   └── utils
│       └── __init__.py          # Utility functions
├── assets
│   ├── EN/                      # English game assets
│   └── CN/                      # Chinese game assets
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation
```

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

3. Select your language (EN/CN) from the dropdown.

4. Click on the desired automation function to start.

5. Click "Stop Automation" to stop the running automation.

## Requirements
- Python 3.8+
- Windows OS
- AFK Journey game client

## Author
Authored by ylx

## License
This project is licensed under the MIT License.