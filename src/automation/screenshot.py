"""Screenshot utilities for capturing monitor screens."""

import mss
import numpy as np
import cv2


def screenshot_monitor(monitor_number: int = 1, output: str = "screenshot.png") -> np.ndarray:
    """
    Take a screenshot of a specific monitor.
    
    Args:
        monitor_number: The monitor number (1-indexed)
        output: The output file path for the screenshot
        
    Returns:
        Grayscale image as numpy array
    """
    with mss.mss() as sct:
        monitors = sct.monitors

        if monitor_number < 1 or monitor_number >= len(monitors):
            raise ValueError(
                f"Monitor number {monitor_number} is out of range. "
                f"Available monitors: {len(monitors) - 1}"
            )

        monitor = monitors[monitor_number]
        screenshot = sct.grab(monitor)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=output)

        img = np.array(screenshot, dtype=np.uint8)[:, :, :3]
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        return gray_img