#!/usr/bin/env python3
"""
Visual Debugging and Template Matching Guide - BrowserGeist

Comprehensive guide to visual automation with BrowserGeist:
- Template matching with confidence levels
- Multi-scale template detection
- Screenshot capture and analysis
- Visual debugging techniques
- OCR text detection
- Creating and managing template libraries
- Troubleshooting vision system issues

This example provides practical guidance for visual automation debugging.
"""

import sys
import os
import time
from pathlib import Path
from typing import Optional, List, Tuple

# Add SDK to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'python_sdk'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'vision'))

from browsergeist import HumanMouse, target, MotionProfiles
from template_matcher import TemplateMatcher, VisionCache

class VisualDebugger:
    """
    Comprehensive visual debugging tool for BrowserGeist automation.
    """
    
    def __init__(self):
        self.bot = None
        self.matcher = TemplateMatcher()
        self.cache = VisionCache()
        self.debug_dir = Path("debug_screenshots")
        self.debug_dir.mkdir(exist_ok=True)
        
    def __enter__(self):
        """Context manager entry"""
        self.bot = HumanMouse()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.bot:
            self.bot.close()
    
    def capture_and_save_screenshot(self, filename: str = None) -> Optional[str]:
        """
        Capture current screen and save for analysis.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to saved screenshot file
        """
        try:
            print("📸 Capturing screenshot...")
            
            # Take screenshot using daemon
            result = self.bot._send_command({"action": "screenshot"})
            
            if not result.success:
                print(f"❌ Screenshot failed: {result.error_message}")
                return None
            
            # Generate filename if not provided
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            # Save screenshot
            screenshot_path = self.debug_dir / filename
            
            import base64
            screenshot_data = result.data.get("image")
            if screenshot_data:
                image_bytes = base64.b64decode(screenshot_data)
                with open(screenshot_path, "wb") as f:
                    f.write(image_bytes)
                
                print(f"✅ Screenshot saved: {screenshot_path}")
                return str(screenshot_path)
            else:
                print("❌ No screenshot data received")
                return None
                
        except Exception as e:
            print(f"❌ Screenshot capture failed: {e}")
            return None
    
    def analyze_template_matching(self, template_path: str, confidence_levels: List[float] = None) -> None:
        """
        Analyze template matching at different confidence levels.
        
        Args:
            template_path: Path to template image
            confidence_levels: List of confidence levels to test
        """
        if confidence_levels is None:
            confidence_levels = [0.9, 0.8, 0.7, 0.6, 0.5]
        
        print(f"🔍 Analyzing template matching for: {template_path}")
        print("-" * 60)
        
        if not Path(template_path).exists():
            print(f"❌ Template file not found: {template_path}")
            return
        
        # Capture current screenshot
        screenshot_path = self.capture_and_save_screenshot("analysis_screenshot.png")
        if not screenshot_path:
            return
        
        import cv2
        screenshot = cv2.imread(screenshot_path)
        template = cv2.imread(template_path)
        
        if screenshot is None or template is None:
            print("❌ Could not load screenshot or template")
            return
        
        print(f"📊 Screenshot: {screenshot.shape[1]}x{screenshot.shape[0]}")
        print(f"📊 Template: {template.shape[1]}x{template.shape[0]}")
        print()
        
        # Test different confidence levels
        for confidence in confidence_levels:
            print(f"🎯 Testing confidence level: {confidence}")
            
            try:
                result = self.matcher.find_template(
                    screenshot, template, confidence=confidence
                )
                
                if result:
                    print(f"   ✅ Match found at ({result.center[0]}, {result.center[1]})")
                    print(f"   📊 Confidence: {result.confidence:.3f}")
                    print(f"   📊 Method: {result.method_used}")
                    if hasattr(result, 'scale_factor'):
                        print(f"   📊 Scale: {result.scale_factor:.2f}x")
                else:
                    print(f"   ❌ No match found")
                
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
            
            print()
    
    def test_multi_scale_detection(self, template_path: str) -> None:
        """
        Test multi-scale template detection.
        
        Args:
            template_path: Path to template image
        """
        print(f"🔬 Multi-Scale Detection Test: {template_path}")
        print("-" * 60)
        
        screenshot_path = self.capture_and_save_screenshot("multiscale_screenshot.png")
        if not screenshot_path:
            return
        
        import cv2
        screenshot = cv2.imread(screenshot_path)
        template = cv2.imread(template_path)
        
        if screenshot is None or template is None:
            print("❌ Could not load images")
            return
        
        # Test different scale factors
        scale_factors = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        
        for scale in scale_factors:
            print(f"🔍 Testing scale factor: {scale:.2f}x")
            
            # Resize template
            new_width = int(template.shape[1] * scale)
            new_height = int(template.shape[0] * scale)
            
            if new_width < 10 or new_height < 10:
                print("   ⚠️  Template too small, skipping")
                continue
            
            if new_width > screenshot.shape[1] or new_height > screenshot.shape[0]:
                print("   ⚠️  Template too large, skipping")
                continue
            
            scaled_template = cv2.resize(template, (new_width, new_height))
            
            try:
                result = self.matcher.find_template(
                    screenshot, scaled_template, confidence=0.7
                )
                
                if result:
                    print(f"   ✅ Match found: confidence {result.confidence:.3f}")
                else:
                    print(f"   ❌ No match")
                    
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
        
        print()
    
    def create_template_from_region(self, name: str, x: int, y: int, width: int, height: int) -> str:
        """
        Create a template by capturing a screen region.
        
        Args:
            name: Template name
            x, y: Top-left coordinates
            width, height: Region dimensions
            
        Returns:
            Path to created template file
        """
        print(f"✂️  Creating template '{name}' from region ({x}, {y}, {width}, {height})")
        
        # Capture full screenshot
        screenshot_path = self.capture_and_save_screenshot("full_capture.png")
        if not screenshot_path:
            return None
        
        try:
            import cv2
            screenshot = cv2.imread(screenshot_path)
            
            # Extract region
            region = screenshot[y:y+height, x:x+width]
            
            # Save as template
            template_dir = Path("templates")
            template_dir.mkdir(exist_ok=True)
            template_path = template_dir / f"{name}.png"
            
            cv2.imwrite(str(template_path), region)
            
            print(f"✅ Template created: {template_path}")
            print(f"📊 Size: {width}x{height}")
            
            # Clean up full screenshot
            os.remove(screenshot_path)
            
            return str(template_path)
            
        except Exception as e:
            print(f"❌ Template creation failed: {e}")
            return None
    
    def guided_template_creation(self) -> None:
        """
        Interactive template creation process.
        """
        print("🎯 Guided Template Creation")
        print("-" * 40)
        print()
        print("This tool helps you create templates for automation.")
        print("1. Position your cursor over the element you want to capture")
        print("2. Press Enter when ready")
        print("3. Click and drag to select the region")
        print()
        
        input("Press Enter when your cursor is positioned over the target element...")
        
        print("\n📍 Step 1: Click the top-left corner of the element")
        
        # Wait for user to click top-left
        print("   Waiting for click...")
        # Capture actual mouse coordinates using system events
        
        import Quartz
        
        # Get current mouse position for top-left
        mouse_pos_1 = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
        x1, y1 = int(mouse_pos_1.x), int(mouse_pos_1.y)
        
        print(f"   Captured top-left: ({x1}, {y1})")
        print("📍 Step 2: Click the bottom-right corner of the element")
        print("   Move to bottom-right and click...")
        
        input("Press Enter when positioned at bottom-right...")
        
        # Get current mouse position for bottom-right
        mouse_pos_2 = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
        x2, y2 = int(mouse_pos_2.x), int(mouse_pos_2.y)
        
        width = x2 - x1
        height = y2 - y1
        
        print(f"\n📐 Captured region: {width}x{height} at ({x1}, {y1})")
        
        # Get template name
        template_name = input("Enter template name: ").strip()
        if not template_name:
            template_name = "custom_template"
        
        # Create template
        template_path = self.create_template_from_region(
            template_name, x1, y1, width, height
        )
        
        if template_path:
            # Test the new template
            print(f"\n🧪 Testing new template...")
            time.sleep(1)  # Brief delay
            self.analyze_template_matching(template_path, [0.8, 0.7, 0.6])
    
    def debug_template_matching_failures(self, template_path: str) -> None:
        """
        Debug why template matching might be failing.
        
        Args:
            template_path: Path to problematic template
        """
        print(f"🔧 Debugging Template Matching Failures")
        print(f"Template: {template_path}")
        print("-" * 60)
        
        if not Path(template_path).exists():
            print(f"❌ Template file not found: {template_path}")
            return
        
        screenshot_path = self.capture_and_save_screenshot("debug_screenshot.png")
        if not screenshot_path:
            return
        
        import cv2
        screenshot = cv2.imread(screenshot_path)
        template = cv2.imread(template_path)
        
        # Check image properties
        print("📊 Image Analysis:")
        print(f"   Screenshot: {screenshot.shape}")
        print(f"   Template: {template.shape}")
        print()
        
        # Check if template is larger than screenshot
        if template.shape[0] > screenshot.shape[0] or template.shape[1] > screenshot.shape[1]:
            print("⚠️  WARNING: Template is larger than screenshot!")
            print("   Solution: Use multi-scale detection or smaller template")
            print()
        
        # Test different matching methods
        methods = [
            (cv2.TM_CCOEFF_NORMED, "TM_CCOEFF_NORMED"),
            (cv2.TM_CCORR_NORMED, "TM_CCORR_NORMED"),
            (cv2.TM_SQDIFF_NORMED, "TM_SQDIFF_NORMED")
        ]
        
        print("🔬 Testing Different Matching Methods:")
        for method, method_name in methods:
            try:
                result = cv2.matchTemplate(screenshot, template, method)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if method == cv2.TM_SQDIFF_NORMED:
                    best_match = min_val
                    print(f"   {method_name}: {best_match:.3f} (lower is better)")
                else:
                    best_match = max_val
                    print(f"   {method_name}: {best_match:.3f} (higher is better)")
                    
            except Exception as e:
                print(f"   {method_name}: Error - {e}")
        
        print()
        
        # Check color space
        print("🎨 Color Analysis:")
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        screenshot_mean = screenshot_gray.mean()
        template_mean = template_gray.mean()
        
        print(f"   Screenshot brightness: {screenshot_mean:.1f}")
        print(f"   Template brightness: {template_mean:.1f}")
        print(f"   Brightness difference: {abs(screenshot_mean - template_mean):.1f}")
        
        if abs(screenshot_mean - template_mean) > 50:
            print("   ⚠️  Large brightness difference detected!")
            print("   Solution: Try adjusting template or use edge detection")
        
        print()
        
        # Suggestions
        print("💡 Troubleshooting Suggestions:")
        print("   1. Lower confidence threshold (try 0.6 or 0.5)")
        print("   2. Use multi-scale detection")
        print("   3. Ensure template is from same screen resolution")
        print("   4. Check if UI element has changed appearance")
        print("   5. Try capturing a larger region around the element")
        print("   6. Use edge detection for shape-based matching")
    
    def validate_template_library(self, templates_dir: str = "templates") -> None:
        """
        Validate all templates in the template library.
        
        Args:
            templates_dir: Directory containing template images
        """
        print("📚 Template Library Validation")
        print("-" * 40)
        
        templates_path = Path(templates_dir)
        if not templates_path.exists():
            print(f"❌ Template directory not found: {templates_dir}")
            return
        
        # Find all image files
        template_files = []
        for ext in ["*.png", "*.jpg", "*.jpeg"]:
            template_files.extend(templates_path.glob(ext))
        
        if not template_files:
            print(f"📁 No template files found in {templates_dir}")
            return
        
        print(f"📁 Found {len(template_files)} template files")
        print()
        
        # Test each template
        screenshot_path = self.capture_and_save_screenshot("validation_screenshot.png")
        if not screenshot_path:
            return
        
        import cv2
        screenshot = cv2.imread(screenshot_path)
        
        results = []
        
        for template_file in template_files:
            print(f"🧪 Testing: {template_file.name}")
            
            try:
                template = cv2.imread(str(template_file))
                if template is None:
                    print(f"   ❌ Could not load template")
                    results.append({"name": template_file.name, "status": "load_error"})
                    continue
                
                # Test at multiple confidence levels
                found_at_confidence = None
                for confidence in [0.8, 0.7, 0.6, 0.5]:
                    result = self.matcher.find_template(
                        screenshot, template, confidence=confidence
                    )
                    if result:
                        found_at_confidence = confidence
                        break
                
                if found_at_confidence:
                    print(f"   ✅ Found at confidence {found_at_confidence}")
                    results.append({
                        "name": template_file.name, 
                        "status": "found",
                        "confidence": found_at_confidence
                    })
                else:
                    print(f"   ❌ Not found")
                    results.append({"name": template_file.name, "status": "not_found"})
                    
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
                results.append({"name": template_file.name, "status": "error"})
        
        # Summary
        print(f"\n📊 Validation Summary:")
        status_counts = {}
        for result in results:
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            print(f"   {status}: {count} templates")

