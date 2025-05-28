#!/usr/bin/env python3
"""
Test Latest Package Versions Compatibility
Tests the latest versions of MediaPipe, OpenCV, and NumPy for compatibility
"""

import subprocess
import sys
import tempfile
import os

def test_package_combination(numpy_version, opencv_version, mediapipe_version):
    """Test a specific combination of package versions"""
    print(f"\n🧪 Testing: NumPy {numpy_version}, OpenCV {opencv_version}, MediaPipe {mediapipe_version}")
    
    # Create a temporary virtual environment
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = os.path.join(temp_dir, "test_env")
        
        try:
            # Create virtual environment
            subprocess.run([sys.executable, "-m", "venv", venv_path], 
                         check=True, capture_output=True)
            
            # Get pip path
            if os.name == 'nt':  # Windows
                pip_path = os.path.join(venv_path, "Scripts", "pip")
                python_path = os.path.join(venv_path, "Scripts", "python")
            else:  # Unix/Linux
                pip_path = os.path.join(venv_path, "bin", "pip")
                python_path = os.path.join(venv_path, "bin", "python")
            
            # Install packages
            packages = [
                f"numpy{numpy_version}",
                f"opencv-python{opencv_version}",
                f"mediapipe{mediapipe_version}"
            ]
            
            for package in packages:
                result = subprocess.run([pip_path, "install", package], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"❌ Failed to install {package}: {result.stderr}")
                    return False
            
            # Test imports
            test_code = """
import warnings
warnings.filterwarnings('ignore')

try:
    import numpy as np
    import cv2
    import mediapipe as mp
    
    print(f"NumPy: {np.__version__}")
    print(f"OpenCV: {cv2.__version__}")
    print(f"MediaPipe: {mp.__version__}")
    
    # Test basic functionality
    test_array = np.zeros((10, 10, 3), dtype=np.uint8)
    result = cv2.cvtColor(test_array, cv2.COLOR_BGR2RGB)
    
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)
    
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    exit(1)
"""
            
            result = subprocess.run([python_path, "-c", test_code], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Combination works!")
                print(result.stdout)
                return True
            else:
                print("❌ Combination failed!")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Test setup failed: {e}")
            return False

def main():
    """Test various package combinations"""
    print("=" * 60)
    print("    Latest Package Versions Compatibility Test")
    print("=" * 60)
    
    # Test combinations based on research findings
    test_combinations = [
        # Latest versions (Feb 2025)
        (">=1.24.0,<2.0.0", "==4.10.0.84", "==0.10.21"),
        
        # Try with NumPy 2.0 (might fail with MediaPipe)
        (">=2.0.0", "==4.10.0.84", "==0.10.21"),
        
        # Conservative stable versions
        (">=1.21.0,<2.0.0", "==4.8.1.78", "==0.10.7"),
        
        # Latest OpenCV with older MediaPipe
        (">=1.24.0,<2.0.0", "==4.10.0.84", "==0.10.7"),
    ]
    
    successful_combinations = []
    
    for i, (numpy_ver, opencv_ver, mediapipe_ver) in enumerate(test_combinations, 1):
        print(f"\n{'='*20} Test {i}/{len(test_combinations)} {'='*20}")
        
        if test_package_combination(numpy_ver, opencv_ver, mediapipe_ver):
            successful_combinations.append((numpy_ver, opencv_ver, mediapipe_ver))
    
    print("\n" + "=" * 60)
    print("                    TEST RESULTS")
    print("=" * 60)
    
    if successful_combinations:
        print("✅ Working combinations:")
        for i, (numpy_ver, opencv_ver, mediapipe_ver) in enumerate(successful_combinations, 1):
            print(f"{i}. NumPy {numpy_ver}, OpenCV {opencv_ver}, MediaPipe {mediapipe_ver}")
        
        print(f"\n🎉 Found {len(successful_combinations)} working combination(s)!")
        
        # Recommend the best combination
        if successful_combinations:
            best = successful_combinations[0]
            print(f"\n🏆 Recommended combination:")
            print(f"   NumPy: {best[0]}")
            print(f"   OpenCV: {best[1]}")
            print(f"   MediaPipe: {best[2]}")
    else:
        print("❌ No working combinations found!")
        print("\nTry using the conservative requirements:")
        print("   numpy>=1.21.0,<2.0.0")
        print("   opencv-python==4.8.1.78")
        print("   mediapipe==0.10.7")

if __name__ == "__main__":
    main()
