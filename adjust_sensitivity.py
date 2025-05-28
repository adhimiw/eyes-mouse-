#!/usr/bin/env python3
"""
Sensitivity Adjustment Tool
Allows real-time adjustment of eye tracking sensitivity settings
"""

import json
import sys
from config_manager import ConfigManager

def display_current_settings(config):
    """Display current gesture settings"""
    print("\n" + "=" * 50)
    print("CURRENT GESTURE SETTINGS")
    print("=" * 50)
    
    gesture_settings = config.get_section("gestures")
    for key, value in gesture_settings.items():
        print(f"{key:25}: {value}")
    print("=" * 50)

def adjust_blink_sensitivity(config):
    """Adjust blink detection sensitivity"""
    current = config.get_setting("gestures", "blink_threshold", 0.008)
    print(f"\nCurrent blink threshold: {current}")
    print("Lower values = more sensitive (more false positives)")
    print("Higher values = less sensitive (may miss intentional blinks)")
    print("Recommended range: 0.006 - 0.012")
    
    try:
        new_value = float(input("Enter new blink threshold (or press Enter to keep current): ") or current)
        if 0.003 <= new_value <= 0.020:
            config.set_setting("gestures", "blink_threshold", new_value)
            print(f"✅ Blink threshold updated to {new_value}")
        else:
            print("❌ Value out of safe range (0.003 - 0.020)")
    except ValueError:
        print("❌ Invalid input")

def adjust_wink_sensitivity(config):
    """Adjust wink detection sensitivity"""
    current = config.get_setting("gestures", "wink_threshold", 0.006)
    print(f"\nCurrent wink threshold: {current}")
    print("Should be slightly lower than blink threshold")
    print("Recommended range: 0.004 - 0.010")
    
    try:
        new_value = float(input("Enter new wink threshold (or press Enter to keep current): ") or current)
        if 0.003 <= new_value <= 0.015:
            config.set_setting("gestures", "wink_threshold", new_value)
            print(f"✅ Wink threshold updated to {new_value}")
        else:
            print("❌ Value out of safe range (0.003 - 0.015)")
    except ValueError:
        print("❌ Invalid input")

def adjust_cooldowns(config):
    """Adjust gesture cooldown periods"""
    print("\n--- COOLDOWN SETTINGS ---")
    
    # Gesture cooldown
    current = config.get_setting("gestures", "gesture_cooldown", 1.0)
    print(f"\nCurrent gesture cooldown: {current}s")
    print("Time between any gesture actions")
    print("Recommended range: 0.5 - 2.0 seconds")
    
    try:
        new_value = float(input("Enter new gesture cooldown (or press Enter to keep current): ") or current)
        if 0.1 <= new_value <= 5.0:
            config.set_setting("gestures", "gesture_cooldown", new_value)
            print(f"✅ Gesture cooldown updated to {new_value}s")
        else:
            print("❌ Value out of safe range (0.1 - 5.0)")
    except ValueError:
        print("❌ Invalid input")
    
    # Wink cooldown
    current = config.get_setting("gestures", "wink_cooldown", 0.8)
    print(f"\nCurrent wink cooldown: {current}s")
    print("Time between wink actions")
    print("Recommended range: 0.5 - 1.5 seconds")
    
    try:
        new_value = float(input("Enter new wink cooldown (or press Enter to keep current): ") or current)
        if 0.1 <= new_value <= 3.0:
            config.set_setting("gestures", "wink_cooldown", new_value)
            print(f"✅ Wink cooldown updated to {new_value}s")
        else:
            print("❌ Value out of safe range (0.1 - 3.0)")
    except ValueError:
        print("❌ Invalid input")

def toggle_features(config):
    """Toggle gesture features on/off"""
    print("\n--- FEATURE TOGGLES ---")
    
    features = [
        ("enable_wink_clicks", "Wink-based clicking"),
        ("enable_head_tilt_scroll", "Head tilt scrolling"),
        ("enable_dwell_click", "Dwell clicking")
    ]
    
    for setting_key, description in features:
        current = config.get_setting("gestures", setting_key, True)
        status = "ENABLED" if current else "DISABLED"
        print(f"\n{description}: {status}")
        
        response = input("Toggle this feature? (y/n): ").lower().strip()
        if response == 'y':
            new_value = not current
            config.set_setting("gestures", setting_key, new_value)
            new_status = "ENABLED" if new_value else "DISABLED"
            print(f"✅ {description} is now {new_status}")

def create_preset(config, preset_name):
    """Create sensitivity presets"""
    presets = {
        "conservative": {
            "blink_threshold": 0.010,
            "wink_threshold": 0.008,
            "gesture_cooldown": 1.5,
            "wink_cooldown": 1.0,
            "head_tilt_cooldown": 1.5,
            "enable_dwell_click": False
        },
        "balanced": {
            "blink_threshold": 0.008,
            "wink_threshold": 0.006,
            "gesture_cooldown": 1.0,
            "wink_cooldown": 0.8,
            "head_tilt_cooldown": 1.0,
            "enable_dwell_click": False
        },
        "sensitive": {
            "blink_threshold": 0.006,
            "wink_threshold": 0.004,
            "gesture_cooldown": 0.8,
            "wink_cooldown": 0.6,
            "head_tilt_cooldown": 0.8,
            "enable_dwell_click": True
        }
    }
    
    if preset_name in presets:
        preset = presets[preset_name]
        for key, value in preset.items():
            config.set_setting("gestures", key, value)
        print(f"✅ Applied {preset_name} preset")
        return True
    else:
        print(f"❌ Unknown preset: {preset_name}")
        return False

def main():
    """Main adjustment interface"""
    print("EYE TRACKING SENSITIVITY ADJUSTMENT TOOL")
    print("=" * 50)
    
    try:
        config = ConfigManager()
        
        while True:
            display_current_settings(config)
            
            print("\nOPTIONS:")
            print("1. Adjust blink sensitivity")
            print("2. Adjust wink sensitivity") 
            print("3. Adjust cooldown periods")
            print("4. Toggle features")
            print("5. Apply preset (conservative/balanced/sensitive)")
            print("6. Save and exit")
            print("7. Exit without saving")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                adjust_blink_sensitivity(config)
            elif choice == "2":
                adjust_wink_sensitivity(config)
            elif choice == "3":
                adjust_cooldowns(config)
            elif choice == "4":
                toggle_features(config)
            elif choice == "5":
                preset = input("Enter preset name (conservative/balanced/sensitive): ").strip().lower()
                create_preset(config, preset)
            elif choice == "6":
                config.save_config()
                print("✅ Configuration saved successfully!")
                break
            elif choice == "7":
                print("Exiting without saving changes")
                break
            else:
                print("❌ Invalid choice")
                
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
