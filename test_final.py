#!/usr/bin/env python3
"""
Final Test Script for Eye-Controlled Interface
Tests all components and provides a summary
"""

import sys
import traceback

def test_imports():
    """Test all required imports"""
    print("🧪 Testing Imports...")
    
    try:
        import cv2
        print(f"   ✅ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"   ❌ OpenCV: {e}")
        return False
    
    try:
        import pyautogui
        print(f"   ✅ PyAutoGUI: Available")
    except ImportError as e:
        print(f"   ❌ PyAutoGUI: {e}")
        return False
    
    try:
        import tkinter
        print(f"   ✅ Tkinter: Available")
    except ImportError as e:
        print(f"   ❌ Tkinter: {e}")
        return False
    
    try:
        import numpy
        print(f"   ✅ NumPy: {numpy.__version__}")
    except ImportError as e:
        print(f"   ❌ NumPy: {e}")
        return False
    
    try:
        from config_manager import ConfigManager
        print(f"   ✅ ConfigManager: Available")
    except ImportError as e:
        print(f"   ❌ ConfigManager: {e}")
        return False
    
    try:
        from eye_tracker_opencv import EyeTrackerOpenCV
        print(f"   ✅ EyeTrackerOpenCV: Available")
    except ImportError as e:
        print(f"   ❌ EyeTrackerOpenCV: {e}")
        return False
    
    try:
        from ui_overlay import EyeTrackingOverlay
        print(f"   ✅ EyeTrackingOverlay: Available")
    except ImportError as e:
        print(f"   ❌ EyeTrackingOverlay: {e}")
        return False
    
    return True

def test_camera():
    """Test camera access"""
    print("\n🧪 Testing Camera...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print(f"   ✅ Camera: Working (Frame: {frame.shape})")
                return True
            else:
                print("   ❌ Camera: Cannot read frames")
                return False
        else:
            print("   ❌ Camera: Cannot open")
            return False
    except Exception as e:
        print(f"   ❌ Camera: {e}")
        return False

def test_eye_tracker():
    """Test eye tracker initialization"""
    print("\n🧪 Testing Eye Tracker...")
    
    try:
        from config_manager import ConfigManager
        from eye_tracker_opencv import EyeTrackerOpenCV
        
        config = ConfigManager()
        tracker = EyeTrackerOpenCV(config)
        
        # Test initialization
        if tracker.initialize_camera():
            print("   ✅ Eye Tracker: Initialized successfully")
            tracker.cleanup()
            return True
        else:
            print("   ❌ Eye Tracker: Failed to initialize camera")
            return False
            
    except Exception as e:
        print(f"   ❌ Eye Tracker: {e}")
        return False

def test_screen_control():
    """Test screen control capabilities"""
    print("\n🧪 Testing Screen Control...")
    
    try:
        import pyautogui
        
        # Test screen size detection
        screen_size = pyautogui.size()
        print(f"   ✅ Screen Size: {screen_size}")
        
        # Test cursor position
        pos = pyautogui.position()
        print(f"   ✅ Cursor Position: {pos}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Screen Control: {e}")
        return False

def test_main_application():
    """Test main application import"""
    print("\n🧪 Testing Main Application...")
    
    try:
        # Test import without running
        import main
        print("   ✅ Main Application: Import successful")
        return True
        
    except Exception as e:
        print(f"   ❌ Main Application: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("    Eye-Controlled Interface - Final Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Camera", test_camera),
        ("Eye Tracker", test_eye_tracker),
        ("Screen Control", test_screen_control),
        ("Main Application", test_main_application),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"   ❌ {test_name}: Unexpected error - {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("                    FINAL RESULTS")
    print("=" * 60)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The eye-controlled interface is ready to use.")
        print("\nTo run the application:")
        print("  python3 main.py                    # Full GUI application")
        print("  python3 simple_eye_mouse_opencv.py # Simple eye mouse")
    else:
        print(f"\n⚠️  {total-passed} tests failed. Some features may not work correctly.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
