"""
BrowserGeist Wait Conditions and Utilities

Comprehensive waiting system inspired by Playwright's API for robust
automation timing and element readiness verification.
"""

import time
import asyncio
from typing import Callable, Optional, Any, Union, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
import cv2
import numpy as np


@dataclass
class WaitResult:
    """Result of a wait operation"""
    success: bool
    value: Any = None
    timeout: bool = False
    error: Optional[Exception] = None
    elapsed_time: float = 0.0
    attempts: int = 0


class WaitCondition(ABC):
    """Base class for wait conditions"""
    
    @abstractmethod
    def check(self, bot) -> bool:
        """Check if the condition is met"""
        pass
    
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what we're waiting for"""
        pass


class ElementVisibleCondition(WaitCondition):
    """Wait for an element to be visible on screen"""
    
    def __init__(self, text: str, confidence: float = 0.8, use_accessibility: bool = True):
        self.text = text
        self.confidence = confidence
        self.use_accessibility = use_accessibility
        self._last_result = None
    
    def check(self, bot) -> bool:
        try:
            target_coords = None
            
            # Try accessibility API first if enabled
            if self.use_accessibility:
                try:
                    command = {"action": "find_element_by_text", "text": self.text}
                    result = bot._send_command(command)
                    if result.success and "x" in result.details and "y" in result.details:
                        target_coords = (result.details["x"], result.details["y"])
                except Exception:
                    pass
            
            # Fall back to OCR if accessibility didn't work
            if not target_coords:
                screenshot = bot._take_screenshot()
                if screenshot is not None:
                    ocr_result = bot.vision.find_text(screenshot, self.text, self.confidence)
                    if ocr_result:
                        target_coords = ocr_result.center
            
            self._last_result = target_coords
            return target_coords is not None
            
        except Exception as e:
            return False
    
    def description(self) -> str:
        return f"Element with text '{self.text}' to be visible"
    
    def get_coordinates(self):
        """Get the coordinates of the found element"""
        return self._last_result


class TextVisibleCondition(WaitCondition):
    """Wait for specific text to appear on screen"""
    
    def __init__(self, text: str, confidence: float = 0.8):
        self.text = text
        self.confidence = confidence
        self._last_result = None
    
    def check(self, bot) -> bool:
        try:
            screenshot = bot._take_screenshot()
            if screenshot is not None:
                result = bot.vision.find_text(screenshot, self.text, self.confidence)
                self._last_result = result
                return result is not None
            return False
        except Exception:
            return False
    
    def description(self) -> str:
        return f"Text '{self.text}' to appear on screen"
    
    def get_result(self):
        """Get the OCR result of the found text"""
        return self._last_result


class ImageVisibleCondition(WaitCondition):
    """Wait for an image template to be visible on screen"""
    
    def __init__(self, image_path: str, confidence: float = 0.8):
        self.image_path = image_path
        self.confidence = confidence
        self._last_result = None
    
    def check(self, bot) -> bool:
        try:
            screenshot = bot._take_screenshot()
            if screenshot is not None:
                result = bot.vision.find_template_with_fallbacks(screenshot, self.image_path, self.confidence)
                self._last_result = result
                return result is not None
            return False
        except Exception:
            return False
    
    def description(self) -> str:
        return f"Image '{self.image_path}' to be visible"
    
    def get_result(self):
        """Get the template matching result"""
        return self._last_result


class CustomCondition(WaitCondition):
    """Wait for a custom condition function to return True"""
    
    def __init__(self, condition_func: Callable, description: str, *args, **kwargs):
        self.condition_func = condition_func
        self._description = description
        self.args = args
        self.kwargs = kwargs
        self._last_result = None
    
    def check(self, bot) -> bool:
        try:
            result = self.condition_func(bot, *self.args, **self.kwargs)
            self._last_result = result
            return bool(result)
        except Exception:
            return False
    
    def description(self) -> str:
        return self._description
    
    def get_result(self):
        """Get the result of the custom condition"""
        return self._last_result


