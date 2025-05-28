#!/usr/bin/env python3
"""
Quick test script to verify the verified setup is working
"""

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing package imports...")
    
    try:
        import numpy as np
        print(f"✅ NumPy {np.__version__} imported successfully")
        
        # Check NumPy version compatibility
        major_version = int(np.__version__.split('.')[0])
        if major_version >= 2:
            print("❌ WARNING: NumPy 2.x detected - MediaPipe may have issues")
        else:
            print("✅ NumPy 1.x confirmed - MediaPipe compatible")
            
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import cv2
        print(f"✅ OpenCV {cv2.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import mediapipe as mp
        print(f"✅ MediaPipe {mp.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ MediaPipe import failed: {e}")
        return False
    
    try:
        import pynput
        print("✅ pynput imported successfully")
    except ImportError as e:
        print(f"❌ pynput import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality"""
    print("\n🔧 Testing basic functionality...")
    
    try:
        import numpy as np
        import cv2
        
        # Test OpenCV-NumPy integration
        test_array = np.zeros((10, 10, 3), dtype=np.uint8)
        result = cv2.cvtColor(test_array, cv2.COLOR_BGR2RGB)
        print("✅ OpenCV-NumPy integration working")
        
    except Exception as e:
        print(f"❌ OpenCV-NumPy integration failed: {e}")
        return False
    
    try:
        import mediapipe as mp
        
        # Test MediaPipe initialization (without camera)
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print("✅ MediaPipe face mesh initialization working")
        
    except Exception as e:
        print(f"❌ MediaPipe initialization failed: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("=" * 60)
    print("    VERIFIED SETUP TEST")
    print("    Eye-Controlled Interface Environment")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        return False
    
    # Test functionality
    if not test_basic_functionality():
        print("\n❌ Functionality tests failed!")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("✅ Your verified environment is ready to use!")
    print("")
    print("🚀 You can now run:")
    print("  python simple_eye_mouse.py    # Simple eye mouse")
    print("  python main.py                # Full application")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
