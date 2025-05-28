#!/usr/bin/env python3
"""
Test Script for Eye Tracking Click Fix
Verifies that automatic clicking issues have been resolved
"""

import sys
import time
import logging
import threading
from typing import Dict, Any

# Import our modules
from config_manager import ConfigManager
try:
    from eye_tracker import EyeTracker
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    from eye_tracker_opencv import EyeTrackerOpenCV as EyeTracker
    MEDIAPIPE_AVAILABLE = False

from gesture_controller import GestureController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ClickFixTester:
    def __init__(self):
        """Initialize the click fix tester"""
        self.config = ConfigManager()
        self.eye_tracker = EyeTracker(self.config)
        self.gesture_controller = GestureController(self.config)
        
        self.is_running = False
        self.test_duration = 30  # seconds
        self.stats = {
            "frames_processed": 0,
            "gestures_detected": 0,
            "false_positives": 0,
            "start_time": None
        }
        
    def run_test(self):
        """Run the click sensitivity test"""
        print("=" * 60)
        print("EYE TRACKING CLICK FIX TEST")
        print("=" * 60)
        print(f"Testing for {self.test_duration} seconds...")
        print("Instructions:")
        print("- Look around normally (cursor should move smoothly)")
        print("- Blink naturally (should NOT trigger clicks)")
        print("- Try deliberate left eye wink (should trigger left click)")
        print("- Try deliberate right eye wink (should trigger right click)")
        print("- Try deliberate both-eye blink (should trigger middle click)")
        print("- Tilt head left/right (should trigger scrolling)")
        print("- Press Ctrl+C to stop early")
        print("=" * 60)
        
        # Initialize camera
        if not self.eye_tracker.initialize_camera():
            print("ERROR: Failed to initialize camera")
            return False
            
        self.is_running = True
        self.stats["start_time"] = time.time()
        
        try:
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self._monitor_stats, daemon=True)
            monitor_thread.start()
            
            # Main test loop
            while self.is_running and (time.time() - self.stats["start_time"]) < self.test_duration:
                frame, tracking_data = self.eye_tracker.process_frame()
                
                if frame is not None and tracking_data.get("eye_position"):
                    self.stats["frames_processed"] += 1
                    
                    # Process gestures
                    gesture_actions = self.gesture_controller.process_tracking_data(tracking_data)
                    
                    if gesture_actions:
                        self.stats["gestures_detected"] += len(gesture_actions)
                        for action in gesture_actions:
                            self._log_gesture(action)
                
                time.sleep(0.033)  # ~30 FPS
                
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
        except Exception as e:
            print(f"Test error: {e}")
        finally:
            self.is_running = False
            self.eye_tracker.cleanup()
            
        self._print_results()
        return True
        
    def _monitor_stats(self):
        """Monitor and display real-time statistics"""
        while self.is_running:
            elapsed = time.time() - self.stats["start_time"]
            fps = self.stats["frames_processed"] / elapsed if elapsed > 0 else 0
            
            print(f"\rElapsed: {elapsed:.1f}s | FPS: {fps:.1f} | Gestures: {self.stats['gestures_detected']}", end="")
            time.sleep(1)
            
    def _log_gesture(self, action: Dict[str, Any]):
        """Log detected gestures"""
        gesture_type = action.get("type", "unknown")
        action_name = action.get("action", "unknown")
        timestamp = action.get("timestamp", time.time())
        
        elapsed = timestamp - self.stats["start_time"]
        print(f"\n[{elapsed:.1f}s] GESTURE: {gesture_type} -> {action_name}")
        
        # Check for potential false positives
        if gesture_type in ["single_blink", "double_blink"] and action_name in ["left_click", "right_click"]:
            self.stats["false_positives"] += 1
            print(f"  WARNING: Potential false positive detected!")
            
    def _print_results(self):
        """Print test results"""
        elapsed = time.time() - self.stats["start_time"]
        avg_fps = self.stats["frames_processed"] / elapsed if elapsed > 0 else 0
        
        print("\n" + "=" * 60)
        print("TEST RESULTS")
        print("=" * 60)
        print(f"Test Duration: {elapsed:.1f} seconds")
        print(f"Frames Processed: {self.stats['frames_processed']}")
        print(f"Average FPS: {avg_fps:.1f}")
        print(f"Total Gestures Detected: {self.stats['gestures_detected']}")
        print(f"Potential False Positives: {self.stats['false_positives']}")
        
        # Get gesture controller stats
        gesture_stats = self.gesture_controller.get_gesture_stats()
        print(f"\nGesture Breakdown:")
        print(f"  Left Clicks: {gesture_stats['left_clicks']}")
        print(f"  Right Clicks: {gesture_stats['right_clicks']}")
        print(f"  Middle Clicks: {gesture_stats['middle_clicks']}")
        print(f"  Scrolls: {gesture_stats['scrolls']}")
        
        # Evaluate results
        print(f"\nEVALUATION:")
        if self.stats["false_positives"] == 0:
            print("✅ EXCELLENT: No false positive clicks detected!")
        elif self.stats["false_positives"] <= 2:
            print("✅ GOOD: Very few false positives detected")
        elif self.stats["false_positives"] <= 5:
            print("⚠️  FAIR: Some false positives detected, may need tuning")
        else:
            print("❌ POOR: Too many false positives, needs adjustment")
            
        if avg_fps >= 25:
            print("✅ PERFORMANCE: Excellent frame rate")
        elif avg_fps >= 15:
            print("✅ PERFORMANCE: Good frame rate")
        else:
            print("⚠️  PERFORMANCE: Low frame rate, may affect responsiveness")
            
        print("=" * 60)

def main():
    """Main test function"""
    try:
        tester = ClickFixTester()
        success = tester.run_test()
        
        if success:
            print("\nTest completed successfully!")
            print("If you experienced fewer accidental clicks, the fix is working!")
        else:
            print("\nTest failed to complete")
            return 1
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
