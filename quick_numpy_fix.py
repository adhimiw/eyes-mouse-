#!/usr/bin/env python3
"""
Quick NumPy Compatibility Fix
One-command solution for NumPy 2.x compatibility issues
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def main():
    print("=" * 60)
    print("    Quick NumPy Compatibility Fix")
    print("=" * 60)
    
    # Check current NumPy version
    try:
        import numpy
        version = numpy.__version__
        print(f"Current NumPy version: {version}")
        
        if version.startswith('2.'):
            print("⚠️  NumPy 2.x detected - fixing compatibility...")
            needs_fix = True
        else:
            print("✅ NumPy 1.x detected - checking package compatibility...")
            needs_fix = False
    except ImportError:
        print("❌ NumPy not found - installing...")
        needs_fix = True
    
    # Commands to fix the issue
    commands = [
        # Remove conflicting packages
        ("python3 -m pip uninstall -y opencv-python opencv-contrib-python mediapipe pyautogui numpy scipy", 
         "Removing conflicting packages"),
        
        # Install compatible NumPy
        ("python3 -m pip install --user 'numpy>=1.21.0,<2.0.0'", 
         "Installing compatible NumPy"),
        
        # Install other packages with compatible versions
        ("python3 -m pip install --user opencv-python==4.8.1.78", 
         "Installing OpenCV"),
        
        ("python3 -m pip install --user mediapipe==0.10.7", 
         "Installing MediaPipe"),
        
        ("python3 -m pip install --user pyautogui==0.9.54", 
         "Installing PyAutoGUI"),
        
        ("python3 -m pip install --user 'Pillow>=9.0.0,<11.0.0'", 
         "Installing Pillow"),
        
        ("python3 -m pip install --user 'psutil>=5.8.0'", 
         "Installing psutil"),
        
        ("python3 -m pip install --user 'pynput>=1.7.0'", 
         "Installing pynput"),
        
        ("python3 -m pip install --user 'screeninfo>=0.8.0'", 
         "Installing screeninfo"),
    ]
    
    # Execute commands
    success_count = 0
    for cmd, desc in commands:
        if run_command(cmd, desc):
            success_count += 1
    
    print(f"\n📊 Completed {success_count}/{len(commands)} operations")
    
    # Test the fix
    print("\n🧪 Testing the fix...")
    test_code = """
import warnings
warnings.filterwarnings('ignore')

try:
    import numpy
    print(f'✅ NumPy {numpy.__version__}')
    
    import cv2
    print(f'✅ OpenCV {cv2.__version__}')
    
    import mediapipe
    print(f'✅ MediaPipe {mediapipe.__version__}')
    
    import pyautogui
    print(f'✅ PyAutoGUI {pyautogui.__version__}')
    
    # Test NumPy-OpenCV integration
    import numpy as np
    test_array = np.zeros((10, 10, 3), dtype=np.uint8)
    result = cv2.cvtColor(test_array, cv2.COLOR_BGR2RGB)
    print('✅ NumPy-OpenCV integration working')
    
    print('\\n🎉 All packages working correctly!')
    
except Exception as e:
    print(f'❌ Test failed: {e}')
    exit(1)
"""
    
    if run_command(f"python3 -c \"{test_code}\"", "Testing package compatibility"):
        print("\n" + "=" * 60)
        print("    FIX COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ NumPy compatibility issues resolved")
        print("✅ All packages are working correctly")
        print("\nNext steps:")
        print("1. Test: python3 simple_eye_mouse.py")
        print("2. Run: python3 test_system.py")
        print("3. Launch: python3 main.py")
    else:
        print("\n❌ Fix verification failed")
        print("Try running the full fix script: ./fix_numpy_compatibility.sh")
        sys.exit(1)

if __name__ == "__main__":
    main()
