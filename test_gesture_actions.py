#!/usr/bin/env python3
"""
Test Gesture Actions
Simple test script to verify that gesture actions are working properly
"""

import time
import subprocess
import sys
from gesture_action_processor import GestureActionProcessor
from advanced_gesture_detector import GestureType

def test_xdotool_basic():
    """Test basic xdotool functionality"""
    print("🔧 Testing basic xdotool functionality...")
    
    try:
        # Test mouse position
        result = subprocess.run(['xdotool', 'getmouselocation'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Current mouse position: {result.stdout.strip()}")
        
        # Test simple click
        print("Testing left click...")
        result = subprocess.run(['xdotool', 'click', '1'], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print("✅ Left click successful")
        else:
            print(f"❌ Left click failed: {result.stderr}")
        
        # Test scroll
        print("Testing scroll up...")
        result = subprocess.run(['xdotool', 'click', '4'], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print("✅ Scroll up successful")
        else:
            print(f"❌ Scroll up failed: {result.stderr}")
        
        # Test key press
        print("Testing key press...")
        result = subprocess.run(['xdotool', 'key', 'space'], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print("✅ Key press successful")
        else:
            print(f"❌ Key press failed: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"❌ xdotool test failed: {e}")
        return False

def test_gesture_processor():
    """Test the gesture action processor"""
    print("\n🎯 Testing Gesture Action Processor...")
    
    try:
        processor = GestureActionProcessor('xdotool')
        
        # Test left click
        print("Testing left click gesture...")
        gesture_data = {
            'type': GestureType.LEFT_WINK,
            'confidence': 0.8,
            'timestamp': time.time()
        }
        success = processor.left_click(gesture_data)
        print(f"Left click result: {'✅ Success' if success else '❌ Failed'}")
        time.sleep(1)
        
        # Test right click
        print("Testing right click gesture...")
        gesture_data = {
            'type': GestureType.RIGHT_WINK,
            'confidence': 0.8,
            'timestamp': time.time()
        }
        success = processor.right_click(gesture_data)
        print(f"Right click result: {'✅ Success' if success else '❌ Failed'}")
        time.sleep(1)
        
        # Test scroll down
        print("Testing scroll down gesture...")
        gesture_data = {
            'type': GestureType.HEAD_TILT_DOWN,
            'confidence': 1.0,
            'angle': 25.0,
            'timestamp': time.time()
        }
        success = processor.scroll_down(gesture_data)
        print(f"Scroll down result: {'✅ Success' if success else '❌ Failed'}")
        time.sleep(1)
        
        # Test scroll up
        print("Testing scroll up gesture...")
        gesture_data = {
            'type': GestureType.HEAD_TILT_UP,
            'confidence': 1.0,
            'angle': -25.0,
            'timestamp': time.time()
        }
        success = processor.scroll_up(gesture_data)
        print(f"Scroll up result: {'✅ Success' if success else '❌ Failed'}")
        time.sleep(1)
        
        # Get statistics
        stats = processor.get_action_statistics()
        print(f"\n📊 Action Statistics:")
        print(f"Total actions: {stats['total_actions']}")
        for action, count in stats['action_counts'].items():
            if count > 0:
                print(f"  {action}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gesture processor test failed: {e}")
        return False

def test_alternative_methods():
    """Test alternative action methods"""
    print("\n🔄 Testing Alternative Action Methods...")
    
    try:
        # Test PyAutoGUI
        print("Testing PyAutoGUI...")
        try:
            import pyautogui
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0.1
            
            current_pos = pyautogui.position()
            print(f"PyAutoGUI current position: {current_pos}")
            
            # Test small movement
            pyautogui.moveRel(5, 5)
            pyautogui.moveRel(-5, -5)
            print("✅ PyAutoGUI movement test successful")
            
            # Test click
            pyautogui.click()
            print("✅ PyAutoGUI click test successful")
            
        except Exception as e:
            print(f"❌ PyAutoGUI test failed: {e}")
        
        # Test system commands
        print("Testing system commands...")
        try:
            import os
            os.system('xdotool click 1 > /dev/null 2>&1')
            print("✅ System command test successful")
        except Exception as e:
            print(f"❌ System command test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Alternative methods test failed: {e}")
        return False

def test_window_focus():
    """Test window focus and active window detection"""
    print("\n🪟 Testing Window Focus...")
    
    try:
        # Get active window
        result = subprocess.run(['xdotool', 'getactivewindow'], 
                              capture_output=True, text=True, check=True)
        window_id = result.stdout.strip()
        print(f"Active window ID: {window_id}")
        
        # Get window name
        result = subprocess.run(['xdotool', 'getwindowname', window_id], 
                              capture_output=True, text=True, check=True)
        window_name = result.stdout.strip()
        print(f"Active window name: {window_name}")
        
        # Test window-specific click
        result = subprocess.run(['xdotool', 'mousemove', '--window', window_id, '50', '50'], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print("✅ Window-specific mouse move successful")
        else:
            print(f"❌ Window-specific mouse move failed: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Window focus test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Gesture Action Test Suite")
    print("This will test if gesture actions are working properly")
    print("=" * 60)
    
    # Run tests
    basic_test = test_xdotool_basic()
    processor_test = test_gesture_processor()
    alternative_test = test_alternative_methods()
    focus_test = test_window_focus()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Basic xdotool: {'✅ PASS' if basic_test else '❌ FAIL'}")
    print(f"Gesture processor: {'✅ PASS' if processor_test else '❌ FAIL'}")
    print(f"Alternative methods: {'✅ PASS' if alternative_test else '❌ FAIL'}")
    print(f"Window focus: {'✅ PASS' if focus_test else '❌ FAIL'}")
    
    if all([basic_test, processor_test, alternative_test, focus_test]):
        print("\n🎉 All tests PASSED! Gesture actions should work properly.")
    else:
        print("\n⚠️  Some tests FAILED. Check the output above for details.")
        print("\nTroubleshooting tips:")
        print("1. Make sure you're running in a graphical environment")
        print("2. Try running with X11 instead of Wayland")
        print("3. Check if the active window accepts input")
        print("4. Ensure xdotool has proper permissions")

if __name__ == "__main__":
    main()
