"""
Simple launcher for the Eye-Controlled Interface
Provides easy startup with error handling and system checks
"""

import sys
import os
import subprocess
import logging
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = [
        'cv2', 'mediapipe', 'pyautogui', 'numpy', 
        'PIL', 'psutil', 'pynput', 'screeninfo'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    return missing_modules

def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    """Main launcher function"""
    setup_logging()
    
    print("=" * 60)
    print("    Eye-Controlled Computer Interface Launcher")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: main.py not found in current directory")
        print("Please run this launcher from the project directory")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("\n📦 Would you like to install missing dependencies? (y/n): ", end="")
        
        try:
            response = input().lower()
            if response in ['y', 'yes']:
                print("📥 Installing dependencies...")
                try:
                    subprocess.run([sys.executable, "setup.py"], check=True)
                    print("✅ Dependencies installed successfully")
                except subprocess.CalledProcessError:
                    print("❌ Failed to install dependencies")
                    print("Please run: python setup.py")
                    input("Press Enter to exit...")
                    sys.exit(1)
            else:
                print("Please install dependencies manually:")
                print("python setup.py")
                input("Press Enter to exit...")
                sys.exit(1)
        except KeyboardInterrupt:
            print("\nLauncher cancelled by user")
            sys.exit(1)
    else:
        print("✅ All dependencies found")
    
    # Check camera availability
    print("📷 Checking camera access...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera access confirmed")
            cap.release()
        else:
            print("⚠️  Camera not accessible - please check permissions")
    except Exception as e:
        print(f"⚠️  Camera check failed: {e}")
    
    # Launch the main application
    print("\n🚀 Starting Eye-Controlled Interface...")
    print("=" * 60)
    
    try:
        # Import and run the main application
        from main import main as run_main_app
        run_main_app()
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        logging.error(f"Application error: {e}", exc_info=True)
        print("\nCheck the log files for more details")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
