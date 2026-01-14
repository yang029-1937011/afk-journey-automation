"""Click simulation utilities for automated game interaction."""

import os
import sys
import random
from typing import Optional, Tuple

import cv2
import numpy as np
from pywinauto import mouse, Application
from pywinauto.controls.hwndwrapper import HwndWrapper
from screeninfo import get_monitors

from .screenshot import screenshot_monitor
from .image_matching import findMatchings

# Constants
CLICK_DEVIATION_RANGE = 5  # Random pixel deviation for more human-like clicks
DEFAULT_MONITOR = 1

# Global variable for language/asset path
_current_language = "EN"


def _get_base_path() -> str:
    """Get the base path for assets, works both in dev and when packaged with PyInstaller."""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return sys._MEIPASS
    else:
        # Running in development
        return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


_assets_base_path = os.path.join(_get_base_path(), "assets")


def set_language(lang: str) -> None:
    """Set the current language for asset loading (EN or CN)."""
    global _current_language
    if lang in ["EN", "CN"]:
        _current_language = lang
    else:
        raise ValueError(f"Invalid language: {lang}. Must be 'EN' or 'CN'")


def get_language() -> str:
    """Get the current language setting."""
    return _current_language


def get_asset_path(filename: str) -> str:
    """Get the full path to an asset file based on current language."""
    return os.path.join(_assets_base_path, _current_language, filename)


def get_game_window() -> Optional[HwndWrapper]:
    """
    Get the game window object.
    
    Returns:
        The game window object, or None if not found.
    """
    try:
        app = Application().connect(class_name="UnityWndClass", title="AFK Journey")
        return app.window(title="AFK Journey")
    except Exception as e:
        print(f"Could not find game window: {e}")
        return None


def get_game_monitor() -> int:
    """
    Detect which monitor the game window is on.
    
    Returns:
        Monitor number (1-indexed for mss). Defaults to 1 if detection fails.
    """
    window = get_game_window()
    if window is None:
        return DEFAULT_MONITOR
    
    try:
        rect = window.rectangle()
        window_center_x = (rect.left + rect.right) // 2
        window_center_y = (rect.top + rect.bottom) // 2
        
        monitors = get_monitors()
        for i, monitor in enumerate(monitors):
            if (monitor.x <= window_center_x < monitor.x + monitor.width and
                monitor.y <= window_center_y < monitor.y + monitor.height):
                return i + 1  # mss uses 1-indexed monitors
        
        return DEFAULT_MONITOR
    except Exception as e:
        print(f"Error detecting monitor: {e}")
        return DEFAULT_MONITOR


def get_game_window_offset() -> Tuple[int, int]:
    """
    Get the game window's position offset for accurate clicking.
    
    Returns:
        Tuple of (x, y) coordinates for the window's top-left corner.
    """
    window = get_game_window()
    if window is None:
        monitors = get_monitors()
        return monitors[0].x, monitors[0].y
    
    try:
        rect = window.rectangle()
        return rect.left, rect.top
    except Exception as e:
        print(f"Error getting window offset: {e}")
        monitors = get_monitors()
        return monitors[0].x, monitors[0].y


def click(x: int, y: int, focus: bool = True) -> None:
    """
    Perform a mouse click at the specified coordinates.
    
    Args:
        x: The x coordinate to click.
        y: The y coordinate to click.
        focus: Whether to focus the game window before clicking.
    """
    if focus:
        window = get_game_window()
        if window:
            window.set_focus()

    mouse.move(coords=(x, y))
    mouse.click(button='left', coords=(x, y))


def simulateClickOnImage(
    main_image: np.ndarray,
    targetImage: str,
    min_x: int = -9999,
    min_y: int = -9999,
    focus: bool = True
) -> bool:
    """
    Find a target image within a screenshot and click on it.
    
    Args:
        main_image: The screenshot to search in (grayscale numpy array).
        targetImage: The filename of the template image to find.
        min_x: Minimum x coordinate for valid matches.
        min_y: Minimum y coordinate for valid matches.
        focus: Whether to focus the game window before clicking.
        
    Returns:
        True if the image was found and clicked, False otherwise.
    """
    asset_path = get_asset_path(targetImage)
    
    template = cv2.imread(asset_path, 0)
    if template is None:
        print(f"Warning: Could not load template image: {asset_path}")
        return False
    
    h, w = template.shape[:2]
    loc = findMatchings(main_image, template)
    
    if not loc:
        return False
    
    # Find first match that meets minimum coordinate requirements
    for pt in loc:
        if pt[0] >= min_x and pt[1] >= min_y:
            # Calculate center of matched region with random deviation
            match_x = pt[0] + w // 2 + random.randint(-CLICK_DEVIATION_RANGE, CLICK_DEVIATION_RANGE)
            match_y = pt[1] + h // 2 + random.randint(-CLICK_DEVIATION_RANGE, CLICK_DEVIATION_RANGE)

            # Convert to screen coordinates
            offset_x, offset_y = get_game_window_offset()
            click(offset_x + match_x, offset_y + match_y, focus=focus)
            return True
    
    return False


def clickOnScreenShoot(targetImage: str, focus: bool = True) -> bool:
    """
    Take a screenshot of the game window's monitor and click on the target image if found.
    
    Args:
        targetImage: The filename of the template image to find and click.
        focus: Whether to focus the game window before clicking.
        
    Returns:
        True if the image was found and clicked, False otherwise.
    """
    monitor = get_game_monitor()
    screenshot = screenshot_monitor(monitor)
    return simulateClickOnImage(screenshot, targetImage, focus=focus)