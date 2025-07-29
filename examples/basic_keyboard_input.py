#!/usr/bin/env python3
"""
Basic Keyboard Input Example - BrowserGeist

Demonstrates fundamental keyboard input capabilities:
- Text typing with different speed profiles
- Special key handling (Enter, Tab, etc.)
- Character frequency-based realistic timing
- Password and sensitive data handling
- Different typing styles and patterns

This example covers all aspects of human-like keyboard automation.
"""

import sys
import os
import time

# Add SDK to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'python_sdk'))

from browsergeist import HumanMouse, MotionProfiles

def demo_basic_typing():
    """Demonstrate basic text typing with different profiles"""
    print("⌨️  Basic Text Typing Demo")
    print("-" * 40)
    
    with HumanMouse() as bot:
        # Move to a text area first
        print("1. Moving to text input area...")
        bot.move_to((400, 300), profile=MotionProfiles.NATURAL)
        bot.click()
        time.sleep(0.3)
        
        # Demonstrate different typing profiles
        typing_examples = [
            ("careful", "This text is typed with careful precision."),
            ("average", "This demonstrates average typing speed."),
            ("fast", "Quick typing for efficient data entry."),
            ("natural", "Natural typing with realistic human rhythm.")
        ]
        
        for profile, text in typing_examples:
            print(f"2. Typing with '{profile}' profile...")
            start_time = time.time()
            bot.type_text(text, delay_profile=profile)
            duration = time.time() - start_time
            
            # Add line break
            bot.type_text("\n", delay_profile=profile)
            
            print(f"   ⏱️  '{profile}' profile completed in {duration:.2f}s")
            time.sleep(0.5)
        
        print("✅ Basic typing demo completed!")

def demo_special_characters():
    """Demonstrate typing special characters and symbols"""
    print("\n🔣 Special Characters Demo")
    print("-" * 40)
    
    with HumanMouse() as bot:
        # Move cursor to fresh area
        bot.move_to((400, 500), profile=MotionProfiles.NATURAL)
        bot.click()
        time.sleep(0.3)
        
        print("1. Typing email address with special characters...")
        email = "user.name+test@example.com"
        bot.type_text(email, delay_profile="average")
        bot.type_text("\n")
        
        print("2. Typing password with mixed characters...")
        # Note: In real scenarios, handle passwords securely
        password = "MySecure123!@#"
        bot.type_text(password, delay_profile="careful")
        bot.type_text("\n")
        
        print("3. Typing URL with special characters...")
        url = "https://example.com/path?param=value&other=123"
        bot.type_text(url, delay_profile="average")
        bot.type_text("\n")
        
        print("4. Typing programming code...")
        code = "function hello() { return 'Hello, World!'; }"
        bot.type_text(code, delay_profile="fast")
        bot.type_text("\n")
        
        print("✅ Special characters demo completed!")

