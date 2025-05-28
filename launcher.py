#!/usr/bin/env python3
"""
Launcher for Eye and Gesture Controlled Mouse Systems
Choose between different control modes and implementations
"""

import os
import sys
import subprocess
import time

def print_banner():
    """Print application banner"""
    print("=" * 70)
    print("    🚀 EYE & GESTURE CONTROLLED MOUSE LAUNCHER")
    print("    Advanced Computer Control with AI & Reinforcement Learning")
    print("=" * 70)

def print_menu():
    """Print main menu"""
    print("\n📋 Available Control Systems:")
    print()
    print("1. 👁️  Simple Eye Mouse (Working - Basic)")
    print("   - Eye tracking for cursor movement")
    print("   - Blink to click")
    print("   - Lightweight and fast")
    print()
    print("2. 🎮 Working Gesture Controller (NEW - FULLY FUNCTIONAL)")
    print("   - Based on Viral-Doshi repository")
    print("   - V-gesture cursor control")
    print("   - Fist drag, pinch scroll")
    print("   - Reinforcement learning")
    print()
    print("3. 🔍 Gesture Debug & Test System (DEBUGGING)")
    print("   - Individual gesture testing")
    print("   - Performance benchmarks")
    print("   - Accuracy measurements")
    print("   - Real-time debug info")
    print()
    print("4. 🔥 Hybrid Eye + Gesture Controller")
    print("   - Eyes for cursor movement")
    print("   - Hands for actions")
    print("   - Multiple control modes")
    print()
    print("5. ⚡ Optimized Eye Interface (Performance)")
    print("   - Maximum performance eye tracking")
    print("   - Minimal latency")
    print("   - Optimized for speed")
    print()
    print("6. 👁️ Eye Tracking Test (DEBUGGING)")
    print("   - Test eye cursor movement")
    print("   - Debug iris detection")
    print("   - Sensitivity adjustment")
    print()
    print("7. 🛠️  System Test & Diagnostics")
    print("   - Test camera and dependencies")
    print("   - Performance benchmarks")
    print("   - Compatibility checks")
    print()
    print("8. ❌ Exit")
    print()

def run_application(script_name, description):
    """Run a specific application"""
    print(f"\n🚀 Starting {description}...")
    print("   Press Ctrl+C to return to menu")
    print("-" * 50)

    try:
        # Check if script exists
        if not os.path.exists(script_name):
            print(f"❌ Error: {script_name} not found!")
            return False

        # Run the script
        result = subprocess.run([sys.executable, script_name],
                              capture_output=False,
                              text=True)

        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
        else:
            print(f"⚠️  {description} exited with code {result.returncode}")

        return True

    except KeyboardInterrupt:
        print(f"\n⏹️  {description} interrupted by user")
        return True
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    print("\n🔍 Checking dependencies...")

    required_modules = [
        'cv2', 'mediapipe', 'pyautogui', 'numpy'
    ]

    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing.append(module)

    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("   Please run: pip install opencv-python mediapipe pyautogui numpy")
        return False
    else:
        print("\n✅ All dependencies available!")
        return True

def show_performance_tips():
    """Show performance optimization tips"""
    print("\n💡 Performance Tips:")
    print("   • Ensure good lighting for camera")
    print("   • Position face 50-80cm from camera")
    print("   • Close unnecessary applications")
    print("   • Use 'simple_eye_mouse.py' for best performance")
    print("   • Adjust sensitivity with 's' key")
    print("   • Use 'q' or ESC to quit applications")

def main():
    """Main launcher function"""
    print_banner()

    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Cannot proceed without required dependencies")
        return

    show_performance_tips()

    while True:
        print_menu()

        try:
            choice = input("🎯 Select option (1-8): ").strip()

            if choice == '1':
                success = run_application('simple_eye_mouse.py', 'Simple Eye Mouse')
                if not success:
                    print("   Trying alternative...")
                    run_application('simple_eye_mouse_opencv.py', 'Simple Eye Mouse (OpenCV)')

            elif choice == '2':
                run_application('gesture_controller_working.py', 'Working Gesture Controller')

            elif choice == '3':
                run_application('gesture_debug_tester.py', 'Gesture Debug & Test System')

            elif choice == '4':
                run_application('hybrid_eye_gesture_controller.py', 'Hybrid Eye + Gesture Controller (FIXED)')

            elif choice == '5':
                run_application('main_optimized.py', 'Optimized Eye Interface')

            elif choice == '6':
                run_application('test_eye_tracking_fix.py', 'Eye Tracking Test')

            elif choice == '7':
                run_application('test_system.py', 'System Test & Diagnostics')

            elif choice == '8':
                print("\n👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice. Please select 1-8.")
                continue

            # Pause before showing menu again
            input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

if __name__ == "__main__":
    main()
