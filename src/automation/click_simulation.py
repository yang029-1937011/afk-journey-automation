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

# Global variables
_current_language = "EN"
_debug_mode = False  # Toggle for debug output


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
    focus: bool = True,
    monitor_number: int = None
) -> bool:
    """
    Find a target image within a screenshot and click on it.
    
    Args:
        main_image: The screenshot to search in (grayscale numpy array).
        targetImage: The filename of the template image to find.
        min_x: Minimum x coordinate for valid matches.
        min_y: Minimum y coordinate for valid matches.
        focus: Whether to focus the game window before clicking.
        monitor_number: The monitor number the screenshot was taken from (for offset calculation)
        
    Returns:
        True if the image was found and clicked, False otherwise.
    """
    asset_path = get_asset_path(targetImage)
    
    _debug_print(f"Looking for template: {targetImage}")
    _debug_print(f"Template path: {asset_path}")
    
    template = cv2.imread(asset_path, 0)
    if template is None:
        print(f"Warning: Could not load template image: {asset_path}")
        return False
    
    _debug_print(f"Template size: {template.shape}")
    _debug_print(f"Screenshot size: {main_image.shape}")
    
    loc = findMatchings(main_image, template)
    
    if not loc:
        _debug_print(f"No matches found for {targetImage}")
        return False
    
    _debug_print(f"Found {len(loc)} match(es) for {targetImage}")
    
    # Find first match that meets minimum coordinate requirements
    # Note: findMatchings returns center coordinates directly
    for i, pt in enumerate(loc):
        _debug_print(f"Match {i+1} at relative position: ({pt[0]}, {pt[1]})")
        
        if pt[0] >= min_x and pt[1] >= min_y:
            # Add random deviation for more human-like clicking
            deviation_x = random.randint(-CLICK_DEVIATION_RANGE, CLICK_DEVIATION_RANGE)
            deviation_y = random.randint(-CLICK_DEVIATION_RANGE, CLICK_DEVIATION_RANGE)
            match_x = pt[0] + deviation_x
            match_y = pt[1] + deviation_y
            
            _debug_print(f"Applied deviation: ({deviation_x}, {deviation_y})")
            _debug_print(f"Adjusted match position: ({match_x}, {match_y})")

            # Convert to screen coordinates
            # Use monitor offset if provided, otherwise use game window offset
            if monitor_number is not None:
                offset_x, offset_y = get_monitor_offset(monitor_number)
            else:
                offset_x, offset_y = get_game_window_offset()
            
            screen_x = offset_x + match_x
            screen_y = offset_y + match_y
            
            _debug_print(f"Monitor/Window offset: ({offset_x}, {offset_y})")
            _debug_print(f"Final screen coordinates: ({screen_x}, {screen_y})")
            print(f"✓ '{targetImage}' matched at ({pt[0]}, {pt[1]}) -> clicking at screen ({screen_x}, {screen_y})")
            
            click(screen_x, screen_y, focus=focus)
            return True
    
    _debug_print(f"No valid matches found (all below min_x={min_x}, min_y={min_y})")
    return False


def findImageLocation(targetImage: str) -> Optional[Tuple[int, int]]:
    """
    Find a target image in the game window without clicking.
    
    Args:
        targetImage: The filename of the template image to find.
        
    Returns:
        Tuple of (screen_x, screen_y) coordinates if found, None otherwise.
    """
    monitor = get_game_monitor()
    screenshot = screenshot_monitor(monitor)
    
    if screenshot is None:
        return None
    
    asset_path = get_asset_path(targetImage)
    template = cv2.imread(asset_path, 0)
    
    if template is None:
        return None
    
    loc = findMatchings(screenshot, template)
    
    if not loc:
        return None
    
    # Get first match
    pt = loc[0]
    
    # Convert to screen coordinates
    offset_x, offset_y = get_monitor_offset(monitor)
    screen_x = offset_x + pt[0]
    screen_y = offset_y + pt[1]
    
    _debug_print(f"Found '{targetImage}' at screen coordinates ({screen_x}, {screen_y})")
    return (screen_x, screen_y)


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
    _debug_print(f"Taking screenshot from monitor {monitor}")
    screenshot = screenshot_monitor(monitor)
    return simulateClickOnImage(screenshot, targetImage, focus=focus, monitor_number=monitor)


def set_debug_mode(enabled: bool) -> None:
    """Enable or disable debug output."""
    global _debug_mode
    _debug_mode = enabled


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return _debug_mode


def _debug_print(message: str) -> None:
    """Print debug message if debug mode is enabled."""
    if _debug_mode:
        print(f"[DEBUG] {message}")


def get_monitor_offset(monitor_number: int) -> Tuple[int, int]:
    """
    Get the monitor's position offset in absolute screen coordinates.
    
    Args:
        monitor_number: Monitor number (1-indexed)
        
    Returns:
        Tuple of (x, y) coordinates for the monitor's top-left corner.
    """
    monitors = get_monitors()
    if monitor_number < 1 or monitor_number > len(monitors):
        _debug_print(f"Invalid monitor number {monitor_number}, using monitor 1")
        monitor_number = 1
    
    monitor = monitors[monitor_number - 1]
    _debug_print(f"Monitor {monitor_number} offset: ({monitor.x}, {monitor.y})")
    return monitor.x, monitor.y