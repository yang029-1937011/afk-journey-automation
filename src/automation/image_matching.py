"""Image matching utilities with scale-invariant feature matching."""

import cv2
import numpy as np
from typing import List, Tuple, Optional


def _compute_match_center(template, kp1, kp2, good_matches):
    """Helper function to compute the center of matched region using homography."""
    try:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        
        # For very small match counts (< 8), use affine transform instead of homography
        # Homography needs at least 4 points but is unreliable with < 8
        if len(good_matches) < 8:
            # Use affine transform (needs only 3 points)
            if len(good_matches) >= 3:
                M = cv2.estimateAffinePartial2D(src_pts, dst_pts, method=cv2.RANSAC, 
                                                ransacReprojThreshold=5.0)
                if M is None or M[0] is None:
                    return None
                M_transform = M[0]
                inliers_mask = M[1].ravel()
            else:
                return None
        else:
            # Use full homography for more matches
            M_transform, inliers_mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            if M_transform is None:
                return None
        
        # Count inliers (matches that fit the transformation)
        inliers = int(np.sum(inliers_mask))
        inlier_ratio = inliers / len(good_matches) if len(good_matches) > 0 else 0
        
        # Adaptive inlier ratio validation based on match count
        # Very small templates with few features need more relaxed validation
        if len(good_matches) < 8:
            # For very small templates: require at least 60% inliers
            if inlier_ratio < 0.6:
                return None
        elif len(good_matches) < 15:
            # Require 70% inliers for 8-14 matches
            if inlier_ratio < 0.7:
                return None
        elif len(good_matches) < 20:
            # Require 65% inliers for 15-19 matches
            if inlier_ratio < 0.65:
                return None
        else:
            # Require 60% inliers for 20+ matches
            if inlier_ratio < 0.6:
                return None
        
        h, w = template.shape[:2]
        
        # Transform template corners to find matched region
        if len(good_matches) < 8:
            # For affine transform, need to add homogeneous coordinate
            pts = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
            # Apply affine transform manually
            dst = cv2.transform(pts, M_transform)
        else:
            # For homography, use perspective transform
            pts = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, M_transform)
        
        # Compute center of matched region
        # Note: Uses affine transform for <8 matches, homography for >=8 matches.
        # Scale and aspect ratio validation removed to support extreme DPI scaling.
        # Inlier ratio validation: 60% for <8 or 20+ matches, 70% for 8-14, 65% for 15-19.
        center_x = int(np.mean(dst[:, 0, 0]))
        center_y = int(np.mean(dst[:, 0, 1]))
        
        return [(center_x, center_y)]
    except Exception:
        return None