class ElementClickableCondition(WaitCondition):
    """Wait for an element to be clickable (visible and not moving)"""
    
    def __init__(self, text: str, confidence: float = 0.8, stability_duration: float = 0.5, use_accessibility: bool = True):
        self.text = text
        self.confidence = confidence
        self.stability_duration = stability_duration
        self.use_accessibility = use_accessibility
        self._last_position = None
        self._stable_since = None
        self._last_result = None
    
    def check(self, bot) -> bool:
        try:
            target_coords = None
            
            # Try accessibility API first if enabled
            if self.use_accessibility:
                try:
                    command = {"action": "find_element_by_text", "text": self.text}
                    result = bot._send_command(command)
                    if result.success and "x" in result.details and "y" in result.details:
                        target_coords = (result.details["x"], result.details["y"])
                except Exception:
                    pass
            
            # Fall back to OCR if accessibility didn't work
            if not target_coords:
                screenshot = bot._take_screenshot()
                if screenshot is not None:
                    ocr_result = bot.vision.find_text(screenshot, self.text, self.confidence)
                    if ocr_result:
                        target_coords = ocr_result.center
            
            if not target_coords:
                return False
            
            current_time = time.time()
            
            # Check if position has changed
            if self._last_position is None:
                self._last_position = target_coords
                self._stable_since = current_time
                return False
            
            # Calculate distance moved
            distance = ((target_coords[0] - self._last_position[0]) ** 2 + 
                       (target_coords[1] - self._last_position[1]) ** 2) ** 0.5
            
            if distance <= 2:  # Element is stable (within 2 pixels)
                if current_time - self._stable_since >= self.stability_duration:
                    self._last_result = target_coords
                    return True
            else:
                # Element moved, reset stability timer
                self._last_position = target_coords
                self._stable_since = current_time
            
            return False
            
        except Exception:
            return False
    
    def description(self) -> str:
        return f"Element with text '{self.text}' to be clickable (visible and stable)"
    
    def get_coordinates(self):
        """Get the coordinates of the clickable element"""
        return self._last_result


class ElementDisappearedCondition(WaitCondition):
    """Wait for an element to disappear from screen"""
    
    def __init__(self, text: str, confidence: float = 0.8, use_accessibility: bool = True):
        self.text = text
        self.confidence = confidence
        self.use_accessibility = use_accessibility
    
    def check(self, bot) -> bool:
        try:
            target_coords = None
            
            # Try accessibility API first if enabled
            if self.use_accessibility:
                try:
                    command = {"action": "find_element_by_text", "text": self.text}
                    result = bot._send_command(command)
                    if result.success and "x" in result.details and "y" in result.details:
                        target_coords = (result.details["x"], result.details["y"])
                except Exception:
                    pass
            
            # Fall back to OCR if accessibility didn't work
            if not target_coords:
                screenshot = bot._take_screenshot()
                if screenshot is not None:
                    ocr_result = bot.vision.find_text(screenshot, self.text, self.confidence)
                    if ocr_result:
                        target_coords = ocr_result.center
            
            # Element has disappeared if we can't find it
            return target_coords is None
            
        except Exception:
            # If there's an error, assume element is still there
            return False
    
    def description(self) -> str:
        return f"Element with text '{self.text}' to disappear"


class ScreenStableCondition(WaitCondition):
    """Wait for the screen to stop changing (useful after navigation)"""
    
    def __init__(self, stability_duration: float = 1.0, similarity_threshold: float = 0.95):
        self.stability_duration = stability_duration
        self.similarity_threshold = similarity_threshold
        self.first_screenshot = None
        self.stable_since = None
    
    def check(self, bot) -> bool:
        try:
            current_screenshot = bot._take_screenshot()
            if current_screenshot is None:
                return False
            
            current_time = time.time()
            
            if self.first_screenshot is None:
                self.first_screenshot = current_screenshot
                self.stable_since = current_time
                return False
            
            # Compare current screenshot with the first one
            similarity = self._calculate_similarity(self.first_screenshot, current_screenshot)
            
            if similarity >= self.similarity_threshold:
                # Screen is stable, check if it's been stable long enough
                if current_time - self.stable_since >= self.stability_duration:
                    return True
            else:
                # Screen changed, reset stability timer
                self.first_screenshot = current_screenshot
                self.stable_since = current_time
            
            return False
            
        except Exception:
            return False
    
    def _calculate_similarity(self, img1, img2) -> float:
        """Calculate similarity between two images"""
        try:
            # Convert to grayscale for comparison
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            # Resize to same dimensions if needed
            if gray1.shape != gray2.shape:
                h, w = min(gray1.shape[0], gray2.shape[0]), min(gray1.shape[1], gray2.shape[1])
                gray1 = cv2.resize(gray1, (w, h))
                gray2 = cv2.resize(gray2, (w, h))
            
            # Calculate structural similarity
            diff = cv2.absdiff(gray1, gray2)
            non_zero_count = np.count_nonzero(diff)
            total_pixels = diff.shape[0] * diff.shape[1]
            
            similarity = 1.0 - (non_zero_count / total_pixels)
            return similarity
            
        except Exception:
            return 0.0
    
    def description(self) -> str:
        return f"Screen to be stable for {self.stability_duration}s"


