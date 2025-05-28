"""
System Test Suite for Eye-Controlled Interface
Comprehensive testing of all components and functionality
"""

import sys
import time
import logging
import traceback
from typing import Dict, Any, List
import unittest
from unittest.mock import Mock, patch

# Configure logging
logging.basicConfig(level=logging.INFO)

class SystemTestSuite:
    def __init__(self):
        self.test_results = {}
        self.failed_tests = []
        
    def run_all_tests(self):
        """Run all system tests"""
        print("=" * 60)
        print("    Eye-Controlled Interface System Tests")
        print("=" * 60)
        
        tests = [
            ("Dependencies", self.test_dependencies),
            ("Camera Access", self.test_camera_access),
            ("MediaPipe", self.test_mediapipe),
            ("PyAutoGUI", self.test_pyautogui),
            ("Configuration", self.test_configuration),
            ("Eye Tracker", self.test_eye_tracker),
            ("Gesture Controller", self.test_gesture_controller),
            ("Performance Monitor", self.test_performance_monitor),
            ("Streaming Plugins", self.test_streaming_plugins),
            ("UI Components", self.test_ui_components)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 Testing {test_name}...")
            try:
                result = test_func()
                self.test_results[test_name] = result
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                    self.failed_tests.append(test_name)
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                self.test_results[test_name] = False
                self.failed_tests.append(test_name)
                logging.error(f"Test {test_name} failed: {e}", exc_info=True)
        
        self.print_summary()
    
    def test_dependencies(self) -> bool:
        """Test all required dependencies"""
        required_modules = [
            'cv2', 'mediapipe', 'pyautogui', 'numpy', 
            'PIL', 'psutil', 'pynput', 'screeninfo', 'tkinter'
        ]
        
        missing = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        
        if missing:
            print(f"   Missing modules: {', '.join(missing)}")
            return False
        
        print("   All dependencies available")
        return True
    
    def test_camera_access(self) -> bool:
        """Test camera accessibility"""
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("   Camera not accessible")
                return False
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                print("   Camera accessible but cannot read frames")
                return False
            
            print(f"   Camera working - Frame shape: {frame.shape}")
            return True
            
        except Exception as e:
            print(f"   Camera test error: {e}")
            return False
    
    def test_mediapipe(self) -> bool:
        """Test MediaPipe face mesh"""
        try:
            import mediapipe as mp
            import cv2
            import numpy as np
            
            mp_face_mesh = mp.solutions.face_mesh
            face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
            
            # Create a test image
            test_image = np.zeros((480, 640, 3), dtype=np.uint8)
            results = face_mesh.process(test_image)
            
            print("   MediaPipe face mesh initialized successfully")
            return True
            
        except Exception as e:
            print(f"   MediaPipe test error: {e}")
            return False
    
    def test_pyautogui(self) -> bool:
        """Test PyAutoGUI functionality"""
        try:
            import pyautogui
            
            # Test screen size detection
            screen_size = pyautogui.size()
            print(f"   Screen size detected: {screen_size}")
            
            # Test cursor position
            pos = pyautogui.position()
            print(f"   Current cursor position: {pos}")
            
            # Disable failsafe for testing
            pyautogui.FAILSAFE = False
            
            return True
            
        except Exception as e:
            print(f"   PyAutoGUI test error: {e}")
            return False
    
    def test_configuration(self) -> bool:
        """Test configuration management"""
        try:
            from config_manager import ConfigManager
            
            config = ConfigManager()
            
            # Test setting and getting values
            test_value = 1.5
            config.set_setting("test", "value", test_value)
            retrieved_value = config.get_setting("test", "value")
            
            if retrieved_value != test_value:
                print(f"   Config test failed: {retrieved_value} != {test_value}")
                return False
            
            # Test profile switching
            profiles = list(config.profiles.keys())
            print(f"   Available profiles: {profiles}")
            
            return True
            
        except Exception as e:
            print(f"   Configuration test error: {e}")
            return False
    
    def test_eye_tracker(self) -> bool:
        """Test eye tracker initialization"""
        try:
            from config_manager import ConfigManager
            from eye_tracker import EyeTracker
            
            config = ConfigManager()
            tracker = EyeTracker(config)
            
            # Test initialization
            if not hasattr(tracker, 'face_mesh'):
                print("   Eye tracker missing face_mesh")
                return False
            
            print("   Eye tracker initialized successfully")
            return True
            
        except Exception as e:
            print(f"   Eye tracker test error: {e}")
            return False
    
    def test_gesture_controller(self) -> bool:
        """Test gesture controller"""
        try:
            from config_manager import ConfigManager
            from gesture_controller import GestureController
            
            config = ConfigManager()
            controller = GestureController(config)
            
            # Test gesture processing with mock data
            mock_data = {
                "eye_position": (0.5, 0.5),
                "blink_detected": False,
                "tracking_quality": 0.8
            }
            
            actions = controller.process_tracking_data(mock_data)
            print(f"   Gesture controller processed mock data: {len(actions)} actions")
            
            return True
            
        except Exception as e:
            print(f"   Gesture controller test error: {e}")
            return False
    
    def test_performance_monitor(self) -> bool:
        """Test performance monitoring"""
        try:
            from config_manager import ConfigManager
            from performance_monitor import PerformanceMonitor
            
            config = ConfigManager()
            monitor = PerformanceMonitor(config)
            
            # Test performance data collection
            monitor.update_fps(30.0)
            monitor.update_latency(20.0)
            
            stats = monitor.get_current_performance_data()
            print(f"   Performance monitor working - FPS: {stats.get('fps', 0)}")
            
            return True
            
        except Exception as e:
            print(f"   Performance monitor test error: {e}")
            return False
    
    def test_streaming_plugins(self) -> bool:
        """Test streaming platform plugins"""
        try:
            from config_manager import ConfigManager
            from streaming_plugins.netflix_plugin import NetflixPlugin
            from streaming_plugins.youtube_plugin import YouTubePlugin
            
            config = ConfigManager()
            
            # Test Netflix plugin
            netflix = NetflixPlugin(config)
            print(f"   Netflix plugin: {netflix.platform_name}")
            
            # Test YouTube plugin
            youtube = YouTubePlugin(config)
            print(f"   YouTube plugin: {youtube.platform_name}")
            
            return True
            
        except Exception as e:
            print(f"   Streaming plugins test error: {e}")
            return False
    
    def test_ui_components(self) -> bool:
        """Test UI components"""
        try:
            import tkinter as tk
            from config_manager import ConfigManager
            from eye_tracker import EyeTracker
            from gesture_controller import GestureController
            
            # Test basic Tkinter
            root = tk.Tk()
            root.withdraw()  # Hide the window
            
            config = ConfigManager()
            tracker = EyeTracker(config)
            controller = GestureController(config)
            
            # Test UI overlay creation (without showing)
            from ui_overlay import EyeTrackingOverlay
            ui = EyeTrackingOverlay(config, tracker, controller)
            ui.root.withdraw()  # Hide the window
            
            print("   UI components initialized successfully")
            
            # Cleanup
            ui.root.destroy()
            root.destroy()
            
            return True
            
        except Exception as e:
            print(f"   UI components test error: {e}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("                    TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\nFailed Tests: {', '.join(self.failed_tests)}")
            print("\nRecommendations:")
            
            for test in self.failed_tests:
                if test == "Dependencies":
                    print("- Run: python setup.py")
                elif test == "Camera Access":
                    print("- Check camera permissions and connections")
                elif test == "MediaPipe":
                    print("- Reinstall MediaPipe: pip install mediapipe")
                elif test == "PyAutoGUI":
                    print("- Check display settings and permissions")
        else:
            print("\n🎉 All tests passed! System is ready to use.")
        
        print("=" * 60)

def run_performance_benchmark():
    """Run performance benchmark"""
    print("\n🏃 Running Performance Benchmark...")
    
    try:
        from config_manager import ConfigManager
        from eye_tracker import EyeTracker
        import time
        
        config = ConfigManager()
        tracker = EyeTracker(config)
        
        if not tracker.initialize_camera():
            print("❌ Camera initialization failed")
            return
        
        print("📊 Processing 100 frames...")
        start_time = time.time()
        frame_count = 0
        
        for i in range(100):
            frame, data = tracker.process_frame()
            if frame is not None:
                frame_count += 1
        
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time if elapsed_time > 0 else 0
        
        print(f"✅ Benchmark Results:")
        print(f"   Processed Frames: {frame_count}/100")
        print(f"   Time Elapsed: {elapsed_time:.2f}s")
        print(f"   Average FPS: {fps:.1f}")
        print(f"   Frame Processing Time: {(elapsed_time/frame_count)*1000:.1f}ms")
        
        tracker.cleanup()
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")

def main():
    """Main test function"""
    print("Starting system tests...")
    
    # Run system tests
    test_suite = SystemTestSuite()
    test_suite.run_all_tests()
    
    # Ask if user wants to run performance benchmark
    if not test_suite.failed_tests:
        try:
            response = input("\nRun performance benchmark? (y/n): ").lower()
            if response in ['y', 'yes']:
                run_performance_benchmark()
        except KeyboardInterrupt:
            print("\nTests completed.")

if __name__ == "__main__":
    main()
