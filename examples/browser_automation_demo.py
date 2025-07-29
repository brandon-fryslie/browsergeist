#!/usr/bin/env python3
"""
BrowserGeist Demo - Advanced Browser Automation

This example demonstrates stealth browser automation using
human-like mouse movements and visual target detection.
"""

import sys
import os
import time
import cv2
import numpy as np

# Add SDK to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'python_sdk'))

from browsergeist import HumanMouse, MotionProfiles, target

def main():
    print("🤖 BrowserGeist Demo - Advanced Browser Automation")
    print("=" * 50)
    
    try:
        # Initialize the automation bot
        print("🔗 Connecting to control daemon...")
        bot = HumanMouse()
        print("✅ Connected successfully!")
        
        # Demo 1: Human-like cursor movement
        print("\n📍 Demo 1: Human-like cursor movement")
        print("Moving cursor to center of screen...")
        
        # Move to center of screen with natural motion
        bot.move_to((800, 400), profile=MotionProfiles.NATURAL)
        time.sleep(1)
        
        # Demo 2: Different motion profiles
        print("\n🎯 Demo 2: Motion profile demonstration")
        
        profiles = [
            (MotionProfiles.CAREFUL, "Careful movement"),
            (MotionProfiles.FAST, "Fast movement"),
            (MotionProfiles.NATURAL, "Natural movement")
        ]
        
        for profile, description in profiles:
            print(f"  - {description}")
            bot.move_to((600 + int(100 * np.random.randn()), 
                        300 + int(100 * np.random.randn())), 
                       profile=profile)
            time.sleep(0.5)
        
        # Demo 3: Click simulation
        print("\n🖱️  Demo 3: Human-like clicking")
        bot.click(duration=0.08)  # Slightly longer click
        time.sleep(0.5)
        
        # Demo 4: Text typing
        print("\n⌨️  Demo 4: Human-like typing")
        demo_text = "Hello, world! This is BrowserGeist automation."
        print(f"Typing: '{demo_text}'")
        bot.type(demo_text, delay_profile="natural")
        
        # Demo 5: Scrolling
        print("\n📜 Demo 5: Smooth scrolling")
        print("Performing smooth scroll...")
        bot.scroll(dx=0, dy=100, smooth=True)
        time.sleep(1)
        bot.scroll(dx=0, dy=-100, smooth=True)
        
        print("\n✅ Demo completed successfully!")
        print("\nBrowserGeist features demonstrated:")
        print("  ✓ Human-like mouse movement with physics simulation")
        print("  ✓ Multiple motion profiles (careful, fast, natural)")
        print("  ✓ Realistic click timing and duration")
        print("  ✓ Natural typing with variable delays")
        print("  ✓ Smooth scrolling with momentum")
        print("  ✓ Undetectable Core Graphics event injection")
        
    except ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure the daemon is running: `make daemon`")
        print("2. Check accessibility permissions in System Preferences")
        print("3. Ensure screen recording permissions are granted")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def test_vision_system():
    """Test the vision system independently"""
    print("\n🔍 Testing Vision System...")
    
    try:
        from template_matcher import TemplateMatcher
        
        matcher = TemplateMatcher()
        print("✅ Vision system initialized")
        
        # You could add template images in examples/ to test this
        print("📷 Vision features available:")
        print("  ✓ Template matching with multiple algorithms")
        print("  ✓ SIFT feature-based detection")
        print("  ✓ OCR text recognition (if pytesseract installed)")
        print("  ✓ Multi-scale template detection")
        print("  ✓ Vision caching for performance")
        
    except ImportError as e:
        print(f"⚠️  Vision system not fully available: {e}")
        print("Install missing dependencies: uv pip install opencv-python")

if __name__ == "__main__":
    main()
    test_vision_system()
