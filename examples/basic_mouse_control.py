#!/usr/bin/env python3
"""
Basic Mouse Control Example - BrowserGeist

Demonstrates fundamental mouse movement and clicking capabilities:
- Moving to specific coordinates
- Different click types (left, right, middle)
- Motion profiles (Natural, Careful, Fast)
- Human-like timing and randomization

This is a foundational example for understanding BrowserGeist mouse automation.
"""

import sys
import os
import time

# Add SDK to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'python_sdk'))

from browsergeist import HumanMouse, MotionProfiles

def demo_basic_movements():
    """Demonstrate basic mouse movements with different profiles"""
    print("🖱️  Basic Mouse Movement Demo")
    print("-" * 40)
    
    with HumanMouse() as bot:
        # Get current screen dimensions (rough estimates for demo)
        screen_width, screen_height = 1920, 1080
        center_x, center_y = screen_width // 2, screen_height // 2
        
        print("1. Moving to screen center with Natural profile...")
        bot.move_to((center_x, center_y), profile=MotionProfiles.NATURAL)
        time.sleep(1)
        
        print("2. Moving to top-left with Careful profile...")
        bot.move_to((200, 200), profile=MotionProfiles.CAREFUL)
        time.sleep(1)
        
        print("3. Moving to bottom-right with Fast profile...")
        bot.move_to((center_x + 300, center_y + 200), profile=MotionProfiles.FAST)
        time.sleep(1)
        
        print("✅ Movement demo completed!")

def demo_click_types():
    """Demonstrate different types of mouse clicks"""
    print("\n🎯 Mouse Click Types Demo")
    print("-" * 40)
    
    with HumanMouse() as bot:
        # Move to a neutral position
        bot.move_to((400, 300), profile=MotionProfiles.NATURAL)
        
        print("1. Standard left click...")
        bot.click("left", duration=0.05)
        time.sleep(0.5)
        
        print("2. Right click (context menu)...")
        bot.click("right", duration=0.06)
        time.sleep(0.5)
        
        print("3. Longer duration click (button press feel)...")
        bot.click("left", duration=0.12)
        time.sleep(0.5)
        
        print("4. Quick double-click simulation...")
        bot.click("left", duration=0.04)
        time.sleep(0.08)  # Brief pause between clicks
        bot.click("left", duration=0.04)
        time.sleep(0.5)
        
        print("✅ Click demo completed!")

def demo_motion_profiles():
    """Demonstrate the differences between motion profiles"""
    print("\n🏃‍♂️ Motion Profiles Comparison")
    print("-" * 40)
    
    profiles = [
        ("Natural", MotionProfiles.NATURAL, "Realistic human movement with natural curves"),
        ("Careful", MotionProfiles.CAREFUL, "Slow, precise movement for delicate operations"),
        ("Fast", MotionProfiles.FAST, "Quick movement for efficient automation")
    ]
    
    with HumanMouse() as bot:
        start_pos = (300, 300)
        
        for i, (name, profile, description) in enumerate(profiles):
            target_x = 300 + (i * 250)
            target_y = 400
            
            print(f"{i+1}. {name} Profile: {description}")
            
            # Start from same position each time
            bot.move_to(start_pos, profile=MotionProfiles.FAST)
            time.sleep(0.2)
            
            # Time the movement with this profile
            start_time = time.time()
            bot.move_to((target_x, target_y), profile=profile)
            duration = time.time() - start_time
            
            print(f"   ⏱️  Completed in {duration:.3f} seconds")
            time.sleep(1)
    
    print("✅ Profile comparison completed!")

def demo_realistic_interactions():
    """Demonstrate realistic interaction patterns"""
    print("\n🎭 Realistic Interaction Patterns")
    print("-" * 40)
    
    with HumanMouse() as bot:
        print("1. Simulating browsing behavior...")
        
        # Simulate reading a webpage with occasional clicks
        positions = [
            (400, 200, "Article title"),
            (450, 350, "First paragraph"),
            (380, 500, "Interesting link"),
            (600, 450, "Side navigation"),
            (420, 650, "Continue reading button")
        ]
        
        for x, y, description in positions:
            print(f"   👁️  Looking at: {description}")
            
            # Add human-like delay (reading time)
            time.sleep(0.8 + (len(description) * 0.02))  # Reading time based on text length
            
            # Move with slight randomness
            actual_x = x + int((hash(description) % 21) - 10)  # ±10 pixel variation
            actual_y = y + int((hash(description) % 11) - 5)   # ±5 pixel variation
            
            bot.move_to((actual_x, actual_y), profile=MotionProfiles.NATURAL)
            
            # Sometimes click, sometimes just hover
            if "button" in description.lower() or "link" in description.lower():
                print(f"   🖱️  Clicking: {description}")
                bot.click("left")
                time.sleep(0.3)  # Brief pause after action
        
        print("✅ Realistic interaction completed!")

