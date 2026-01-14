"""Click simulation utilities for automated game interaction."""

import os
import random

import cv2
import numpy as np
from pywinauto import mouse, Application
from screeninfo import get_monitors

from .screenshot import screenshot_monitor
from .image_matching import findMatchings

# Global variable for language/asset path
_current_language = "EN"
_assets_base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")

def set_language(lang: str):
    """Set the current language for asset loading (EN or CN)"""
    global _current_language
    if lang in ["EN", "CN"]:
        _current_language = lang
    else:
        raise ValueError(f"Invalid language: {lang}. Must be 'EN' or 'CN'")

def get_language() -> str:
    """Get the current language setting"""
    return _current_language

def get_asset_path(filename: str) -> str:
    """Get the full path to an asset file based on current language"""
    return os.path.join(_assets_base_path, _current_language, filename)

def get_game_window():
    """Get the game window object"""
    try:
        app = Application().connect(class_name="UnityWndClass", title="AFK Journey")
        return app.window(title="AFK Journey")
    except Exception as e:
        print(f"Could not find game window: {e}")
        return None

def get_game_monitor():
    """Detect which monitor the game window is on and return monitor number (1-indexed for mss)"""
    window = get_game_window()
    if window is None:
        return 1  # Default to monitor 1
    
    try:
        rect = window.rectangle()
        window_center_x = (rect.left + rect.right) // 2
        window_center_y = (rect.top + rect.bottom) // 2
        
        monitors = get_monitors()
        for i, monitor in enumerate(monitors):
            if (monitor.x <= window_center_x < monitor.x + monitor.width and
                monitor.y <= window_center_y < monitor.y + monitor.height):
                return i + 1  # mss uses 1-indexed monitors
        
        return 1  # Default to monitor 1 if not found
    except Exception as e:
        print(f"Error detecting monitor: {e}")
        return 1

def get_game_window_offset():
    """Get the game window's position offset for accurate clicking"""
    window = get_game_window()
    if window is None:
        # Fall back to first monitor position
        monitors = get_monitors()
        return monitors[0].x, monitors[0].y
    
    try:
        rect = window.rectangle()
        return rect.left, rect.top
    except Exception as e:
        print(f"Error getting window offset: {e}")
        monitors = get_monitors()
        return monitors[0].x, monitors[0].y

def click(x: int, y: int, focus: bool = True):
    if focus:
        window = get_game_window()
        if window:
            window.set_focus()

    mouse.move(coords=(x, y))
    mouse.click(button='left', coords=(x, y))

def simulateClickOnImage(main_image: np.ndarray, targetImage: str, min_x: int = -9999, min_y: int = -9999, focus: bool = True) -> bool:
    # Get the full asset path
    asset_path = get_asset_path(targetImage)
    
    template = cv2.imread(asset_path, 0)
    if template is None:
        print(f"Warning: Could not load template image: {asset_path}")
        return False
    
    w, h = template.shape[::-1]

    loc = findMatchings(main_image, template)
    deviation_range = 5
    if loc:
        index = 0
        while loc[index][0] < min_x or loc[index][1] < min_y:
            index += 1
            if index == len(loc):
                return False

        pt = loc[index]
        match_x, match_y = pt[0] + w // 2, pt[1] + h // 2

        deviation_x = random.randint(-deviation_range, deviation_range)
        deviation_y = random.randint(-deviation_range, deviation_range)

        match_x += deviation_x
        match_y += deviation_y

        # Get game window offset for accurate clicking
        screen_x, screen_y = get_game_window_offset()

        screen_x += match_x
        screen_y += match_y
        click(screen_x, screen_y, focus=focus)
        return True
    else:
        return False

def clickOnScreenShoot(targetImage: str, focus: bool = True) -> bool:
    """Take a screenshot of the game window's monitor and click on the target image if found"""
    monitor = get_game_monitor()
    screenShot = screenshot_monitor(monitor)
    if simulateClickOnImage(screenShot, targetImage, focus=focus):
        return True
    else:
        return False