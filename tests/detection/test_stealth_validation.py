#!/usr/bin/env python3
"""
BrowserGeist Stealth Validation Test
Tests the enhanced virtual mouse driver against browser detection mechanisms.
"""

import sys
import os
import time
import subprocess
import webbrowser
from pathlib import Path

# Add the source directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent / "src" / "python_sdk"))

try:
    from browsergeist import HumanMouse, MotionProfiles
except ImportError as e:
    print(f"❌ Failed to import BrowserGeist SDK: {e}")
    print("Make sure the daemon is built and the Python SDK is available")
    sys.exit(1)

def check_daemon_running():
    """Check if browsergeist daemon is running"""
    try:
        result = subprocess.run(['pgrep', '-f', 'browsergeist-daemon'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def start_daemon():
    """Start the browsergeist daemon"""
    daemon_path = Path(__file__).parent.parent.parent / "bin" / "browsergeist-daemon"
    if not daemon_path.exists():
        print(f"❌ Daemon not found at {daemon_path}")
        print("Run 'make build' to compile the daemon first")
        return False
    
    try:
        subprocess.Popen([str(daemon_path)], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        time.sleep(2)  # Give daemon time to start
        return check_daemon_running()
    except Exception as e:
        print(f"❌ Failed to start daemon: {e}")
        return False

def run_stealth_test():
    """Run automated stealth validation test"""
    print("🤖 BrowserGeist Stealth Validation Test")
    print("=" * 50)
    
    # Check daemon status
    if not check_daemon_running():
        print("⚠️ Daemon not running, attempting to start...")
        if not start_daemon():
            print("❌ Could not start daemon. Please run manually:")
            print("   make build && ./bin/browsergeist-daemon &")
            return False
    
    print("✅ Daemon is running")
    
    # Initialize mouse controller
    try:
        bot = HumanMouse()
        print("✅ Connected to BrowserGeist daemon")
    except Exception as e:
        print(f"❌ Failed to connect to daemon: {e}")
        return False
    
    # Open browser test page
    test_file = Path(__file__).parent / "browser_detection_test.html"
    test_url = f"file://{test_file.absolute()}"
    
    print(f"🌐 Opening test page: {test_url}")
    webbrowser.open(test_url)
    
    # Wait for browser to load
    print("⏳ Waiting for browser to load...")
    time.sleep(3)
    
    # Run test sequence
    print("\n🧪 Running stealth test sequence...")
    
    try:
        # Test 1: Natural movement pattern
        print("Test 1: Natural mouse movement...")
        for i in range(5):
            x = 400 + (i * 50)
            y = 300 + (i * 20)
            bot.move_to((x, y), profile=MotionProfiles.NATURAL)
            time.sleep(0.5)
        
        # Test 2: Clicking with different profiles
        print("Test 2: Clicking with motion profiles...")
        profiles = [MotionProfiles.NATURAL, MotionProfiles.CAREFUL, MotionProfiles.FAST]
        for i, profile in enumerate(profiles):
            x = 500 + (i * 30)
            y = 400
            bot.move_to((x, y), profile=profile)
            bot.click()
            time.sleep(1)
        
        # Test 3: Rapid movements to test timing variations
        print("Test 3: Rapid movement sequence...")
        positions = [
            (300, 200), (600, 200), (600, 500), (300, 500), (450, 350)
        ]
        for pos in positions:
            bot.move_to(pos, profile=MotionProfiles.FAST)
            time.sleep(0.2)
        
        # Test 4: Micro-movements and clicks
        print("Test 4: Micro-movements and precise clicking...")
        for i in range(3):
            bot.move_to((450 + i, 350 + i), profile=MotionProfiles.CAREFUL)
            bot.click()
            time.sleep(0.8)
        
        print("\n✅ Test sequence completed!")
        print("\n📊 Please check the browser window for detailed results:")
        print("   - Trust ratio should be >90% for good stealth")
        print("   - Look for any 'SUSPICIOUS' event indicators")
        print("   - Export results for detailed analysis")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def analyze_results():
    """Provide guidance on interpreting test results"""
    print("\n📋 Result Analysis Guide:")
    print("=" * 30)
    print("✅ GOOD STEALTH INDICATORS:")
    print("   • Trust ratio >90%")
    print("   • isTrusted=true for all events")
    print("   • No 'perfect-coordinates' warnings")
    print("   • Natural timing variance in movements")
    print()
    print("⚠️ POTENTIAL DETECTION RISKS:")
    print("   • Trust ratio <70%")
    print("   • 'too-fast-movement' warnings")
    print("   • 'low-timing-variance' indicators")
    print("   • Consistent event patterns")
    print()
    print("🔧 IMPROVEMENTS NEEDED IF DETECTED:")
    print("   • Increase timing randomization")
    print("   • Add more motion curve variation")
    print("   • Implement deeper HID-level injection")
    print("   • Add micro-tremor to movements")

if __name__ == "__main__":
    success = run_stealth_test()
    analyze_results()
    
    if success:
        print(f"\n🎯 Test completed. Check browser for detailed stealth analysis.")
    else:
        print(f"\n❌ Test failed. Please check daemon status and try again.")