def demo_screenshot_capture():
    """Demonstrate screenshot capture and analysis"""
    print("📸 Screenshot Capture Demo")
    print("-" * 40)
    
    with VisualDebugger() as debugger:
        # Capture and save screenshot
        screenshot_path = debugger.capture_and_save_screenshot("demo_screenshot.png")
        
        if screenshot_path:
            print("✅ Screenshot captured successfully!")
            print(f"   Saved to: {screenshot_path}")
            print("   You can open this file to see what BrowserGeist sees")
        else:
            print("❌ Screenshot capture failed")

def demo_template_analysis():
    """Demonstrate template matching analysis"""
    print("\n🔍 Template Matching Analysis Demo")
    print("-" * 40)
    
    # Create a demo template (in real usage, you'd have actual templates)
    demo_template_path = "examples/assets/demo_button.png"
    
    with VisualDebugger() as debugger:
        if Path(demo_template_path).exists():
            debugger.analyze_template_matching(demo_template_path)
            debugger.test_multi_scale_detection(demo_template_path)
            debugger.debug_template_matching_failures(demo_template_path)
        else:
            print(f"💡 Demo template not found: {demo_template_path}")
            print("   Create templates using the guided creation tool")

def demo_template_creation():
    """Demonstrate interactive template creation"""
    print("\n✂️  Template Creation Demo")
    print("-" * 40)
    
    with VisualDebugger() as debugger:
        # For demo purposes, create a simple template
        template_path = debugger.create_template_from_region(
            "demo_region", 300, 200, 200, 100
        )
        
        if template_path:
            print("✅ Demo template created!")
            # Test the newly created template
            debugger.analyze_template_matching(template_path, [0.7, 0.6, 0.5])