def findMatchings_sift(main_image: np.ndarray, template: np.ndarray, 
                       threshold: float = 0.65, min_matches: int = 10) -> List[Tuple[int, int]]:
    """
    Find template using SIFT (Scale-Invariant Feature Transform).
    Best for handling large scale differences.
    
    Args:
        main_image: The main image to search in (grayscale)
        template: The template image to search for (grayscale)
        threshold: Match quality threshold (Lowe's ratio test) - lower = stricter
        min_matches: Minimum number of good matches required
        
    Returns:
        List of (x, y) coordinates where matches were found (center of matched region)
    """
    try:
        # Create SIFT detector
        sift = cv2.SIFT_create()
        
        # Find keypoints and descriptors
        kp1, des1 = sift.detectAndCompute(template, None)
        kp2, des2 = sift.detectAndCompute(main_image, None)
        
        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            return []
        
        # Adaptive parameters for small templates
        # Small images have fewer features, so we need to adjust thresholds
        h, w = template.shape[:2]
        template_area = h * w
        
        # For very small templates (< 10,000 pixels), use relaxed thresholds
        if template_area < 10000:
            # Relax ratio test for small images (more permissive)
            actual_threshold = min(threshold + 0.1, 0.75)
            # Reduce minimum matches requirement
            actual_min_matches = max(4, min_matches // 2)
        else:
            actual_threshold = threshold
            actual_min_matches = min_matches
        
        # Use FLANN matcher for SIFT (better for float descriptors)
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        
        matches = flann.knnMatch(des1, des2, k=2)
        
        # Apply Lowe's ratio test
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < actual_threshold * n.distance:
                    good_matches.append(m)
        
        if len(good_matches) >= actual_min_matches:
            result = _compute_match_center(template, kp1, kp2, good_matches)
            if result:
                return result
    except Exception:
        pass
    
    return []


def findMatchings_akaze(main_image: np.ndarray, template: np.ndarray,
                        threshold: float = 0.65, min_matches: int = 10) -> List[Tuple[int, int]]:
    """
    Find template using AKAZE (Accelerated-KAZE).
    Good balance of speed and accuracy, scale-invariant.
    
    Args:
        main_image: The main image to search in (grayscale)
        template: The template image to search for (grayscale)
        threshold: Match quality threshold - lower = stricter
        min_matches: Minimum number of good matches required
        
    Returns:
        List of (x, y) coordinates where matches were found
    """
    try:
        # Create AKAZE detector
        akaze = cv2.AKAZE_create()
        
        # Find keypoints and descriptors
        kp1, des1 = akaze.detectAndCompute(template, None)
        kp2, des2 = akaze.detectAndCompute(main_image, None)
        
        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            return []
        
        # Adaptive parameters for small templates
        h, w = template.shape[:2]
        template_area = h * w
        
        if template_area < 10000:
            actual_threshold = min(threshold + 0.1, 0.75)
            actual_min_matches = max(4, min_matches // 2)
        else:
            actual_threshold = threshold
            actual_min_matches = min_matches
        
        # Use BFMatcher with Hamming distance for binary descriptors
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        matches = bf.knnMatch(des1, des2, k=2)
        
        # Apply ratio test
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < actual_threshold * n.distance:
                    good_matches.append(m)
        
        if len(good_matches) >= actual_min_matches:
            result = _compute_match_center(template, kp1, kp2, good_matches)
            if result:
                return result
    except Exception:
        pass
    
    return []


def findMatchings_multiscale(main_image: np.ndarray, template: np.ndarray, 
                            scales: List[float] = None, threshold: float = 0.7) -> List[Tuple[int, int]]:
    """
    Find template in main image using multi-scale template matching.
    This is especially useful for simple geometric shapes or buttons that may appear at different scales.
    
    Args:
        main_image: The main image to search in (grayscale)
        template: The template image to search for (grayscale)
        scales: List of scales to try (default: [0.5, 0.75, 1.0, 1.25, 1.5])
        threshold: The matching threshold (0-1), typically 0.7-0.9 for good matches
        
    Returns:
        List containing single (x, y) coordinate where best match was found (center point), or empty list
    """
    if scales is None:
        scales = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
    
    try:
        h, w = template.shape[:2]
        best_val = 0
        best_location = None
        
        for scale in scales:
            # Resize template
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            # Skip invalid sizes
            if new_w < 10 or new_h < 10 or new_w > main_image.shape[1] or new_h > main_image.shape[0]:
                continue
            
            scaled_template = cv2.resize(template, (new_w, new_h))
            
            # Perform template matching
            res = cv2.matchTemplate(main_image, scaled_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            
            # Track best match across all scales
            if max_val > best_val:
                best_val = max_val
                # Return center point
                center_x = max_loc[0] + new_w // 2
                center_y = max_loc[1] + new_h // 2
                best_location = (center_x, center_y)
        
        # Return result if above threshold
        if best_val >= threshold and best_location is not None:
            return [best_location]
    
    except Exception:
        pass
    
    return []


def findMatchings(main_image: np.ndarray, template: np.ndarray, threshold: float = 0.65) -> List[Tuple[int, int]]:
    """
    Find template in main image using multiple feature-based algorithms.
    Tries SIFT first (best for scale), then AKAZE, then multi-scale matching.
    Uses stricter matching parameters to reduce false positives.
    
    Args:
        main_image: The main image to search in (grayscale)
        template: The template image to search for (grayscale)
        threshold: The matching threshold (0-1), lower = stricter
        
    Returns:
        List of (x, y) coordinates where matches were found (center points)
    """
    # Try SIFT first (best for large scale differences)
    result = findMatchings_sift(main_image, template, threshold=threshold, min_matches=10)
    if result:
        return result
    
    # Try AKAZE as backup
    result = findMatchings_akaze(main_image, template, threshold=threshold, min_matches=10)
    if result:
        return result
    
    # For simple templates, try multi-scale matching as last resort
    # Use a higher threshold (0.7) for template matching as it's more reliable for simple shapes
    result = findMatchings_multiscale(main_image, template, 
                                     scales=[0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0], 
                                     threshold=0.7)
    if result:
        return result
    
    return []