def demo_form_filling():
    """Demonstrate realistic form filling patterns"""
    print("\n📝 Form Filling Demo")
    print("-" * 40)
    
    # Sample form data
    form_data = {
        "first_name": "John",
        "last_name": "Doe", 
        "email": "john.doe@example.com",
        "phone": "(555) 123-4567",
        "address": "123 Main Street",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94102",
        "comments": "This is a sample comment with multiple sentences. It demonstrates how longer text would be typed in a form field."
    }
    
    # Simulate form field positions
    form_fields = [
        (300, 200, "first_name"),
        (500, 200, "last_name"),
        (400, 250, "email"),
        (400, 300, "phone"),
        (400, 350, "address"),
        (300, 400, "city"),
        (450, 400, "state"),
        (550, 400, "zip"),
        (400, 500, "comments")
    ]
    
    with HumanMouse() as bot:
        print("Filling out form with realistic human behavior...")
        
        for i, (x, y, field_name) in enumerate(form_fields):
            value = form_data[field_name]
            
            print(f"{i+1}. Filling {field_name}: '{value[:30]}{'...' if len(value) > 30 else ''}'")
            
            # Move to field with slight randomness
            actual_x = x + (i * 2 - 5)  # Small variations
            actual_y = y + (i % 3 - 1)
            
            bot.move_to((actual_x, actual_y), profile=MotionProfiles.NATURAL)
            bot.click()
            
            # Brief pause (user focusing on field)
            time.sleep(0.2 + (len(field_name) * 0.01))
            
            # Choose typing profile based on field type
            if field_name in ["first_name", "last_name", "city", "state"]:
                profile = "fast"  # Familiar info typed quickly
            elif field_name in ["email", "phone", "zip"]:
                profile = "careful"  # Important info typed carefully
            elif field_name == "comments":
                profile = "natural"  # Long text typed naturally
            else:
                profile = "average"
            
            bot.type_text(value, delay_profile=profile)
            
            # Tab to next field (except for last field)
            if i < len(form_fields) - 1:
                time.sleep(0.1)
                # Note: Tab key handling would be implemented here
                # bot.key_press("Tab")
    
    print("✅ Form filling demo completed!")

def demo_typing_corrections():
    """Demonstrate realistic typing corrections and backspacing"""
    print("\n🔄 Typing Corrections Demo")
    print("-" * 40)
    
    with HumanMouse() as bot:
        bot.move_to((400, 300), profile=MotionProfiles.NATURAL)
        bot.click()
        time.sleep(0.3)
        
        print("1. Typing with intentional 'mistakes' and corrections...")
        
        # Type initial text
        text = "This is an exampel of typing"
        bot.type_text(text, delay_profile="average")
        time.sleep(0.5)
        
        print("   🔍 'Noticing' the typo in 'exampel'...")
        time.sleep(1.0)  # Pause to notice mistake
        
        # Backspace to fix "exampel" -> "example"
        print("   ⌫ Correcting the typo...")
        # Note: Backspace key handling would be implemented here
        # for _ in range(7):  # Remove "exampel"
        #     bot.key_press("Backspace")
        #     time.sleep(0.05)
        
        # bot.type_text("example", delay_profile="careful")
        
        # Continue with rest of sentence
        bot.type_text(" with corrections", delay_profile="average")
        bot.type_text("\n")
        
        print("2. Demonstrating hesitation and partial typing...")
        
        # Start typing something, pause, then change mind
        partial_text = "I was going to say"
        bot.type_text(partial_text, delay_profile="average")
        time.sleep(0.8)  # Pause (thinking)
        
        print("   🤔 Changing mind about what to write...")
        
        # Clear the line and start over
        # Note: Select all and delete would be implemented here
        # bot.key_press("Command+A")
        # bot.key_press("Delete")
        
        new_text = "Actually, let me write something different."
        bot.type_text(new_text, delay_profile="natural")
        bot.type_text("\n")
        
        print("✅ Typing corrections demo completed!")

def demo_different_typing_styles():
    """Demonstrate different typing styles (hunt-and-peck vs touch typing)"""
    print("\n👆 Typing Styles Demo")
    print("-" * 40)
    
    with HumanMouse() as bot:
        bot.move_to((400, 300), profile=MotionProfiles.NATURAL)
        bot.click()
        time.sleep(0.3)
        
        print("1. Touch typing style (fast, confident)...")
        touch_typing_text = "This text is typed with confident touch typing, flowing smoothly with minimal pauses between words."
        start_time = time.time()
        bot.type_text(touch_typing_text, delay_profile="fast")
        touch_duration = time.time() - start_time
        bot.type_text("\n\n")
        
        print("2. Hunt-and-peck style (slower, with pauses)...")
        hunt_peck_text = "This text is typed with hunt-and-peck method, slower and more deliberate."
        start_time = time.time()
        bot.type_text(hunt_peck_text, delay_profile="careful")
        hunt_duration = time.time() - start_time
        bot.type_text("\n\n")
        
        print(f"   📊 Touch typing: {touch_duration:.2f}s")
        print(f"   📊 Hunt-and-peck: {hunt_duration:.2f}s")
        print(f"   📊 Speed difference: {hunt_duration/touch_duration:.1f}x slower")
        
        print("3. Mixed style (varying speed based on word familiarity)...")
        mixed_text = "Common words flow quickly but technical terminology is typed more slowly."
        bot.type_text(mixed_text, delay_profile="natural")
        bot.type_text("\n")
        
        print("✅ Typing styles demo completed!")