def demo_library_validation():
    """Demonstrate template library validation"""
    print("\n📚 Template Library Validation Demo")
    print("-" * 40)
    
    with VisualDebugger() as debugger:
        debugger.validate_template_library("examples/assets")

def main():
    """Run all visual debugging demonstrations"""
    print("👁️  BrowserGeist - Visual Debugging and Template Matching Guide")
    print("=" * 80)
    print()
    print("This comprehensive guide covers visual automation debugging:")
    print("• Screenshot capture and analysis")
    print("• Template matching with confidence analysis")
    print("• Multi-scale detection testing")
    print("• Interactive template creation")
    print("• Template library management")
    print("• Troubleshooting matching failures")
    print()
    
    try:
        demo_screenshot_capture()
        demo_template_analysis()
        demo_template_creation()
        demo_library_validation()
        
        print("\n🎉 All visual debugging demos completed!")
        print("\n💡 Visual Automation Best Practices:")
        print("   • Start with confidence level 0.8, reduce if needed")
        print("   • Use multi-scale detection for different screen sizes")
        print("   • Capture templates from actual target environment")
        print("   • Keep templates updated when UI changes")
        print("   • Use larger regions for more reliable matching")
        print("   • Test templates regularly to ensure they still work")
        
        print("\n🔧 Debugging Workflow:")
        print("   1. Capture current screenshot")
        print("   2. Test template at different confidence levels")
        print("   3. Try multi-scale detection if size varies")
        print("   4. Check image properties and brightness")
        print("   5. Create new template if UI has changed")
        print("   6. Validate entire template library periodically")
        
        print("\n📁 Generated Files:")
        print("   • Screenshots saved to: debug_screenshots/")
        print("   • Templates saved to: templates/")
        print("   • Use these for debugging and automation")
        
    except ConnectionError:
        print("❌ Connection failed: BrowserGeist daemon not running")
        print("\n🔧 To fix this:")
        print("   1. Start the daemon: ./bin/browsergeist daemon start")
        print("   2. Check permissions: ./bin/browsergeist doctor")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        print("Run './bin/browsergeist doctor' to diagnose issues")

if __name__ == "__main__":
    main()
