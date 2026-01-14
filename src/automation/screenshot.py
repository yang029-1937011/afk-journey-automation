from PIL import Image
import mss
import numpy as np
import cv2
import time
from screeninfo import get_monitors
from pywinauto import mouse, Application
import random

def screenshot_monitor(monitor_number: int = 1, output="screenshot.png") -> np.ndarray:
    with mss.mss() as sct:
        monitors = sct.monitors

        if monitor_number < 1 or monitor_number >= len(monitors):
            raise ValueError(f"Monitor number {monitor_number} is out of range. Available monitors: {len(monitors)}")

        monitor = monitors[monitor_number]
        screenshot = sct.grab(monitor)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=output)

        img = np.array(screenshot, dtype=np.uint8)[:, :, :3]
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        return gray_img

def click(x: int, y: int, focus: bool = True):
    if focus:
        app = Application().connect(class_name="UnityWndClass", title="AFK Journey")
        app_dialog = app.window(title="AFK Journey")
        app_dialog.set_focus()

    mouse.move(coords=(x, y))
    mouse.click(button='left', coords=(x, y))

def clickOnScreenShoot(targetImage: str, monitor: int = 1, focus: bool = True) -> bool:
    screenShot = screenshot_monitor(monitor)
    return simulateClickOnImage(screenShot, targetImage, focus=focus)

def simulateClickOnImage(main_image: np.ndarray, targetImage: str, min_x: int = -9999, min_y: int = -9999, focus: bool = True) -> bool:
    template = cv2.imread(targetImage, 0)
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

        monitors = get_monitors()
        screen = monitors[0]
        screen_x, screen_y = screen.x, screen.y

        screen_x += match_x
        screen_y += match_y
        click(screen_x, screen_y, focus=focus)
        return True

    return False

def findMatchings(main_image: np.ndarray, template: np.ndarray) -> np.ndarray:
    result = cv2.matchTemplate(main_image, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(result >= threshold)
    loc = list(zip(*loc[::-1]))
    return loc