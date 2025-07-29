#!/usr/bin/env python3
"""
BrowserGeist CAPTCHA Solving Example

Demonstrates how to use the CAPTCHA solving capabilities:
1. Automatic CAPTCHA detection during automation
2. Manual CAPTCHA solving via webserver
3. OpenAI API integration for automated solving
4. 2Captcha service integration
"""

import os
import sys
import time

# Add the SDK to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'python_sdk'))

from browsergeist import HumanMouse, MotionProfiles
from captcha_solver import CaptchaSolveMethod

def example_basic_captcha_detection():
    """Basic example: Check for CAPTCHA and solve manually if found"""
    print("🚀 Basic CAPTCHA Detection Example")
    print("=" * 50)
    
    # Initialize with manual solving only
    with HumanMouse(auto_solve_captcha=True) as bot:
        print("Checking current screen for CAPTCHA...")
        
        # Check for CAPTCHA on current screen
        solution = bot.check_for_captcha(methods=[CaptchaSolveMethod.MANUAL])
        
        if solution:
            print(f"✅ CAPTCHA solved: {solution.success}")
            if solution.solution:
                print(f"   Text solution: {solution.solution}")
            if solution.coordinates:
                print(f"   Click coordinates: {solution.coordinates}")
        else:
            print("ℹ️ No CAPTCHA detected on current screen")

def example_openai_captcha():
    """Example using OpenAI API for automatic CAPTCHA solving"""
    print("\n🤖 OpenAI CAPTCHA Solving Example")
    print("=" * 50)
    
    # Get API key from environment or user input
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("⚠️ OpenAI API key not found in environment.")
        print("Set OPENAI_API_KEY environment variable or skip this example.")
        return
    
    with HumanMouse(openai_api_key=openai_key, auto_solve_captcha=True) as bot:
        print("Checking for CAPTCHA with OpenAI solving...")
        
        # Try OpenAI first, then manual as fallback
        solution = bot.check_for_captcha(methods=[
            CaptchaSolveMethod.OPENAI, 
            CaptchaSolveMethod.MANUAL
        ])
        
        if solution:
            print(f"✅ CAPTCHA solved using {solution.method_used.value}")
        else:
            print("ℹ️ No CAPTCHA detected")

def example_2captcha_service():
    """Example using 2Captcha service for outsourced solving"""
    print("\n🌐 2Captcha Service Example")
    print("=" * 50)
    
    # Get API key from environment
    twocaptcha_key = os.getenv('TWOCAPTCHA_API_KEY')
    if not twocaptcha_key:
        print("⚠️ 2Captcha API key not found in environment.")
        print("Set TWOCAPTCHA_API_KEY environment variable or skip this example.")
        return
    
    with HumanMouse(twocaptcha_api_key=twocaptcha_key, auto_solve_captcha=True) as bot:
        print("Checking for CAPTCHA with 2Captcha service...")
        
        solution = bot.check_for_captcha(methods=[CaptchaSolveMethod.TWOCAPTCHA])
        
        if solution:
            print(f"✅ CAPTCHA solved using 2Captcha service")
        else:
            print("ℹ️ No CAPTCHA detected")

