#!/usr/bin/env python3
"""
Simple BrowserGeist Demo

Demonstrates basic usage of the BrowserGeist framework
for human-like browser automation.
"""

import sys
import os
import time

# Add the SDK to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'python_sdk'))

from browsergeist import HumanMouse, target, MotionProfiles

def demo_basic_interaction():
    """Demonstrate basic mouse movement and clicking"""
    print("🤖 Starting BrowserGeist demo...")
    
    try:
        with HumanMouse() as bot:
            print("✅ Connected to BrowserGeist daemon")
            
            # Demo 1: Move to specific coordinates
            print("📍 Moving to coordinates (400, 300)...")
            bot.move_to((400, 300), profile=MotionProfiles.NATURAL)
            
            # Demo 2: Click
            print("🖱️  Performing left click...")
            bot.click("left")
            
            # Demo 3: Move with different profile
            print("📍 Moving with careful profile to (600, 400)...")
            bot.move_to((600, 400), profile=MotionProfiles.CAREFUL)
            
            # Demo 4: Right click
            print("🖱️  Performing right click...")
            bot.click("right")
            
            # Demo 5: Typing simulation
            print("⌨️  Typing demo text...")
            bot.type("Hello from BrowserGeist!", delay_profile="average")
            
            print("✅ Demo completed successfully!")
            
    except ConnectionError:
        print("❌ Failed to connect to daemon. Make sure it's running:")
        print("   make daemon")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def demo_image_targeting():
    """Demonstrate image-based targeting (requires screenshot capability)"""
    print("\n🖼️  Image targeting demo...")
    
    # Note: This would require actual image files and a running browser
    # For now, we'll just show the syntax
    
    print("📝 Example syntax for image-based targeting:")
    print("""
    with HumanMouse() as bot:
        # Find and click a login button
        bot.move_to(target("assets/login_button.png"))
        bot.click()
        
        # Type in an email field
        bot.move_to(target("assets/email_field.png"))
        bot.click()
        bot.type("user@example.com")
        
        # Submit the form
        bot.move_to(target("assets/submit_button.png"))
        bot.click()
    """)

def demo_motion_profiles():
    """Demonstrate different motion profiles"""
    print("\n🎯 Motion profile demo...")
    
    profiles = [
        ("Natural", MotionProfiles.NATURAL),
        ("Careful", MotionProfiles.CAREFUL),
        ("Fast", MotionProfiles.FAST)
    ]
    
    try:
        with HumanMouse() as bot:
            for name, profile in profiles:
                print(f"🎭 Testing {name} profile...")
                
                # Move to a random position with this profile
                x = 200 + (profiles.index((name, profile)) * 200)
                y = 200
                
                bot.move_to((x, y), profile=profile)
                time.sleep(0.5)  # Brief pause between movements
                
    except ConnectionError:
        print("❌ Daemon not running. Use 'make daemon' to start it.")

if __name__ == "__main__":
    print("🚀 BrowserGeist Demo Script")
    print("=" * 40)
    
    # Check if daemon is likely running
    import socket
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/tmp/browsergeist.sock")
        sock.close()
        daemon_running = True
    except:
        daemon_running = False
    
    if not daemon_running:
        print("⚠️  Daemon not detected. Starting demos in simulation mode...")
        print("💡 To run full demos, start the daemon with: make daemon")
        print()
    
    # Run demos
    demo_basic_interaction()
    demo_image_targeting() 
    demo_motion_profiles()
    
    print("\n🎉 All demos completed!")
    print("\n📚 Next steps:")
    print("   1. Grant Input Monitoring permissions in System Preferences")
    print("   2. Start the daemon: make daemon")
    print("   3. Create your own automation scripts!")
