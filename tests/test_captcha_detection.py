"""
Tests for CAPTCHA detection functionality.

These tests verify real detection behavior without tautological mocks.
They test at appropriate layers to enable future refactoring.
"""

import pytest
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "python_sdk"))

from captcha_solver import CaptchaDetector, CaptchaChallenge


class TestCaptchaDetector:
    """Test CAPTCHA detection with real images and scenarios"""
    
    @pytest.fixture
    def detector(self):
        """Create a detector instance for testing"""
        return CaptchaDetector()
    
    @pytest.fixture
    def sample_text_captcha(self):
        """Create a realistic text-based CAPTCHA image"""
        # Create image with CAPTCHA-like text
        img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw distorted text
        try:
            # Try to use system font, fallback to default
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 30), "VERIFY HUMAN", fill='black', font=font)
        draw.text((50, 60), "Enter code: ABC123", fill='blue', font=font)
        
        # Convert to numpy array
        return np.array(img)
    
    @pytest.fixture
    def sample_grid_captcha(self):
        """Create a realistic grid-based CAPTCHA image"""
        img = np.zeros((300, 300, 3), dtype=np.uint8)
        img.fill(240)  # Light gray background
        
        # Draw grid lines (common in image selection CAPTCHAs)
        for i in range(4):
            # Vertical lines
            cv2.line(img, (i * 75, 0), (i * 75, 300), (0, 0, 0), 2)
            # Horizontal lines
            cv2.line(img, (0, i * 75), (300, i * 75), (0, 0, 0), 2)
        
        # Add some colored rectangles (simulating images)
        cv2.rectangle(img, (10, 10), (65, 65), (255, 0, 0), -1)
        cv2.rectangle(img, (85, 10), (140, 65), (0, 255, 0), -1)
        cv2.rectangle(img, (160, 10), (215, 65), (0, 0, 255), -1)
        
        return img
    
    @pytest.fixture
    def normal_webpage(self):
        """Create a normal webpage screenshot without CAPTCHA"""
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add normal webpage elements
        draw.rectangle([50, 50, 750, 100], fill='lightblue', outline='blue')
        draw.text((60, 65), "Welcome to Our Website", fill='darkblue')
        
        draw.rectangle([50, 150, 300, 180], fill='lightgray', outline='gray')
        draw.text((60, 160), "Username", fill='black')
        
        draw.rectangle([50, 200, 300, 230], fill='lightgray', outline='gray')
        draw.text((60, 210), "Password", fill='black')
        
        return np.array(img)

    def test_detect_text_based_captcha(self, detector, sample_text_captcha):
        """Test detection of text-based CAPTCHAs using OCR"""
        result = detector.detect_captcha(sample_text_captcha)
        
        assert result is not None, "Should detect text-based CAPTCHA"
        assert isinstance(result, CaptchaChallenge)
        assert result.challenge_type == "text_based"
        assert result.confidence > 0.5
        assert result.bbox is not None
        assert len(result.bbox) == 4  # x, y, width, height
    
    def test_detect_grid_pattern_captcha(self, detector, sample_grid_captcha):
        """Test detection of grid-based CAPTCHAs using pattern recognition"""
        result = detector.detect_captcha(sample_grid_captcha)
        
        assert result is not None, "Should detect grid pattern CAPTCHA"
        assert result.challenge_type == "grid_pattern"
        assert result.confidence > 0.4  # Lower threshold for pattern detection
        assert result.image is not None
    
    def test_no_false_positive_on_normal_page(self, detector, normal_webpage):
        """Test that normal webpages don't trigger false CAPTCHA detection"""
        result = detector.detect_captcha(normal_webpage)
        
        # Should not detect CAPTCHA on normal webpage
        assert result is None, "Should not detect CAPTCHA on normal webpage"
    
    def test_detection_with_grayscale_input(self, detector, sample_text_captcha):
        """Test that detector works with both color and grayscale images"""
        # Convert to grayscale
        gray_image = cv2.cvtColor(sample_text_captcha, cv2.COLOR_RGB2GRAY)
        
        result = detector.detect_captcha(gray_image)
        
        assert result is not None, "Should detect CAPTCHA in grayscale image"
        assert result.challenge_type == "text_based"
    
    def test_template_matching_with_real_template(self, detector):
        """Test template matching with actual template files"""
        # Create a mock template directory structure
        template_dir = Path(detector._load_captcha_templates.__globals__['Path'](__file__).parent / "templates" / "captcha")
        
        if not template_dir.exists():
            # If no templates exist, this test should gracefully handle it
            result = detector._detect_by_template(np.zeros((100, 100, 3), dtype=np.uint8))
            assert result is None, "Should return None when no templates available"
        else:
            # If templates exist, test with them
            test_image = np.zeros((200, 200, 3), dtype=np.uint8)
            result = detector._detect_by_template(test_image)
            # Result could be None (no match) or a CaptchaChallenge (match found)
            if result is not None:
                assert isinstance(result, CaptchaChallenge)
                assert result.confidence > 0.5
    
    def test_bbox_coordinates_are_valid(self, detector, sample_text_captcha):
        """Test that detected bounding boxes have valid coordinates"""
        result = detector.detect_captcha(sample_text_captcha)
        
        if result is not None:
            x, y, width, height = result.bbox
            
            # Coordinates should be non-negative
            assert x >= 0, "X coordinate should be non-negative"
            assert y >= 0, "Y coordinate should be non-negative"
            assert width > 0, "Width should be positive"
            assert height > 0, "Height should be positive"
            
            # Coordinates should be within image bounds
            img_height, img_width = sample_text_captcha.shape[:2]
            assert x + width <= img_width, "Bounding box should not exceed image width"
            assert y + height <= img_height, "Bounding box should not exceed image height"
    
    def test_challenge_image_extraction(self, detector, sample_text_captcha):
        """Test that extracted challenge images are valid"""
        result = detector.detect_captcha(sample_text_captcha)
        
        if result is not None:
            # Challenge image should be valid numpy array
            assert isinstance(result.image, np.ndarray)
            assert len(result.image.shape) >= 2  # At least 2D array
            assert result.image.size > 0, "Challenge image should not be empty"
            
            # Image dimensions should match bbox if it's a cropped region
            if result.challenge_type != "text_based":  # text_based returns full image
                expected_height = result.bbox[3]
                expected_width = result.bbox[2]
                actual_height, actual_width = result.image.shape[:2]
                
                # Allow some padding tolerance
                assert abs(actual_height - expected_height) <= 40, "Height should roughly match bbox"
                assert abs(actual_width - expected_width) <= 40, "Width should roughly match bbox"


