"""Image matching utilities for template matching."""

import cv2
import numpy as np
from typing import List, Tuple


def findMatchings(main_image: np.ndarray, template: np.ndarray, threshold: float = 0.8) -> List[Tuple[int, int]]:
    """
    Find all locations where the template matches in the main image.
    
    Args:
        main_image: The main image to search in (grayscale)
        template: The template image to search for (grayscale)
        threshold: The matching threshold (0-1), higher = stricter matching
        
    Returns:
        List of (x, y) coordinates where matches were found
    """
    result = cv2.matchTemplate(main_image, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    loc = list(zip(*loc[::-1]))
    return loc