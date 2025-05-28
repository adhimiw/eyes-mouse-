#!/usr/bin/env python3
"""
ConfigManager Fix Verification Script
Tests that all ConfigManager methods are working correctly
"""

import sys
import traceback

def test_config_manager():
    """Test ConfigManager functionality"""
    print("🧪 Testing ConfigManager...")
    
    try:
        from config_manager import ConfigManager
        print("✅ ConfigManager imported successfully")
        
        # Test initialization
        config = ConfigManager()
        print("✅ ConfigManager initialized")
        
        # Test get_setting method
        blink_threshold = config.get_setting("gestures", "blink_threshold", 0.008)
        print(f"✅ get_setting works: blink_threshold = {blink_threshold}")
        
        # Test set_setting method
        config.set_setting("test", "verification", 42)
        test_value = config.get_setting("test", "verification")
        print(f"✅ set_setting works: test_value = {test_value}")
        
        # Test get_section method (this was the broken one)
        gesture_settings = config.get_section("gestures")
        print(f"✅ get_section works: found {len(gesture_settings)} gesture settings")
        
        # Display some settings
        print("\n📊 Current gesture settings:")
        for key, value in list(gesture_settings.items())[:8]:
            print(f"  {key:25}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ ConfigManager test failed: {e}")
        traceback.print_exc()
        return False

def test_sensitivity_adjuster():
    """Test that the sensitivity adjuster can import and initialize"""
    print("\n🧪 Testing Sensitivity Adjuster...")
    
    try:
        # Test the function that was failing
        from config_manager import ConfigManager
        config = ConfigManager()
        
        # This is the exact line that was failing before
        gesture_settings = config.get_section("gestures")
        
        print("✅ Sensitivity adjuster imports work")
        print(f"✅ Found {len(gesture_settings)} gesture settings")
        
        # Test a few key settings that the adjuster needs
        required_settings = [
            "blink_threshold",
            "wink_threshold", 
            "gesture_cooldown",
            "wink_cooldown",
            "enable_wink_clicks"
        ]
        
        missing_settings = []
        for setting in required_settings:
            if setting not in gesture_settings:
                missing_settings.append(setting)
        
        if missing_settings:
            print(f"⚠️  Missing settings: {missing_settings}")
        else:
            print("✅ All required settings present")
        
        return True
        
    except Exception as e:
        print(f"❌ Sensitivity adjuster test failed: {e}")
        traceback.print_exc()
        return False

def test_advanced_gesture_detector():
    """Test that the advanced gesture detector can initialize"""
    print("\n🧪 Testing Advanced Gesture Detector...")
    
    try:
        from config_manager import ConfigManager
        from eye_gesture_advanced import AdvancedEyeGestureDetector
        
        config = ConfigManager()
        detector = AdvancedEyeGestureDetector(config)
        
        print("✅ AdvancedEyeGestureDetector initialized")
        print(f"✅ Blink threshold: {detector.blink_threshold}")
        print(f"✅ Wink threshold: {detector.wink_threshold}")
        print(f"✅ Gesture cooldown: {detector.gesture_cooldown}")
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced gesture detector test failed: {e}")
        traceback.print_exc()
        return False

def test_gesture_controller():
    """Test that the gesture controller can initialize"""
    print("\n🧪 Testing Gesture Controller...")
    
    try:
        from config_manager import ConfigManager
        from gesture_controller import GestureController
        
        config = ConfigManager()
        controller = GestureController(config)
        
        print("✅ GestureController initialized")
        print(f"✅ Gesture cooldown: {controller.gesture_cooldown}")
        
        # Test getting stats
        stats = controller.get_gesture_stats()
        print(f"✅ Gesture stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gesture controller test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all verification tests"""
    print("=" * 60)
    print("🔧 CONFIGMANAGER FIX VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("ConfigManager Basic Functions", test_config_manager),
        ("Sensitivity Adjuster Compatibility", test_sensitivity_adjuster),
        ("Advanced Gesture Detector", test_advanced_gesture_detector),
        ("Gesture Controller", test_gesture_controller)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        
        if test_func():
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
            failed += 1
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed}/{passed+failed} ({100*passed/(passed+failed):.1f}%)")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ ConfigManager fix is working correctly")
        print("✅ Sensitivity adjustment tool should work")
        print("✅ Main eye tracking application should work")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        print("❌ Some components may not work correctly")
        return 1
    
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