class MultipleCondition(WaitCondition):
    """Wait for multiple conditions (AND or OR logic)"""
    
    def __init__(self, conditions: List[WaitCondition], logic: str = "AND"):
        self.conditions = conditions
        self.logic = logic.upper()
        if self.logic not in ["AND", "OR"]:
            raise ValueError("Logic must be 'AND' or 'OR'")
    
    def check(self, bot) -> bool:
        results = [condition.check(bot) for condition in self.conditions]
        
        if self.logic == "AND":
            return all(results)
        else:  # OR
            return any(results)
    
    def description(self) -> str:
        descriptions = [condition.description() for condition in self.conditions]
        connector = " AND " if self.logic == "AND" else " OR "
        return f"({connector.join(descriptions)})"


class WaitTimeoutError(Exception):
    """Raised when a wait operation times out"""
    
    def __init__(self, condition_description: str, timeout: float, attempts: int):
        self.condition_description = condition_description
        self.timeout = timeout
        self.attempts = attempts
        super().__init__(f"Timeout after {timeout}s waiting for: {condition_description} (tried {attempts} times)")


class WaitSystem:
    """Main wait system providing Playwright-inspired waiting functionality"""
    
    def __init__(self, bot, default_timeout: float = 30.0, default_poll_interval: float = 0.5):
        self.bot = bot
        self.default_timeout = default_timeout
        self.default_poll_interval = default_poll_interval
    
    def for_element(self, text: str, 
                   timeout: Optional[float] = None,
                   confidence: float = 0.8,
                   use_accessibility: bool = True) -> WaitResult:
        """Wait for an element to be visible"""
        condition = ElementVisibleCondition(text, confidence, use_accessibility)
        result = self._wait_for_condition(condition, timeout)
        if result.success:
            result.value = condition.get_coordinates()
        return result
    
    def for_text(self, text: str,
                timeout: Optional[float] = None,
                confidence: float = 0.8) -> WaitResult:
        """Wait for text to appear on screen"""
        condition = TextVisibleCondition(text, confidence)
        result = self._wait_for_condition(condition, timeout)
        if result.success:
            result.value = condition.get_result()
        return result
    
    def for_image(self, image_path: str,
                 timeout: Optional[float] = None,
                 confidence: float = 0.8) -> WaitResult:
        """Wait for an image template to be visible"""
        condition = ImageVisibleCondition(image_path, confidence)
        result = self._wait_for_condition(condition, timeout)
        if result.success:
            result.value = condition.get_result()
        return result
    
    def for_condition(self, condition_func: Callable,
                     description: str,
                     timeout: Optional[float] = None,
                     *args, **kwargs) -> WaitResult:
        """Wait for a custom condition"""
        condition = CustomCondition(condition_func, description, *args, **kwargs)
        result = self._wait_for_condition(condition, timeout)
        if result.success:
            result.value = condition.get_result()
        return result
    
    def for_stable_screen(self, timeout: Optional[float] = None,
                         stability_duration: float = 1.0,
                         similarity_threshold: float = 0.95) -> WaitResult:
        """Wait for screen to stop changing"""
        condition = ScreenStableCondition(stability_duration, similarity_threshold)
        return self._wait_for_condition(condition, timeout)
    
    def for_any(self, conditions: List[WaitCondition],
               timeout: Optional[float] = None) -> WaitResult:
        """Wait for any of the conditions to be met (OR logic)"""
        condition = MultipleCondition(conditions, "OR")
        return self._wait_for_condition(condition, timeout)
    
    def for_all(self, conditions: List[WaitCondition],
               timeout: Optional[float] = None) -> WaitResult:
        """Wait for all conditions to be met (AND logic)"""
        condition = MultipleCondition(conditions, "AND")
        return self._wait_for_condition(condition, timeout)
    
    def for_clickable(self, text: str,
                     timeout: Optional[float] = None,
                     confidence: float = 0.8,
                     stability_duration: float = 0.5,
                     use_accessibility: bool = True) -> WaitResult:
        """Wait for an element to be clickable (visible and stable)"""
        condition = ElementClickableCondition(text, confidence, stability_duration, use_accessibility)
        result = self._wait_for_condition(condition, timeout)
        if result.success:
            result.value = condition.get_coordinates()
        return result
    
    def for_element_to_disappear(self, text: str,
                               timeout: Optional[float] = None,
                               confidence: float = 0.8,
                               use_accessibility: bool = True) -> WaitResult:
        """Wait for an element to disappear from screen"""
        condition = ElementDisappearedCondition(text, confidence, use_accessibility)
        return self._wait_for_condition(condition, timeout)
    
    def _wait_for_condition(self, condition: WaitCondition, timeout: Optional[float] = None) -> WaitResult:
        """Internal method to wait for any condition"""
        timeout = timeout or self.default_timeout
        start_time = time.time()
        attempts = 0
        
        while True:
            attempts += 1
            elapsed = time.time() - start_time
            
            try:
                if condition.check(self.bot):
                    return WaitResult(
                        success=True,
                        timeout=False,
                        elapsed_time=elapsed,
                        attempts=attempts
                    )
            except Exception as e:
                # Continue trying unless we've timed out
                if elapsed >= timeout:
                    return WaitResult(
                        success=False,
                        timeout=True,
                        error=e,
                        elapsed_time=elapsed,
                        attempts=attempts
                    )
            
            if elapsed >= timeout:
                return WaitResult(
                    success=False,
                    timeout=True,
                    elapsed_time=elapsed,
                    attempts=attempts
                )
            
            time.sleep(self.default_poll_interval)


