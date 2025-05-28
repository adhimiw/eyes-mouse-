#!/usr/bin/env python3
"""
Debug Hybrid Eye Tracking
Test the exact same method as simple_eye_mouse.py in hybrid controller
"""

import cv2
import mediapipe as mp
import pyautogui
import time

# Disable PyAutoGUI failsafe
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.001

class DebugHybridEyeTracking:
    def __init__(self):
        print("🔍 Debug Hybrid Eye Tracking")
        
        # MediaPipe setup - EXACT same as simple_eye_mouse.py
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,  # Same as simple_eye_mouse.py
            min_tracking_confidence=0.5    # Same as simple_eye_mouse.py
        )
        
        # Camera setup - EXACT same as simple_eye_mouse.py
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Settings - EXACT same as simple_eye_mouse.py
        self.sensitivity = 1.0  # Same default as simple_eye_mouse.py
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()
        
        print(f"   Screen: {self.screen_w}x{self.screen_h}")
        print(f"   Sensitivity: {self.sensitivity}")
        print("\n🎯 This uses EXACT same method as simple_eye_mouse.py")
        print("   If this works, then hybrid controller should work too")

    def run_debug_test(self):
        """Run debug test using EXACT same method as simple_eye_mouse.py"""
        print("\n🚀 Starting debug test...")
        print("   Look around - cursor should move")
        print("   Press 'q' to quit")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read from camera")
                    break
                
                # EXACT same processing as simple_eye_mouse.py
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process with MediaPipe
                results = self.face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    
                    # EXACT same iris detection as simple_eye_mouse.py
                    if len(landmarks) > 475:
                        iris_center = landmarks[475]  # Right iris center
                        
                        # EXACT same coordinate conversion as simple_eye_mouse.py
                        raw_x = iris_center.x * self.screen_w * self.sensitivity
                        raw_y = iris_center.y * self.screen_h * self.sensitivity
                        
                        # EXACT same bounds clamping as simple_eye_mouse.py
                        screen_x = max(0, min(self.screen_w - 1, int(raw_x)))
                        screen_y = max(0, min(self.screen_h - 1, int(raw_y)))
                        
                        # EXACT same cursor movement as simple_eye_mouse.py
                        pyautogui.moveTo(screen_x, screen_y)
                        
                        # Debug info
                        cv2.putText(frame, f"Iris: ({iris_center.x:.3f}, {iris_center.y:.3f})", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(frame, f"Screen: ({screen_x}, {screen_y})", 
                                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(frame, "CURSOR SHOULD BE MOVING", 
                                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                    else:
                        cv2.putText(frame, f"Not enough landmarks: {len(landmarks)}", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, "NO FACE DETECTED", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Performance info
                current_time = time.time()
                elapsed = current_time - self.start_time
                fps = self.frame_count / elapsed if elapsed > 0 else 0
                
                cv2.putText(frame, f"FPS: {fps:.1f}", 
                           (10, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Display frame
                cv2.imshow('Debug Hybrid Eye Tracking', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('+'):
                    self.sensitivity = min(3.0, self.sensitivity + 0.1)
                    print(f"Sensitivity: {self.sensitivity:.1f}")
                elif key == ord('-'):
                    self.sensitivity = max(0.1, self.sensitivity - 0.1)
                    print(f"Sensitivity: {self.sensitivity:.1f}")
                
                self.frame_count += 1
        
        except KeyboardInterrupt:
            print("\n⏹️ Test stopped by user")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
        # Final stats
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        print(f"\n📊 Debug Results:")
        print(f"   Runtime: {elapsed:.1f}s")
        print(f"   Frames: {self.frame_count}")
        print(f"   Average FPS: {avg_fps:.1f}")
        
        if avg_fps > 15:
            print("✅ Performance is good")
        else:
            print("⚠️  Performance might be an issue")

def main():
    """Main debug function"""
    print("=" * 60)
    print("    🔍 DEBUG HYBRID EYE TRACKING")
    print("    Using EXACT same method as simple_eye_mouse.py")
    print("=" * 60)
    
    try:
        debugger = DebugHybridEyeTracking()
        debugger.run_debug_test()
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
