from PIL import Image
import cv2
import numpy as np

def findMatchings(main_image: np.ndarray, template: np.ndarray) -> np.ndarray:
    result = cv2.matchTemplate(main_image, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(result >= threshold)
    loc = list(zip(*loc[::-1]))
    return loc

def simulateClickOnImage(main_image: np.ndarray, targetImage: str, min_x: int = -9999, min_y: int = -9999, focus: bool = True) -> bool:
    template = cv2.imread(targetImage, 0)
    w, h = template.shape[::-1]
    loc = findMatchings(main_image, template)
    deviation_range = 5
    if loc:
        index = 0
        while (loc[index][0] < min_x or loc[index][1] < min_y):
            index += 1
            if index == len(loc):
                return False
        pt = loc[index]
        match_x, match_y = pt[0] + w // 2, pt[1] + h // 2
        deviation_x = random.randint(-deviation_range, deviation_range)
        deviation_y = random.randint(-deviation_range, deviation_range)
        match_x += deviation_x
        match_y += deviation_y
        click(match_x, match_y, focus=focus)
        return True
    else:
        return False

def click(x: int, y: int, focus: bool = True):
    if focus:
        app = Application().connect(class_name="UnityWndClass", title="AFK Journey")
        app_dialog = app.window(title="AFK Journey")
        app_dialog.set_focus()
    mouse.move(coords=(x, y))
    mouse.click(button='left', coords=(x, y))

def clickOnScreenShoot(targetImage: str, monitor: int = 1, focus: bool = True) -> bool:
    screenShot = screenshot_monitor(monitor)
    if simulateClickOnImage(screenShot, targetImage, focus=focus):
        return True
    else:
        return False