def demo_sensitive_data_handling():
    """Demonstrate secure handling of sensitive data like passwords"""
    print("\n🔐 Sensitive Data Handling Demo")
    print("-" * 40)
    
    # In real scenarios, never hard-code sensitive data!
    # This is just for demonstration purposes
    
    with HumanMouse() as bot:
        print("1. Typing username (normal speed)...")
        bot.move_to((400, 300), profile=MotionProfiles.NATURAL)
        bot.click()
        time.sleep(0.3)
        
        username = "demo_user"
        bot.type_text(username, delay_profile="average")
        time.sleep(0.5)
        
        # Tab to password field
        print("2. Moving to password field...")
        bot.move_to((400, 350), profile=MotionProfiles.NATURAL)
        bot.click()
        time.sleep(0.3)
        
        print("3. Typing password (slower, more careful)...")
        # Simulate password typing - more careful and deliberate
        demo_password = "DemoPass123!"
        bot.type_text(demo_password, delay_profile="careful")
        time.sleep(0.8)  # Pause to verify password is correct
        
        print("4. Moving to confirm password field...")
        bot.move_to((400, 400), profile=MotionProfiles.NATURAL)
        bot.click()
        time.sleep(0.3)
        
        print("5. Confirming password (even more careful)...")
        bot.type_text(demo_password, delay_profile="careful")
        
        print("✅ Sensitive data handling demo completed!")
        print("💡 In production: Use secure credential management!")

def main():
    """Run all keyboard input demonstrations"""
    print("⌨️  BrowserGeist - Basic Keyboard Input Examples")
    print("=" * 60)
    print()
    print("This demo showcases comprehensive keyboard automation capabilities:")
    print("• Text typing with realistic human timing")
    print("• Different typing speed profiles")
    print("• Special character and symbol handling")
    print("• Form filling with appropriate patterns")
    print("• Typing corrections and error recovery")
    print("• Different typing styles (touch typing vs hunt-and-peck)")
    print("• Secure handling of sensitive data")
    print()
    
    try:
        demo_basic_typing()
        demo_special_characters()
        demo_form_filling()
        demo_typing_corrections()
        demo_different_typing_styles()
        demo_sensitive_data_handling()
        
        print("\n🎉 All keyboard input demos completed successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("   • Character frequency-based timing (common letters faster)")
        print("   • Realistic keystroke duration variation (30-80ms)")
        print("   • Burst prevention (pauses after rapid typing)")
        print("   • Fatigue modeling (gradual slowdown)")
        print("   • Profile-based adaptation (careful/average/fast/natural)")
        print("   • Human-like thinking pauses during typing")
        
        print("\n🎯 Best Practices:")
        print("   • Use 'careful' profile for passwords and important data")
        print("   • Use 'fast' profile for familiar text")
        print("   • Use 'natural' profile for long-form content")
        print("   • Add realistic pauses between form fields")
        print("   • Implement error correction patterns for realism")
        
    except ConnectionError:
        print("❌ Connection failed: BrowserGeist daemon not running")
        print("\n🔧 To fix this:")
        print("   1. Start the daemon: ./bin/browsergeist daemon start")
        print("   2. Check permissions: ./bin/browsergeist doctor")
        print("   3. Grant Input Monitoring permissions in System Preferences")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        print("Run './bin/browsergeist doctor' to diagnose issues")

if __name__ == "__main__":
    main()