class TestCaptchaDetectionRobustness:
    """Test robustness and edge cases in CAPTCHA detection"""
    
    @pytest.fixture
    def detector(self):
        return CaptchaDetector()
    
    def test_empty_image_handling(self, detector):
        """Test handling of empty or invalid images"""
        # Empty array
        empty_img = np.array([])
        result = detector.detect_captcha(empty_img)
        # Should handle gracefully without crashing
        
        # Very small image
        tiny_img = np.ones((1, 1, 3), dtype=np.uint8)
        result = detector.detect_captcha(tiny_img)
        # Should handle gracefully
    
    def test_very_large_image_handling(self, detector):
        """Test performance with large images"""
        # Create a large image (simulating high-res screenshot)
        large_img = np.zeros((2000, 2000, 3), dtype=np.uint8)
        large_img.fill(255)  # White background
        
        # Add some CAPTCHA-like text in the center
        cv2.putText(large_img, "CAPTCHA", (900, 1000), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        
        # Should complete in reasonable time
        import time
        start_time = time.time()
        result = detector.detect_captcha(large_img)
        duration = time.time() - start_time
        
        assert duration < 5.0, "Detection should complete within 5 seconds for large images"
    
    def test_noise_resistance(self, detector):
        """Test detection works with noisy images"""
        # Create image with CAPTCHA text
        img = np.ones((200, 300, 3), dtype=np.uint8) * 255
        cv2.putText(img, "VERIFY HUMAN", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # Add random noise
        noise = np.random.randint(0, 50, img.shape, dtype=np.uint8)
        noisy_img = cv2.add(img, noise)
        
        result = detector.detect_captcha(noisy_img)
        
        # Should still detect despite noise
        if result is not None:
            assert result.confidence > 0.3, "Should maintain reasonable confidence despite noise"
    
    def test_multiple_detection_methods_consistency(self, detector):
        """Test that different detection methods can work together"""
        # Create image that might trigger multiple detection methods
        img = np.ones((300, 400, 3), dtype=np.uint8) * 240
        
        # Add grid lines (pattern detection)
        for i in range(4):
            cv2.line(img, (i * 100, 0), (i * 100, 300), (0, 0, 0), 2)
            
        # Add CAPTCHA text (OCR detection)
        cv2.putText(img, "Select all cars", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        
        result = detector.detect_captcha(img)
        
        # Should detect using one of the methods
        assert result is not None, "Should detect CAPTCHA using available methods"
        assert result.challenge_type in ["text_based", "grid_pattern"], "Should use valid detection method"


@pytest.mark.integration
class TestCaptchaDetectionIntegration:
    """Integration tests for CAPTCHA detection with real scenarios"""
    
    def test_detection_with_real_screenshot_simulation(self):
        """Test detection with realistic browser screenshot simulation"""
        # Create a realistic browser window simulation
        browser_img = np.ones((768, 1024, 3), dtype=np.uint8) * 255
        
        # Add browser chrome
        cv2.rectangle(browser_img, (0, 0), (1024, 60), (200, 200, 200), -1)  # Address bar
        cv2.putText(browser_img, "https://example.com", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Add page content
        cv2.rectangle(browser_img, (100, 100), (900, 600), (240, 240, 240), -1)  # Content area
        
        # Add CAPTCHA in content area
        cv2.rectangle(browser_img, (300, 250), (700, 450), (255, 255, 255), -1)  # CAPTCHA container
        cv2.rectangle(browser_img, (300, 250), (700, 450), (0, 0, 0), 2)  # CAPTCHA border
        cv2.putText(browser_img, "I'm not a robot", (350, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.rectangle(browser_img, (320, 320), (350, 350), (255, 255, 255), -1)  # Checkbox
        cv2.rectangle(browser_img, (320, 320), (350, 350), (0, 0, 0), 2)  # Checkbox border
        
        detector = CaptchaDetector()
        result = detector.detect_captcha(browser_img)
        
        assert result is not None, "Should detect CAPTCHA in realistic browser simulation"
        
        # CAPTCHA should be detected in the content area, not in browser chrome
        x, y, w, h = result.bbox
        assert y > 60, "CAPTCHA should be detected below browser chrome"
        assert x > 50, "CAPTCHA should be within content margins"
    
    def test_performance_benchmarking(self):
        """Benchmark detection performance for performance regression testing"""
        detector = CaptchaDetector()
        
        # Create test images of different sizes
        test_images = [
            np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),   # Small
            np.random.randint(0, 255, (768, 1024, 3), dtype=np.uint8),  # Medium 
            np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8), # Large
        ]
        
        import time
        performance_results = []
        
        for i, img in enumerate(test_images):
            start_time = time.time()
            result = detector.detect_captcha(img)
            duration = time.time() - start_time
            performance_results.append(duration)
        
        # Performance assertions (these create performance regression tests)
        assert performance_results[0] < 1.0, "Small image detection should be under 1 second"
        assert performance_results[1] < 2.0, "Medium image detection should be under 2 seconds"
        assert performance_results[2] < 5.0, "Large image detection should be under 5 seconds"
        
        # Ensure performance scales reasonably with image size
        assert performance_results[1] > performance_results[0], "Larger images should take more time"