def example_automation_with_captcha():
    """Complete automation example with automatic CAPTCHA handling"""
    print("\n🎯 Automation with CAPTCHA Handling")
    print("=" * 50)
    
    # Initialize with all solving methods available
    openai_key = os.getenv('OPENAI_API_KEY')
    twocaptcha_key = os.getenv('TWOCAPTCHA_API_KEY')
    
    with HumanMouse(
        openai_api_key=openai_key,
        twocaptcha_api_key=twocaptcha_key,
        auto_solve_captcha=True
    ) as bot:
        
        print("Starting automation with CAPTCHA handling...")
        
        # Example automation workflow
        try:
            # Navigate to a form (this would be real coordinates in practice)
            print("🖱️ Moving to username field...")
            bot.move_to((400, 300), profile=MotionProfiles.NATURAL)
            bot.click()
            
            # Type username
            print("⌨️ Typing username...")
            bot.type("test@example.com", delay_profile="average")
            
            # Move to password field
            print("🖱️ Moving to password field...")
            bot.move_to((400, 350), profile=MotionProfiles.NATURAL)
            bot.click()
            
            # Type password
            print("⌨️ Typing password...")
            bot.type("password123", delay_profile="careful")
            
            # Submit form - this might trigger a CAPTCHA
            print("🖱️ Clicking submit button...")
            bot.move_to((400, 400), profile=MotionProfiles.NATURAL)
            
            # Use CAPTCHA-aware click
            bot.click_with_captcha_handling()
            
            # Wait and check for any CAPTCHAs that appeared
            time.sleep(2)
            captcha_handled = bot.solve_captcha_if_present()
            
            if captcha_handled:
                print("✅ Automation completed successfully!")
            else:
                print("⚠️ Automation may need manual intervention")
                
        except Exception as e:
            print(f"❌ Automation failed: {e}")

def example_manual_webserver():
    """Demonstrate the manual CAPTCHA solving webserver"""
    print("\n🌐 Manual CAPTCHA Webserver Example")
    print("=" * 50)
    
    try:
        from captcha_solver import ManualCaptchaSolver, CaptchaChallenge
        import numpy as np
        
        # Create a mock CAPTCHA challenge for demonstration
        print("Creating demo CAPTCHA challenge...")
        
        # Create a simple test image (normally this would be a real CAPTCHA)
        test_image = np.zeros((100, 200, 3), dtype=np.uint8)
        test_image[:] = (200, 200, 200)  # Light gray background
        
        challenge = CaptchaChallenge(
            image=test_image,
            bbox=(0, 0, 200, 100),
            challenge_type="demo_captcha",
            confidence=1.0
        )
        
        # Start manual solver
        manual_solver = ManualCaptchaSolver(port=8899)
        
        print(f"🌐 Manual CAPTCHA solver webserver starting...")
        print(f"📱 Open http://localhost:8899 to solve CAPTCHAs manually")
        print("💡 This is useful when automation encounters complex CAPTCHAs")
        
        # In a real scenario, this would be called automatically when a CAPTCHA is detected
        print("\nNote: In real usage, the webserver starts automatically when CAPTCHAs are detected")
        print("and provides a user-friendly interface for manual solving.")
        
    except ImportError as e:
        print(f"⚠️ Could not start webserver demo: {e}")
        print("Install Flask to enable manual CAPTCHA solving: pip install flask")

def main():
    """Run all CAPTCHA examples"""
    print("🎯 BrowserGeist CAPTCHA Solving Examples")
    print("=" * 60)
    print()
    print("This script demonstrates the three CAPTCHA solving methods:")
    print("1. 🤖 OpenAI API - Automated solving using GPT-4 Vision")
    print("2. 🌐 Manual Webserver - User solves via web interface")
    print("3. 🔗 2Captcha Service - Outsourced solving service")
    print()
    
    # Check dependencies
    missing_deps = []
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    try:
        import numpy as np
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import PIL
    except ImportError:
        missing_deps.append("Pillow")
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install " + ' '.join(missing_deps))
        return
    
    # Run examples
    try:
        example_basic_captcha_detection()
        example_openai_captcha()
        example_2captcha_service()
        example_automation_with_captcha()
        example_manual_webserver()
        
        print("\n🎉 All CAPTCHA examples completed!")
        print("\n💡 Tips for production use:")
        print("  • Set OPENAI_API_KEY for automated solving")
        print("  • Set TWOCAPTCHA_API_KEY for service-based solving")
        print("  • Manual solving always available as fallback")
        print("  • Use auto_solve_captcha=True for seamless automation")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        print("Make sure the BrowserGeist daemon is running: ./bin/browsergeist-daemon")

if __name__ == "__main__":
    main()