def demo_advanced_timing():
    """Demonstrate advanced timing and hesitation patterns"""
    print("\n⏱️  Advanced Timing Patterns")
    print("-" * 40)
    
    with HumanMouse() as bot:
        print("1. Hesitation before important action...")
        
        # Move towards a "submit" button
        bot.move_to((400, 500), profile=MotionProfiles.NATURAL)
        
        # Pause (user thinking/hesitating)
        print("   🤔 Hesitating before clicking submit...")
        time.sleep(1.2)
        
        # Small adjustment movement (common human behavior)
        bot.move_to((405, 498), profile=MotionProfiles.CAREFUL)
        time.sleep(0.3)
        
        # Final click
        print("   ✅ Deciding to click...")
        bot.click("left", duration=0.08)
        
        print("\n2. Distraction and correction pattern...")
        
        # Start moving toward target
        bot.move_to((600, 300), profile=MotionProfiles.NATURAL)
        time.sleep(0.2)
        
        # "Get distracted" and move elsewhere briefly
        print("   👀 Got distracted by something else...")
        bot.move_to((550, 250), profile=MotionProfiles.FAST)
        time.sleep(0.5)
        
        # Return to original task
        print("   🔄 Returning to original task...")
        bot.move_to((600, 300), profile=MotionProfiles.NATURAL)
        bot.click("left")
        
        print("✅ Advanced timing patterns completed!")

def demo_error_recovery():
    """Demonstrate error handling and recovery patterns"""
    print("\n🔧 Error Handling Demo")
    print("-" * 40)
    
    try:
        with HumanMouse() as bot:
            print("1. Attempting normal operation...")
            bot.move_to((400, 300))
            bot.click()
            
            print("2. Simulating failed operation and retry...")
            # In real scenarios, you might detect that an action failed
            # Here we simulate a retry pattern
            
            for attempt in range(3):
                print(f"   Attempt {attempt + 1}: Clicking target...")
                bot.move_to((410 + attempt * 5, 305 + attempt * 2))  # Slight position variation
                bot.click("left", duration=0.06 + attempt * 0.01)   # Slightly longer clicks on retries
                
                # Simulate checking if action succeeded
                time.sleep(0.5)
                success = attempt == 2  # Succeed on third attempt
                
                if success:
                    print("   ✅ Operation succeeded!")
                    break
                else:
                    print("   ⚠️  Operation failed, retrying...")
                    time.sleep(0.3)  # Brief pause before retry
            
            print("✅ Error recovery demo completed!")
    
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Make sure the BrowserGeist daemon is running!")

def main():
    """Run all basic mouse control demonstrations"""
    print("🖱️  BrowserGeist - Basic Mouse Control Examples")
    print("=" * 60)
    print()
    print("This demo showcases fundamental mouse automation capabilities:")
    print("• Basic movements with different motion profiles")
    print("• Various click types and durations")
    print("• Realistic human interaction patterns")
    print("• Advanced timing and hesitation behaviors")
    print("• Error handling and recovery strategies")
    print()
    
    try:
        demo_basic_movements()
        demo_click_types()
        demo_motion_profiles()
        demo_realistic_interactions()
        demo_advanced_timing()
        demo_error_recovery()
        
        print("\n🎉 All mouse control demos completed successfully!")
        print("\n💡 Key Takeaways:")
        print("   • Use MotionProfiles.NATURAL for most realistic movement")
        print("   • MotionProfiles.CAREFUL for precise, important actions")
        print("   • MotionProfiles.FAST for efficient bulk operations")
        print("   • Add realistic timing delays between actions")
        print("   • Implement retry logic for robust automation")
        print("   • Vary click durations and positions slightly for realism")
        
    except ConnectionError:
        print("❌ Connection failed: BrowserGeist daemon not running")
        print("\n🔧 To fix this:")
        print("   1. Start the daemon: ./bin/browsergeist daemon start")
        print("   2. Check permissions: ./bin/browsergeist doctor")
        print("   3. Run this demo again")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        print("Run './bin/browsergeist doctor' to diagnose issues")

if __name__ == "__main__":
    main()