class ExpectationSystem:
    """Assertion system with automatic waiting"""
    
    def __init__(self, wait_system: WaitSystem):
        self.wait_system = wait_system
    
    def element_to_be_visible(self, text: str,
                             timeout: Optional[float] = None,
                             confidence: float = 0.8,
                             use_accessibility: bool = True):
        """Assert that an element becomes visible within timeout"""
        result = self.wait_system.for_element(text, timeout, confidence, use_accessibility)
        if not result.success:
            if result.timeout:
                raise WaitTimeoutError(f"Element '{text}' to be visible", 
                                     timeout or self.wait_system.default_timeout, 
                                     result.attempts)
            else:
                raise Exception(f"Failed to find element '{text}': {result.error}")
        return result.value
    
    def text_to_be_visible(self, text: str,
                          timeout: Optional[float] = None,
                          confidence: float = 0.8):
        """Assert that text becomes visible within timeout"""
        result = self.wait_system.for_text(text, timeout, confidence)
        if not result.success:
            if result.timeout:
                raise WaitTimeoutError(f"Text '{text}' to be visible",
                                     timeout or self.wait_system.default_timeout,
                                     result.attempts)
            else:
                raise Exception(f"Failed to find text '{text}': {result.error}")
        return result.value
    
    def screen_to_be_stable(self, timeout: Optional[float] = None,
                           stability_duration: float = 1.0):
        """Assert that screen becomes stable within timeout"""
        result = self.wait_system.for_stable_screen(timeout, stability_duration)
        if not result.success:
            if result.timeout:
                raise WaitTimeoutError("Screen to be stable",
                                     timeout or self.wait_system.default_timeout,
                                     result.attempts)
            else:
                raise Exception(f"Screen stability check failed: {result.error}")
        return True
    
    def element_to_be_clickable(self, text: str,
                              timeout: Optional[float] = None,
                              confidence: float = 0.8,
                              stability_duration: float = 0.5,
                              use_accessibility: bool = True):
        """Assert that an element becomes clickable within timeout"""
        result = self.wait_system.for_clickable(text, timeout, confidence, stability_duration, use_accessibility)
        if not result.success:
            if result.timeout:
                raise WaitTimeoutError(f"Element '{text}' to be clickable",
                                     timeout or self.wait_system.default_timeout,
                                     result.attempts)
            else:
                raise Exception(f"Failed to find clickable element '{text}': {result.error}")
        return result.value
    
    def element_to_disappear(self, text: str,
                           timeout: Optional[float] = None,
                           confidence: float = 0.8,
                           use_accessibility: bool = True):
        """Assert that an element disappears within timeout"""
        result = self.wait_system.for_element_to_disappear(text, timeout, confidence, use_accessibility)
        if not result.success:
            if result.timeout:
                raise WaitTimeoutError(f"Element '{text}' to disappear",
                                     timeout or self.wait_system.default_timeout,
                                     result.attempts)
            else:
                raise Exception(f"Element '{text}' disappearance check failed: {result.error}")
        return True
