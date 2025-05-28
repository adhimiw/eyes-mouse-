#!/usr/bin/env python3
"""
Test PyAutoGUI Mouse Control on Fedora/Wayland
This script tests if mouse control is working properly
"""

import pyautogui
import time
import sys
import os

def test_basic_mouse_functions():
    """Test basic PyAutoGUI mouse functions"""
    print("🖱️  Testing PyAutoGUI Mouse Control")
    print("=" * 50)
    
    # Disable failsafe for testing
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.001
    
    try:
        # Test 1: Get current position
        print("Test 1: Getting current mouse position...")
        current_pos = pyautogui.position()
        print(f"✅ Current position: {current_pos}")
        
        # Test 2: Get screen size
        print("\nTest 2: Getting screen size...")
        screen_size = pyautogui.size()
        print(f"✅ Screen size: {screen_size}")
        
        # Test 3: Small relative movement
        print("\nTest 3: Small relative movement...")
        print("Moving mouse in a small square pattern...")
        
        original_pos = pyautogui.position()
        movements = [(10, 0), (0, 10), (-10, 0), (0, -10)]
        
        for dx, dy in movements:
            pyautogui.moveRel(dx, dy)
            time.sleep(0.2)
            new_pos = pyautogui.position()
            print(f"  Moved by ({dx}, {dy}) -> Position: {new_pos}")
        
        print("✅ Relative movement test completed")
        
        # Test 4: Absolute movement
        print("\nTest 4: Absolute movement...")
        center_x = screen_size[0] // 2
        center_y = screen_size[1] // 2
        
        print(f"Moving to center: ({center_x}, {center_y})")
        pyautogui.moveTo(center_x, center_y)
        time.sleep(0.5)
        
        final_pos = pyautogui.position()
        print(f"✅ Final position: {final_pos}")
        
        # Return to original position
        pyautogui.moveTo(original_pos[0], original_pos[1])
        
        print("\n🎉 All mouse control tests PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Mouse control test FAILED: {e}")
        print("\nPossible solutions:")
        print("1. Run with X11 instead of Wayland:")
        print("   export GDK_BACKEND=x11")
        print("   export QT_QPA_PLATFORM=xcb")
        print("2. Install additional packages:")
        print("   sudo dnf install python3-tkinter xdotool")
        print("3. Check permissions and accessibility settings")
        return False

def test_wayland_compatibility():
    """Test Wayland-specific issues"""
    print("\n🔍 Testing Wayland Compatibility")
    print("=" * 50)
    
    # Check environment variables
    session_type = os.environ.get('XDG_SESSION_TYPE', 'unknown')
    wayland_display = os.environ.get('WAYLAND_DISPLAY', 'not set')
    display = os.environ.get('DISPLAY', 'not set')
    
    print(f"Session type: {session_type}")
    print(f"Wayland display: {wayland_display}")
    print(f"X11 display: {display}")
    
    if session_type == 'wayland':
        print("\n⚠️  Running on Wayland - this may cause issues with PyAutoGUI")
        print("Recommendations:")
        print("1. Switch to X11 session for better compatibility")
        print("2. Or run with X11 backend: GDK_BACKEND=x11 python script.py")
        return False
    else:
        print("✅ Running on X11 - should work fine")
        return True

def test_performance():
    """Test mouse movement performance"""
    print("\n⚡ Testing Performance")
    print("=" * 50)
    
    try:
        # Test movement speed
        start_time = time.time()
        movements = 100
        
        for i in range(movements):
            pyautogui.moveRel(1, 0)
            pyautogui.moveRel(-1, 0)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = (total_time / movements) * 1000  # ms per movement
        
        print(f"Performed {movements} movements in {total_time:.3f} seconds")
        print(f"Average time per movement: {avg_time:.2f} ms")
        
        if avg_time < 50:  # Sub-50ms requirement
            print("✅ Performance test PASSED (sub-50ms)")
            return True
        else:
            print("⚠️  Performance test WARNING (>50ms)")
            return False
            
    except Exception as e:
        print(f"❌ Performance test FAILED: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 PyAutoGUI Mouse Control Test Suite")
    print("This will test if mouse control works on your system")
    print("Press Ctrl+C to stop at any time\n")
    
    try:
        # Run tests
        basic_test = test_basic_mouse_functions()
        wayland_test = test_wayland_compatibility()
        performance_test = test_performance()
        
        # Summary
        print("\n📊 Test Summary")
        print("=" * 50)
        print(f"Basic mouse control: {'✅ PASS' if basic_test else '❌ FAIL'}")
        print(f"Wayland compatibility: {'✅ PASS' if wayland_test else '⚠️  WARNING'}")
        print(f"Performance (sub-50ms): {'✅ PASS' if performance_test else '⚠️  WARNING'}")
        
        if basic_test:
            print("\n🎉 Mouse control is working! You can proceed with eye tracking.")
        else:
            print("\n❌ Mouse control issues detected. Please fix before using eye tracking.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
