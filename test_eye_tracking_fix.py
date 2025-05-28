#!/usr/bin/env python3
"""
Test Eye Tracking Fix
Quick test to verify eye tracking cursor movement is working
"""

import cv2
import mediapipe as mp
import pyautogui
import time

# Disable PyAutoGUI failsafe
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.001

class EyeTrackingTest:
    def __init__(self):
        # MediaPipe setup
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Settings
        self.sensitivity = 1.2
        self.frame_count = 0
        self.start_time = time.time()
        
        print("🔍 Eye Tracking Test Initialized")
        print(f"   Screen: {self.screen_w}x{self.screen_h}")
        print(f"   Sensitivity: {self.sensitivity}")
        print("\n👁️ Instructions:")
        print("   - Look around to move cursor")
        print("   - Press 'q' to quit")
        print("   - Press '+' to increase sensitivity")
        print("   - Press '-' to decrease sensitivity")

    def draw_debug_info(self, frame, landmarks):
        """Draw debug information"""
        h, w, _ = frame.shape
        
        # Performance info
        current_time = time.time()
        elapsed = current_time - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        # Current cursor position
        cursor_x, cursor_y = pyautogui.position()
        
        debug_info = [
            f"FPS: {fps:.1f}",
            f"Sensitivity: {self.sensitivity:.1f}",
            f"Cursor: ({cursor_x}, {cursor_y})",
            f"Frame: {self.frame_count}"
        ]
        
        # Draw debug text
        for i, text in enumerate(debug_info):
            cv2.putText(frame, text, (10, 30 + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Draw iris landmark if available
        if len(landmarks) > 475:
            iris_center = landmarks[475]
            iris_x = int(iris_center.x * w)
            iris_y = int(iris_center.y * h)
            
            # Draw iris center
            cv2.circle(frame, (iris_x, iris_y), 5, (0, 255, 255), -1)
            cv2.putText(frame, "Iris Center", (iris_x + 10, iris_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            # Show iris coordinates
            cv2.putText(frame, f"Iris: ({iris_center.x:.3f}, {iris_center.y:.3f})", 
                       (10, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Draw crosshair at center
        center_x, center_y = w // 2, h // 2
        cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), (255, 0, 0), 2)
        cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), (255, 0, 0), 2)
        
        return frame

    def test_eye_tracking(self):
        """Test eye tracking cursor movement"""
        print("\n🚀 Starting eye tracking test...")
        print("   Look at different parts of the screen")
        print("   The cursor should follow your eye movement")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Convert to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process with MediaPipe
                results = self.face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    
                    # Get iris position (right iris center - landmark 475)
                    if len(landmarks) > 475:
                        iris_center = landmarks[475]
                        
                        # Convert to screen coordinates with sensitivity
                        # This is the EXACT same method as working simple_eye_mouse.py
                        raw_x = iris_center.x * self.screen_w * self.sensitivity
                        raw_y = iris_center.y * self.screen_h * self.sensitivity
                        
                        # Clamp to screen bounds
                        screen_x = max(0, min(self.screen_w - 1, int(raw_x)))
                        screen_y = max(0, min(self.screen_h - 1, int(raw_y)))
                        
                        # Move cursor directly
                        pyautogui.moveTo(screen_x, screen_y)
                        
                        # Visual feedback
                        cv2.putText(frame, f"Moving to: ({screen_x}, {screen_y})", 
                                   (10, frame.shape[0] - 60), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # Draw debug info
                    frame = self.draw_debug_info(frame, landmarks)
                
                else:
                    # No face detected
                    cv2.putText(frame, "No face detected", (10, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Display frame
                cv2.imshow('Eye Tracking Test', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC
                    break
                elif key == ord('+') or key == ord('='):
                    self.sensitivity = min(3.0, self.sensitivity + 0.1)
                    print(f"👁️ Sensitivity increased to {self.sensitivity:.1f}")
                elif key == ord('-') or key == ord('_'):
                    self.sensitivity = max(0.1, self.sensitivity - 0.1)
                    print(f"👁️ Sensitivity decreased to {self.sensitivity:.1f}")
                elif key == ord(' '):
                    # Center cursor
                    pyautogui.moveTo(self.screen_w // 2, self.screen_h // 2)
                    print("🎯 Cursor centered")
                
                self.frame_count += 1
        
        except KeyboardInterrupt:
            print("\n⏹️ Test stopped by user")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
        # Final stats
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        print(f"📊 Test Results:")
        print(f"   Runtime: {elapsed:.1f}s")
        print(f"   Frames: {self.frame_count}")
        print(f"   Average FPS: {avg_fps:.1f}")
        print("✅ Test completed")

def main():
    """Main test function"""
    print("=" * 60)
    print("    👁️ EYE TRACKING CURSOR MOVEMENT TEST")
    print("=" * 60)
    
    try:
        tester = EyeTrackingTest()
        tester.test_eye_tracking()
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()
