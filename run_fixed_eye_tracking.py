#!/usr/bin/env python3
"""
Fixed Eye Tracking System Launcher
Runs the eye tracking system with all click fixes applied
"""

import sys
import os
import subprocess
import time

def check_environment():
    """Check if the virtual environment is properly set up"""
    venv_path = "eye_tracking_env/bin/python"
    if not os.path.exists(venv_path):
        print("❌ Virtual environment not found!")
        print("Please run: python setup_verified_venv.py")
        return False
    return True

def show_welcome():
    """Display welcome message with fix information"""
    print("=" * 60)
    print("🎯 FIXED EYE TRACKING SYSTEM")
    print("=" * 60)
    print("✅ Click sensitivity issues FIXED!")
    print("✅ Advanced gesture controls added!")
    print("✅ False positive prevention enabled!")
    print("")
    print("🎮 NEW CONTROLS:")
    print("  👁️  Left Eye Wink  → Left Click")
    print("  👁️  Right Eye Wink → Right Click") 
    print("  👀 Both Eyes Blink → Middle Click")
    print("  🔄 Head Tilt Left  → Scroll Left")
    print("  🔄 Head Tilt Right → Scroll Right")
    print("  🔄 Head Tilt Up    → Scroll Up")
    print("  🔄 Head Tilt Down  → Scroll Down")
    print("")
    print("⚙️  IMPROVEMENTS:")
    print("  • Blink threshold: 0.004 → 0.008 (less sensitive)")
    print("  • Gesture cooldown: 0.1s → 1.0s (prevents rapid-fire)")
    print("  • Advanced pattern recognition")
    print("  • Real-time performance monitoring")
    print("")
    print("🛑 EMERGENCY CONTROLS:")
    print("  • Ctrl+Shift+E: Emergency disable gestures")
    print("  • ESC: Exit application")
    print("  • Ctrl+C: Force stop")
    print("=" * 60)

def run_system():
    """Run the main eye tracking system"""
    try:
        print("🚀 Starting fixed eye tracking system...")
        
        # Use the virtual environment python
        venv_python = "eye_tracking_env/bin/python"
        
        # Run the main application
        result = subprocess.run([venv_python, "main.py"], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print("✅ System exited normally")
        else:
            print(f"⚠️  System exited with code: {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ Error running system: {e}")
        return False
    
    return True

def run_test():
    """Run the click fix test"""
    try:
        print("🧪 Running click fix test...")
        
        venv_python = "eye_tracking_env/bin/python"
        result = subprocess.run([venv_python, "test_click_fix.py"], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print("✅ Test completed successfully")
        else:
            print(f"⚠️  Test exited with code: {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False
    
    return True

def adjust_settings():
    """Run the sensitivity adjustment tool"""
    try:
        print("⚙️  Opening sensitivity adjustment tool...")
        
        venv_python = "eye_tracking_env/bin/python"
        result = subprocess.run([venv_python, "adjust_sensitivity.py"], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print("✅ Settings adjustment completed")
        else:
            print(f"⚠️  Settings tool exited with code: {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n🛑 Settings adjustment cancelled")
    except Exception as e:
        print(f"❌ Error running settings tool: {e}")
        return False
    
    return True

def main():
    """Main launcher interface"""
    # Check environment first
    if not check_environment():
        return 1
    
    show_welcome()
    
    while True:
        print("\n📋 MENU:")
        print("1. 🚀 Run Fixed Eye Tracking System")
        print("2. 🧪 Test Click Fix (30 second test)")
        print("3. ⚙️  Adjust Sensitivity Settings")
        print("4. 📖 View Fix Documentation")
        print("5. 🚪 Exit")
        
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                if not run_system():
                    print("System failed to run properly")
                    
            elif choice == "2":
                if not run_test():
                    print("Test failed to run properly")
                    
            elif choice == "3":
                if not adjust_settings():
                    print("Settings adjustment failed")
                    
            elif choice == "4":
                print("\n📖 Opening fix documentation...")
                try:
                    subprocess.run(["less", "CLICK_FIX_SUMMARY.md"])
                except:
                    print("Please read CLICK_FIX_SUMMARY.md for detailed information")
                    
            elif choice == "5":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
