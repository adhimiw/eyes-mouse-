#!/usr/bin/env python3
"""
Action Demonstration Script
Shows exactly what actions are being performed
"""

import time
import subprocess
import sys
from gesture_action_processor import GestureActionProcessor
from advanced_gesture_detector import GestureType

def demonstrate_actions():
    """Demonstrate all gesture actions with clear feedback"""
    print("🎯 GESTURE ACTION DEMONSTRATION")
    print("=" * 50)
    print("This will demonstrate each gesture action with clear feedback")
    print("Watch your screen carefully for the effects!")
    print()
    
    # Initialize processor
    processor = GestureActionProcessor('xdotool')
    
    # Get current mouse position
    try:
        result = subprocess.run(['xdotool', 'getmouselocation'], 
                              capture_output=True, text=True, check=True)
        print(f"📍 Current mouse position: {result.stdout.strip()}")
    except:
        print("📍 Could not get mouse position")
    
    print("\n🚀 Starting action demonstrations...")
    print("Each action will be performed with a 2-second delay")
    print()
    
    # Demonstrate left click
    print("1️⃣  DEMONSTRATING LEFT CLICK (Left Eye Wink)")
    print("   You should see a left mouse click happen...")
    time.sleep(2)
    
    gesture_data = {
        'type': GestureType.LEFT_WINK,
        'confidence': 0.8,
        'timestamp': time.time()
    }
    success = processor.left_click(gesture_data)
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print()
    
    # Demonstrate right click
    print("2️⃣  DEMONSTRATING RIGHT CLICK (Right Eye Wink)")
    print("   You should see a right mouse click (context menu may appear)...")
    time.sleep(2)
    
    gesture_data = {
        'type': GestureType.RIGHT_WINK,
        'confidence': 0.8,
        'timestamp': time.time()
    }
    success = processor.right_click(gesture_data)
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print()
    
    # Demonstrate scroll down
    print("3️⃣  DEMONSTRATING SCROLL DOWN (Head Tilt Down)")
    print("   You should see the page/window scroll down...")
    time.sleep(2)
    
    gesture_data = {
        'type': GestureType.HEAD_TILT_DOWN,
        'confidence': 1.0,
        'angle': 25.0,
        'timestamp': time.time()
    }
    success = processor.scroll_down(gesture_data)
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print()
    
    # Demonstrate scroll up
    print("4️⃣  DEMONSTRATING SCROLL UP (Head Tilt Up)")
    print("   You should see the page/window scroll up...")
    time.sleep(2)
    
    gesture_data = {
        'type': GestureType.HEAD_TILT_UP,
        'confidence': 1.0,
        'angle': -25.0,
        'timestamp': time.time()
    }
    success = processor.scroll_up(gesture_data)
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print()
    
    # Demonstrate scroll left
    print("5️⃣  DEMONSTRATING SCROLL LEFT (Head Tilt Left)")
    print("   You should see horizontal scrolling left...")
    time.sleep(2)
    
    gesture_data = {
        'type': GestureType.HEAD_TILT_LEFT,
        'confidence': 1.0,
        'angle': -20.0,
        'timestamp': time.time()
    }
    success = processor.scroll_left(gesture_data)
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print()
    
    # Demonstrate scroll right
    print("6️⃣  DEMONSTRATING SCROLL RIGHT (Head Tilt Right)")
    print("   You should see horizontal scrolling right...")
    time.sleep(2)
    
    gesture_data = {
        'type': GestureType.HEAD_TILT_RIGHT,
        'confidence': 1.0,
        'angle': 20.0,
        'timestamp': time.time()
    }
    success = processor.scroll_right(gesture_data)
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print()
    
    # Get final statistics
    stats = processor.get_action_statistics()
    print("📊 DEMONSTRATION COMPLETE!")
    print("=" * 50)
    print(f"Total actions performed: {stats['total_actions']}")
    print("Action breakdown:")
    for action, count in stats['action_counts'].items():
        if count > 0:
            print(f"  {action}: {count}")
    
    print("\n💡 TROUBLESHOOTING:")
    print("If you didn't see the actions:")
    print("1. Make sure this terminal window is in focus")
    print("2. Try opening a web browser or text editor and run this again")
    print("3. The actions might be working but not visible in this terminal")
    print("4. Try running the main eye tracking app and watch for effects in other windows")

def test_in_browser():
    """Test actions specifically in a browser"""
    print("\n🌐 BROWSER TEST")
    print("=" * 30)
    print("Opening a browser for better action visibility...")
    
    try:
        # Try to open a browser
        subprocess.run(['firefox', 'https://example.com'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Browser opened - try the actions now!")
        print("You should see scrolling and clicking effects in the browser")
    except:
        try:
            subprocess.run(['google-chrome', 'https://example.com'], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ Browser opened - try the actions now!")
        except:
            print("❌ Could not open browser automatically")
            print("Please open a browser manually and try the actions")

def main():
    """Main demonstration function"""
    print("🎯 GESTURE ACTION DEMONSTRATION SCRIPT")
    print("This will show you exactly what each gesture action does")
    print()
    
    choice = input("Choose test type:\n1. Basic demonstration\n2. Browser test\n3. Both\nEnter choice (1-3): ")
    
    if choice in ['1', '3']:
        demonstrate_actions()
    
    if choice in ['2', '3']:
        test_in_browser()
    
    print("\n🎉 Demonstration complete!")
    print("Now you know what to expect when using the eye tracking system.")

if __name__ == "__main__":
    main()
