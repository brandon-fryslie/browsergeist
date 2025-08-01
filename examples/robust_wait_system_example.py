#!/usr/bin/env python3
"""
BrowserGeist Robust Wait System Example

Demonstrates the comprehensive waiting mechanisms and safe interaction methods
for reliable browser automation.
"""

import time
import sys
import os

# Add the SDK path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'python_sdk'))

from browsergeist import HumanMouse, MotionProfiles
from wait_conditions import WaitTimeoutError


def demonstrate_wait_system():
    """Demonstrate various wait conditions and safe interactions"""
    
    print("🚀 BrowserGeist Robust Wait System Demo")
    print("=" * 50)
    
    # Initialize with a natural persona for realistic behavior
    with HumanMouse(persona="tech_professional") as bot:
        print("✅ Connected to BrowserGeist daemon")
        
        # Example 1: Basic element waiting
        print("\n📍 Example 1: Waiting for page elements")
        try:
            # Wait for a page to be ready
            print("⏳ Waiting for page to stabilize...")
            bot.wait_for_page_load(timeout=10.0, stability_duration=2.0)
            print("✅ Page is stable and ready")
            
            # Wait for specific text to appear
            print("⏳ Waiting for 'Sign In' button...")
            result = bot.wait.for_text("Sign In", timeout=15.0)
            if result.success:
                print(f"✅ Found 'Sign In' text at {result.value.center}")
            else:
                print("❌ 'Sign In' not found within timeout")
                
        except WaitTimeoutError as e:
            print(f"❌ Timeout: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Example 2: Safe clicking with automatic waiting
        print("\n📍 Example 2: Safe interactions with automatic waiting")
        try:
            # Safe click - waits for element before clicking
            print("⏳ Safely clicking 'Login' button...")
            result = bot.safe_click_text("Login", timeout=10.0)
            print("✅ Successfully clicked login button")
            
            # Wait for clickable element (stable and visible)
            print("⏳ Waiting for 'Submit' to be clickable...")
            coords = bot.expect.element_to_be_clickable("Submit", timeout=10.0)
            print(f"✅ Submit button is clickable at {coords}")
            
        except WaitTimeoutError as e:
            print(f"❌ Element not ready: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Example 3: Form filling with safety checks
        print("\n📍 Example 3: Safe form interactions")
        try:
            # Safe form field typing
            print("⏳ Safely typing in email field...")
            bot.safe_type_in_field(
                field_text="Email", 
                content="user@example.com",
                timeout=10.0,
                clear_field=True
            )
            print("✅ Email field filled successfully")
            
            print("⏳ Safely typing in password field...")
            bot.safe_type_in_field(
                field_text="Password",
                content="securepassword123",
                timeout=10.0,
                delay_profile="careful"  # Slower typing for passwords
            )
            print("✅ Password field filled successfully")
            
        except WaitTimeoutError as e:
            print(f"❌ Field not ready: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Example 4: Multiple conditions and complex waiting
        print("\n📍 Example 4: Complex wait conditions")
        try:
            from wait_conditions import ElementVisibleCondition, TextVisibleCondition, MultipleCondition
            
            # Wait for multiple elements (OR logic)
            print("⏳ Waiting for either 'Login' or 'Sign In'...")
            conditions = [
                ElementVisibleCondition("Login"),
                ElementVisibleCondition("Sign In")
            ]
            result = bot.wait.for_any(conditions, timeout=10.0)
            if result.success:
                print("✅ Found one of the login elements")
            
            # Wait for form to be complete (AND logic)
            print("⏳ Waiting for form to be complete...")
            form_conditions = [
                TextVisibleCondition("Email"),
                TextVisibleCondition("Password"),
                TextVisibleCondition("Submit")
            ]
            result = bot.wait.for_all(form_conditions, timeout=15.0)
            if result.success:
                print("✅ Complete form is visible")
                
        except WaitTimeoutError as e:
            print(f"❌ Complex condition timeout: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Example 5: Element state changes
        print("\n📍 Example 5: Waiting for element state changes")
        try:
            # Wait for loading indicator to disappear
            print("⏳ Waiting for loading indicator to disappear...")
            result = bot.wait.for_element_to_disappear("Loading...", timeout=30.0)
            if result.success:
                print("✅ Loading completed")
            
            # Expect specific text to appear after action
            print("⏳ Expecting 'Welcome' message after login...")
            bot.expect.text_to_be_visible("Welcome", timeout=20.0)
            print("✅ Welcome message appeared")
            
        except WaitTimeoutError as e:
            print(f"❌ State change timeout: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Example 6: Custom wait conditions
        print("\n📍 Example 6: Custom wait conditions")
        try:
            # Custom condition function
            def page_has_loaded(bot):
                """Custom condition: check if page has specific elements"""
                screenshot = bot._take_screenshot()
                if screenshot is None:
                    return False
                
                # Check for multiple indicators of a loaded page
                has_header = bot.vision.find_text(screenshot, "Header") is not None
                has_footer = bot.vision.find_text(screenshot, "Footer") is not None
                has_nav = bot.vision.find_text(screenshot, "Navigation") is not None
                
                return has_header and (has_footer or has_nav)
            
            print("⏳ Waiting for custom page load condition...")
            result = bot.wait.for_condition(
                page_has_loaded, 
                "page to have header and navigation",
                timeout=15.0
            )
            
            if result.success:
                print("✅ Custom page load condition met")
            else:
                print("❌ Custom condition not met within timeout")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Example 7: Error recovery and fallbacks
        print("\n📍 Example 7: Error recovery with fallbacks")
        try:
            # Try multiple approaches with fallbacks
            login_attempts = [
                ("Login", "button"),
                ("Sign In", "link"), 
                ("Enter", "button"),
                ("Submit", "button")
            ]
            
            for text, element_type in login_attempts:
                try:
                    print(f"⏳ Trying to find {element_type}: '{text}'...")
                    result = bot.wait.for_text(text, timeout=5.0)
                    if result.success:
                        print(f"✅ Found '{text}' {element_type}")
                        # Could click here: bot.safe_click_text(text)
                        break
                except WaitTimeoutError:
                    print(f"❌ '{text}' not found, trying next...")
                    continue
            else:
                print("❌ No login elements found with any fallback")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n🎯 Wait System Demo Complete!")
        print("Key benefits demonstrated:")
        print("• ✅ Automatic waiting prevents premature actions")
        print("• ✅ Multiple wait conditions (visible, clickable, stable)")
        print("• ✅ Safe interaction methods with built-in waiting")
        print("• ✅ Complex conditions with AND/OR logic")
        print("• ✅ Element state change detection")
        print("• ✅ Custom wait conditions")
        print("• ✅ Error recovery and fallback strategies")
        print("• ✅ Timeout handling and clear error messages")


def demonstrate_playwright_inspired_api():
    """Show Playwright-inspired usage patterns"""
    
    print("\n🎭 Playwright-Inspired API Demo")
    print("=" * 40)
    
    with HumanMouse() as bot:
        try:
            # Playwright-style expectations
            print("📝 Using Playwright-style assertions...")
            
            # Expect elements to be in certain states
            bot.expect.element_to_be_visible("Login", timeout=10)
            bot.expect.element_to_be_clickable("Submit", timeout=10)
            bot.expect.screen_to_be_stable(timeout=15)
            
            print("✅ All expectations met!")
            
            # Chain operations with built-in waiting
            print("🔗 Chaining operations safely...")
            bot.safe_click_text("Login")
            bot.wait_for_page_load()
            bot.safe_type_in_field("Username", "testuser")
            bot.safe_type_in_field("Password", "testpass")
            bot.safe_click_text("Submit")
            bot.expect.text_to_be_visible("Welcome")
            
            print("✅ Login flow completed successfully!")
            
        except WaitTimeoutError as e:
            print(f"❌ Assertion failed: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🤖 BrowserGeist Robust Wait System Examples")
    print("=" * 60)
    
    demonstrate_wait_system()
    demonstrate_playwright_inspired_api()
    
    print("\n✨ All demonstrations complete!")
    print("The robust wait system provides:")
    print("• Reliable automation timing")
    print("• Prevention of race conditions")
    print("• Clear error handling")
    print("• Production-ready safety mechanisms")
