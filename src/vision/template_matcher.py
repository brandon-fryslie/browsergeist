"""
Template Matching Module

Advanced computer vision module for finding UI elements on screen
using template matching, feature detection, and ML-based approaches.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, NamedTuple, Dict
from dataclasses import dataclass
import time
from pathlib import Path
import subprocess
import re
import difflib


@dataclass
class MatchResult:
    """Result of template matching operation"""
    x: int
    y: int
    width: int
    height: int
    confidence: float
    center_x: int
    center_y: int
    method: str
    
    @property
    def center(self) -> Tuple[int, int]:
        return (self.center_x, self.center_y)
    
    @property
    def top_left(self) -> Tuple[int, int]:
        return (self.x, self.y)
    
    @property
    def bottom_right(self) -> Tuple[int, int]:
        return (self.x + self.width, self.y + self.height)


class TemplateMatcher:
    """Advanced template matching with multiple algorithms"""
    
    def __init__(self):
        # Initialize SIFT for feature-based matching
        self.sift = cv2.SIFT_create()
        
        # FLANN parameters for feature matching
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        self.flann = cv2.FlannBasedMatcher(index_params, search_params)
    
    def find_template(self, 
                     screenshot: np.ndarray, 
                     template: np.ndarray,
                     confidence: float = 0.8,
                     method: str = "auto",
                     multi_scale: bool = True) -> Optional[MatchResult]:
        """
        Find template in screenshot using specified method
        
        Args:
            screenshot: Full screen capture
            template: Template image to find
            confidence: Minimum confidence threshold
            method: Matching method ('template', 'feature', 'auto', 'multi_scale')
            multi_scale: Enable multi-scale template matching
        """
        
        if method == "auto":
            # Try multi-scale matching first if enabled
            if multi_scale:
                result = self._match_multi_scale(screenshot, template, confidence)
                if result:
                    return result
            
            # Try feature matching for better accuracy
            result = self._match_features(screenshot, template, confidence)
            if result:
                return result
            
            # Fallback to standard template matching
            return self._match_template(screenshot, template, confidence)
        
        elif method == "template":
            return self._match_template(screenshot, template, confidence)
        
        elif method == "feature":
            return self._match_features(screenshot, template, confidence)
        
        elif method == "multi_scale":
            return self._match_multi_scale(screenshot, template, confidence)
        
        else:
            raise ValueError(f"Unknown matching method: {method}")
    
    def find_multiple(self,
                     screenshot: np.ndarray,
                     template: np.ndarray,
                     confidence: float = 0.8,
                     max_matches: int = 10) -> List[MatchResult]:
        """Find multiple instances of template in screenshot"""
        
        matches = []
        
        # Use template matching for multiple detection
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY) if len(screenshot.shape) == 3 else screenshot
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) if len(template.shape) == 3 else template
        
        result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
        
        # Find all matches above threshold
        locations = np.where(result >= confidence)
        
        # Group nearby matches
        h, w = gray_template.shape
        rectangles = []
        
        for pt in zip(*locations[::-1]):
            rectangles.append([pt[0], pt[1], w, h])
        
        # Apply non-maximum suppression
        rectangles = cv2.groupRectangles(rectangles, 1, 0.2)[0]
        
        for i, rect in enumerate(rectangles[:max_matches]):
            x, y, w, h = rect
            center_x = x + w // 2
            center_y = y + h // 2
            match_confidence = result[y, x]
            
            matches.append(MatchResult(
                x=x, y=y, width=w, height=h,
                confidence=float(match_confidence),
                center_x=center_x, center_y=center_y,
                method="template_multi"
            ))
        
        return sorted(matches, key=lambda m: m.confidence, reverse=True)
    
    def _match_template(self, 
                       screenshot: np.ndarray, 
                       template: np.ndarray,
                       confidence: float) -> Optional[MatchResult]:
        """Standard template matching using normalized cross-correlation"""
        
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY) if len(screenshot.shape) == 3 else screenshot
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) if len(template.shape) == 3 else template
        
        # Try multiple methods and return best result
        methods = [
            cv2.TM_CCOEFF_NORMED,
            cv2.TM_CCORR_NORMED,
            cv2.TM_SQDIFF_NORMED
        ]
        
        best_result = None
        best_confidence = 0
        
        for method in methods:
            result = cv2.matchTemplate(gray_screenshot, gray_template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if method == cv2.TM_SQDIFF_NORMED:
                match_confidence = 1 - min_val
                top_left = min_loc
            else:
                match_confidence = max_val
                top_left = max_loc
            
            if match_confidence > best_confidence and match_confidence >= confidence:
                h, w = gray_template.shape
                center_x = top_left[0] + w // 2
                center_y = top_left[1] + h // 2
                
                best_result = MatchResult(
                    x=top_left[0], y=top_left[1], width=w, height=h,
                    confidence=match_confidence,
                    center_x=center_x, center_y=center_y,
                    method="template"
                )
                best_confidence = match_confidence
        
        return best_result
    
    def _match_features(self, 
                       screenshot: np.ndarray, 
                       template: np.ndarray,
                       confidence: float) -> Optional[MatchResult]:
        """Feature-based matching using SIFT descriptors"""
        
        try:
            gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY) if len(screenshot.shape) == 3 else screenshot
            gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) if len(template.shape) == 3 else template
            
            # Find keypoints and descriptors
            kp1, des1 = self.sift.detectAndCompute(gray_template, None)
            kp2, des2 = self.sift.detectAndCompute(gray_screenshot, None)
            
            if des1 is None or des2 is None or len(des1) < 10:
                return None
            
            # Match features
            matches = self.flann.knnMatch(des1, des2, k=2)
            
            # Apply Lowe's ratio test
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < 0.7 * n.distance:
                        good_matches.append(m)
            
            if len(good_matches) < 10:
                return None
            
            # Find homography
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            
            H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            
            if H is None:
                return None
            
            # Transform template corners to find location in screenshot
            h, w = gray_template.shape
            corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
            transformed_corners = cv2.perspectiveTransform(corners, H)
            
            # Calculate bounding box
            x_coords = transformed_corners[:, 0, 0]
            y_coords = transformed_corners[:, 0, 1]
            
            x = int(np.min(x_coords))
            y = int(np.min(y_coords))
            width = int(np.max(x_coords) - np.min(x_coords))
            height = int(np.max(y_coords) - np.min(y_coords))
            
            center_x = x + width // 2
            center_y = y + height // 2
            
            # Calculate confidence based on inlier ratio
            inlier_ratio = np.sum(mask) / len(mask) if mask is not None else 0
            
            if inlier_ratio >= confidence:
                return MatchResult(
                    x=x, y=y, width=width, height=height,
                    confidence=float(inlier_ratio),
                    center_x=center_x, center_y=center_y,
                    method="feature"
                )
        
        except Exception as e:
            # Feature matching failed, return None
            pass
        
        return None
    
    def _match_multi_scale(self, 
                          screenshot: np.ndarray, 
                          template: np.ndarray,
                          confidence: float) -> Optional[MatchResult]:
        """Multi-scale template matching for different screen resolutions"""
        
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY) if len(screenshot.shape) == 3 else screenshot
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) if len(template.shape) == 3 else template
        
        # Scale factors to try (0.5x to 2.0x in increments)
        scale_factors = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
        
        best_result = None
        best_confidence = 0
        
        original_h, original_w = gray_template.shape
        
        for scale in scale_factors:
            # Scale the template
            scaled_w = int(original_w * scale)
            scaled_h = int(original_h * scale)
            
            # Skip if scaled template is larger than screenshot
            if scaled_h > gray_screenshot.shape[0] or scaled_w > gray_screenshot.shape[1]:
                continue
            
            # Skip if scaled template is too small
            if scaled_h < 10 or scaled_w < 10:
                continue
            
            scaled_template = cv2.resize(gray_template, (scaled_w, scaled_h))
            
            # Perform template matching
            result = cv2.matchTemplate(gray_screenshot, scaled_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_confidence and max_val >= confidence:
                # Calculate actual dimensions and position
                center_x = max_loc[0] + scaled_w // 2
                center_y = max_loc[1] + scaled_h // 2
                
                best_result = MatchResult(
                    x=max_loc[0], y=max_loc[1], 
                    width=scaled_w, height=scaled_h,
                    confidence=max_val,
                    center_x=center_x, center_y=center_y,
                    method=f"multi_scale_{scale:.1f}x"
                )
                best_confidence = max_val
        
        return best_result
    
    def find_template_with_fallbacks(self, 
                                   screenshot: np.ndarray, 
                                   template: np.ndarray,
                                   confidence: float = 0.8) -> Optional[MatchResult]:
        """Find template with comprehensive fallback strategy"""
        
        # Strategy 1: Multi-scale matching (most robust)
        result = self._match_multi_scale(screenshot, template, confidence)
        if result and result.confidence >= confidence:
            return result
        
        # Strategy 2: Feature matching (good for complex images)
        result = self._match_features(screenshot, template, confidence * 0.9)  # Lower threshold
        if result and result.confidence >= confidence * 0.9:
            return result
        
        # Strategy 3: Standard template matching with multiple methods
        result = self._match_template(screenshot, template, confidence * 0.8)  # Even lower threshold
        if result and result.confidence >= confidence * 0.8:
            return result
        
        # Strategy 4: Try with image preprocessing
        result = self._match_with_preprocessing(screenshot, template, confidence * 0.7)
        if result and result.confidence >= confidence * 0.7:
            return result
        
        # Strategy 5: Last resort - very low confidence threshold
        result = self._match_template(screenshot, template, 0.5)
        if result:
            # Mark as low confidence
            result.method += "_low_confidence"
            return result
        
        return None
    
    def _match_with_preprocessing(self, 
                                screenshot: np.ndarray, 
                                template: np.ndarray,
                                confidence: float) -> Optional[MatchResult]:
        """Template matching with image preprocessing techniques"""
        
        # Convert to grayscale
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY) if len(screenshot.shape) == 3 else screenshot
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) if len(template.shape) == 3 else template
        
        # Try different preprocessing techniques
        preprocessing_methods = [
            ("original", lambda img: img),
            ("blur", lambda img: cv2.GaussianBlur(img, (5, 5), 0)),
            ("threshold", lambda img: cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]),
            ("edges", lambda img: cv2.Canny(img, 50, 150)),
            ("morphology", lambda img: cv2.morphologyEx(img, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))))
        ]
        
        best_result = None
        best_confidence = 0
        
        for method_name, preprocess_func in preprocessing_methods:
            try:
                proc_screenshot = preprocess_func(gray_screenshot)
                proc_template = preprocess_func(gray_template)
                
                # Perform template matching
                result = cv2.matchTemplate(proc_screenshot, proc_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val > best_confidence and max_val >= confidence:
                    h, w = proc_template.shape
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2
                    
                    best_result = MatchResult(
                        x=max_loc[0], y=max_loc[1], width=w, height=h,
                        confidence=max_val,
                        center_x=center_x, center_y=center_y,
                        method=f"preprocessed_{method_name}"
                    )
                    best_confidence = max_val
                    
            except Exception:
                continue
        
        return best_result
    
    def find_text(self, 
                  screenshot: np.ndarray,
                  target_text: str,
                  confidence: float = 0.8,
                  fuzzy_threshold: float = 0.6) -> Optional[MatchResult]:
        """Find text on screen using OCR with fuzzy matching (requires pytesseract)
        
        Args:
            screenshot: Screenshot image array
            target_text: Text to search for
            confidence: OCR confidence threshold (0.0-1.0)
            fuzzy_threshold: Fuzzy matching threshold (0.0-1.0)
        """
        
        try:
            import pytesseract
            
            # Preprocess image for better OCR
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY) if len(screenshot.shape) == 3 else screenshot
            
            # Apply threshold to improve text detection
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Get text data with bounding boxes
            data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
            
            target_lower = target_text.lower().strip()
            best_match = None
            best_similarity = 0.0
            
            # Search for target text with fuzzy matching
            for i, text in enumerate(data['text']):
                if not text or not text.strip():
                    continue
                    
                text_clean = text.strip().lower()
                ocr_confidence = float(data['conf'][i]) / 100.0
                
                # Skip if OCR confidence too low
                if ocr_confidence < confidence:
                    continue
                
                # Exact substring match (highest priority)
                if target_lower in text_clean:
                    similarity = 1.0
                elif text_clean in target_lower:
                    similarity = 0.95
                else:
                    # Fuzzy matching using sequence matcher
                    similarity = difflib.SequenceMatcher(None, target_lower, text_clean).ratio()
                
                # Check if this is the best match so far
                if similarity >= fuzzy_threshold and similarity > best_similarity:
                    best_similarity = similarity
                    best_match = {
                        'index': i,
                        'similarity': similarity,
                        'ocr_confidence': ocr_confidence,
                        'text': text
                    }
            
            # Return best match if found
            if best_match:
                i = best_match['index']
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                
                # Combine fuzzy similarity and OCR confidence for final confidence
                final_confidence = (best_match['similarity'] * 0.7 + best_match['ocr_confidence'] * 0.3)
                
                return MatchResult(
                    x=x, y=y, width=w, height=h,
                    confidence=final_confidence,
                    center_x=x + w // 2, center_y=y + h // 2,
                    method=f"ocr_fuzzy({best_match['similarity']:.2f})"
                )
        
        except ImportError:
            print("Warning: pytesseract not installed, text search unavailable")
        except Exception as e:
            print(f"OCR error: {e}")
        
        return None


class MultiMonitorMatcher:
    """Template matching across multiple monitors"""
    
    def __init__(self):
        self.matcher = TemplateMatcher()
        self.monitor_info = self._get_monitor_info()
    
    def _get_monitor_info(self) -> List[Dict]:
        """Get information about connected monitors"""
        try:
            # Use system_profiler to get display information
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                  capture_output=True, text=True)
            
            monitors = []
            if result.returncode == 0:
                # Parse monitor information (simplified)
                # In a full implementation, we'd parse the detailed output
                # For now, assume primary monitor at 0,0
                monitors.append({
                    'id': 0,
                    'x': 0,
                    'y': 0,
                    'width': 1920,  # Default values
                    'height': 1080,
                    'primary': True
                })
            
            return monitors
        except Exception:
            # Fallback to single monitor
            return [{
                'id': 0,
                'x': 0,
                'y': 0,
                'width': 1920,
                'height': 1080,
                'primary': True
            }]
    
    def find_template_all_monitors(self, 
                                  template: np.ndarray,
                                  confidence: float = 0.8,
                                  method: str = "auto") -> List[MatchResult]:
        """Find template across all connected monitors"""
        results = []
        
        # For now, we'll work with the primary monitor
        # In a full implementation, we'd capture each monitor separately
        try:
            # Use the screen capture from the main daemon
            import socket
            import json
            
            # Connect to daemon to get screenshot
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect('/tmp/browsergeist.sock')
            
            command = json.dumps({"command": "screenshot"})
            sock.send(command.encode() + b'\n')
            
            response = sock.recv(1024).decode()
            data = json.loads(response)
            
            if data.get('status') == 'success':
                # Convert base64 image data back to numpy array
                import base64
                from PIL import Image
                import io
                
                image_data = base64.b64decode(data['image'])
                screenshot = np.array(Image.open(io.BytesIO(image_data)))
                
                # Find template in screenshot
                result = self.matcher.find_template(screenshot, template, confidence, method)
                if result:
                    # Adjust coordinates for monitor offset (if needed)
                    monitor = self.monitor_info[0]  # Primary monitor
                    result.x += monitor['x']
                    result.y += monitor['y']
                    result.center_x += monitor['x']
                    result.center_y += monitor['y']
                    results.append(result)
            
            sock.close()
            
        except Exception as e:
            # Fallback: return empty results
            print(f"Multi-monitor capture failed: {e}")
        
        return results
    
    def get_monitor_at_point(self, x: int, y: int) -> Optional[Dict]:
        """Get monitor information for a given point"""
        for monitor in self.monitor_info:
            if (monitor['x'] <= x < monitor['x'] + monitor['width'] and
                monitor['y'] <= y < monitor['y'] + monitor['height']):
                return monitor
        return None


class VisionCache:
    """Cache for template images and matching results"""
    
    def __init__(self, max_size: int = 100, ttl: float = 60.0):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def get_template(self, image_path: str) -> Optional[np.ndarray]:
        """Get cached template image"""
        current_time = time.time()
        
        if image_path in self.cache:
            # Check if cached item is still valid
            if current_time - self.access_times[image_path] < self.ttl:
                self.access_times[image_path] = current_time
                return self.cache[image_path]
            else:
                # Remove expired item
                del self.cache[image_path]
                del self.access_times[image_path]
        
        # Load and cache template
        if Path(image_path).exists():
            template = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if template is not None:
                self._add_to_cache(image_path, template, current_time)
                return template
        
        return None
    
    def _add_to_cache(self, key: str, value: np.ndarray, current_time: float):
        """Add item to cache with size management"""
        # Remove oldest items if cache is full
        while len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = value
        self.access_times[key] = current_time
    
    def clear(self):
        """Clear all cached items"""
        self.cache.clear()
        self.access_times.clear()
