#!/usr/bin/env python3
"""
Fixed Eye-Controlled Mouse with Comprehensive Error Handling
This version addresses all known issues with eye tracking mouse control
"""

import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np
import logging
import os
import sys
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FixedEyeMouse:
    def __init__(self):
        """Initialize with comprehensive error handling and system compatibility"""
        print("🚀 Initializing Fixed Eye Mouse...")
        
        # Check system compatibility
        self.check_system_compatibility()
        
        # Initialize MediaPipe with optimal settings
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.8,  # Higher for stability
            min_tracking_confidence=0.8
        )
        
        # Camera initialization with error handling
        self.camera = None
        self.initialize_camera()
        
        # Screen setup
        self.screen_w, self.screen_h = pyautogui.size()
        print(f"Screen resolution: {self.screen_w}x{self.screen_h}")
        
        # Configure PyAutoGUI for optimal performance
        self.setup_mouse_control()
        
        # Tracking parameters
        self.sensitivity = 2.0  # Higher sensitivity
        self.smoothing_factor = 0.8
        self.dead_zone = 0.015  # Small dead zone
        
        # Smoothing buffers
        self.position_buffer = deque(maxlen=10)
        self.blink_buffer = deque(maxlen=5)
        
        # Performance monitoring
        self.frame_count = 0
        self.start_time = time.time()
        self.last_mouse_move = time.time()
        
        # Blink detection
        self.blink_threshold = 0.004
        self.last_click_time = 0
        self.click_cooldown = 1.0
        
        print("✅ Fixed Eye Mouse initialized successfully!")
        self.print_controls()
    
    def check_system_compatibility(self):
        """Check system compatibility and provide recommendations"""
        print("🔍 Checking system compatibility...")
        
        session_type = os.environ.get('XDG_SESSION_TYPE', 'unknown')
        if session_type == 'wayland':
            print("⚠️  WARNING: Running on Wayland")
            print("   For best compatibility, consider switching to X11 session")
            print("   Or set environment variables: GDK_BACKEND=x11")
        
        # Check if running in virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Running in virtual environment")
        else:
            print("⚠️  Not running in virtual environment - consider using one")
    
    def initialize_camera(self):
        """Initialize camera with comprehensive error handling"""
        print("📷 Initializing camera...")
        
        try:
            # Try different camera indices
            for camera_id in [0, 1, 2]:
                self.camera = cv2.VideoCapture(camera_id)
                if self.camera.isOpened():
                    print(f"✅ Camera {camera_id} opened successfully")
                    break
                self.camera.release()
            else:
                raise Exception("No camera found")
            
            # Configure camera for optimal performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize latency
            
            # Test camera
            ret, frame = self.camera.read()
            if not ret:
                raise Exception("Cannot read from camera")
            
            print(f"✅ Camera configured: {frame.shape}")
            
        except Exception as e:
            print(f"❌ Camera initialization failed: {e}")
            sys.exit(1)
    
    def setup_mouse_control(self):
        """Setup mouse control with error handling"""
        print("🖱️  Setting up mouse control...")
        
        try:
            # Configure PyAutoGUI
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0.001  # Minimal pause
            
            # Test mouse control
            current_pos = pyautogui.position()
            print(f"Current mouse position: {current_pos}")
            
            # Test movement
            pyautogui.moveRel(1, 1)
            pyautogui.moveRel(-1, -1)
            
            print("✅ Mouse control test passed")
            
        except Exception as e:
            print(f"❌ Mouse control setup failed: {e}")
            print("Try running with: GDK_BACKEND=x11 python eye_mouse_fixed.py")
            sys.exit(1)
    
    def get_iris_position(self, landmarks):
        """Get iris position using multiple methods for robustness"""
        try:
            # Primary method: Right iris center
            if len(landmarks) > 475:
                right_iris = landmarks[475]
                
                # Secondary method: Average both iris centers
                if len(landmarks) > 468:
                    left_iris = landmarks[468]
                    
                    # Weighted average (prefer right iris)
                    avg_x = right_iris.x * 0.7 + left_iris.x * 0.3
                    avg_y = right_iris.y * 0.7 + left_iris.y * 0.3
                    
                    return (avg_x, avg_y)
                else:
                    return (right_iris.x, right_iris.y)
            
            # Fallback: Eye corner method
            elif len(landmarks) > 133:
                left_corner = landmarks[33]
                right_corner = landmarks[133]
                
                center_x = (left_corner.x + right_corner.x) / 2
                center_y = (left_corner.y + right_corner.y) / 2
                
                return (center_x, center_y)
                
        except Exception as e:
            logging.error(f"Error getting iris position: {e}")
        
        return None
    
    def apply_smoothing(self, position):
        """Apply advanced smoothing to reduce jitter"""
        self.position_buffer.append(position)
        
        if len(self.position_buffer) < 2:
            return position
        
        # Exponential weighted average
        weights = np.exp(np.linspace(-1, 0, len(self.position_buffer)))
        weights /= weights.sum()
        
        smooth_x = sum(w * pos[0] for w, pos in zip(weights, self.position_buffer))
        smooth_y = sum(w * pos[1] for w, pos in zip(weights, self.position_buffer))
        
        return (smooth_x, smooth_y)
    
    def map_to_screen(self, eye_pos):
        """Map eye position to screen coordinates with dead zone"""
        eye_x, eye_y = eye_pos
        
        # Apply dead zone around center
        center_x, center_y = 0.5, 0.5
        offset_x = eye_x - center_x
        offset_y = eye_y - center_y
        
        # Dead zone
        if abs(offset_x) < self.dead_zone:
            offset_x = 0
        if abs(offset_y) < self.dead_zone:
            offset_y = 0
        
        # Apply sensitivity
        screen_x = (center_x + offset_x) * self.screen_w * self.sensitivity
        screen_y = (center_y + offset_y) * self.screen_h * self.sensitivity
        
        # Clamp to screen bounds
        screen_x = max(0, min(self.screen_w - 1, screen_x))
        screen_y = max(0, min(self.screen_h - 1, screen_y))
        
        return (int(screen_x), int(screen_y))
    
    def detect_blink(self, landmarks):
        """Detect blinks for clicking"""
        try:
            # Left eye ratio
            left_top = landmarks[159]
            left_bottom = landmarks[145]
            left_ratio = abs(left_top.y - left_bottom.y)
            
            # Right eye ratio
            right_top = landmarks[386]
            right_bottom = landmarks[374]
            right_ratio = abs(right_top.y - right_bottom.y)
            
            # Average ratio
            avg_ratio = (left_ratio + right_ratio) / 2
            self.blink_buffer.append(avg_ratio)
            
            if len(self.blink_buffer) < 3:
                return False
            
            # Check if current ratio is below threshold
            current_avg = sum(self.blink_buffer) / len(self.blink_buffer)
            return current_avg < self.blink_threshold
            
        except Exception as e:
            logging.error(f"Blink detection error: {e}")
            return False
    
    def print_controls(self):
        """Print control instructions"""
        print("\n🎮 Controls:")
        print("- Look around to move cursor")
        print("- Blink to click")
        print("- Press 'q' to quit")
        print("- Press '+' to increase sensitivity")
        print("- Press '-' to decrease sensitivity")
        print("- Press 'r' to reset position buffer")
        print("- Press 'h' to show this help")
    
    def run(self):
        """Main application loop"""
        print("\n🚀 Starting eye tracking...")
        print("Look at the camera and move your eyes to control the cursor")
        
        try:
            while True:
                frame_start = time.time()
                
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process with MediaPipe
                results = self.face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    
                    # Get iris position
                    iris_pos = self.get_iris_position(landmarks)
                    if iris_pos:
                        # Apply smoothing
                        smooth_pos = self.apply_smoothing(iris_pos)
                        
                        # Map to screen
                        screen_x, screen_y = self.map_to_screen(smooth_pos)
                        
                        # Move cursor
                        try:
                            pyautogui.moveTo(screen_x, screen_y)
                            self.last_mouse_move = time.time()
                            
                            # Debug output
                            if self.frame_count % 30 == 0:
                                print(f"Eye: ({iris_pos[0]:.3f}, {iris_pos[1]:.3f}) -> Screen: ({screen_x}, {screen_y})")
                        
                        except Exception as e:
                            if self.frame_count % 60 == 0:
                                logging.error(f"Mouse movement error: {e}")
                    
                    # Detect blinks
                    current_time = time.time()
                    if (self.detect_blink(landmarks) and 
                        current_time - self.last_click_time > self.click_cooldown):
                        
                        try:
                            pyautogui.click()
                            self.last_click_time = current_time
                            print("👆 Click detected!")
                        except Exception as e:
                            logging.error(f"Click error: {e}")
                    
                    # Draw landmarks
                    self.mp_drawing.draw_landmarks(
                        frame, results.multi_face_landmarks[0],
                        self.mp_face_mesh.FACEMESH_IRISES,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                    )
                
                # Draw UI info
                self.draw_ui_info(frame)
                
                # Display frame
                cv2.imshow('Fixed Eye Mouse', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('+'):
                    self.sensitivity = min(3.0, self.sensitivity + 0.1)
                    print(f"Sensitivity: {self.sensitivity:.1f}")
                elif key == ord('-'):
                    self.sensitivity = max(0.5, self.sensitivity - 0.1)
                    print(f"Sensitivity: {self.sensitivity:.1f}")
                elif key == ord('r'):
                    self.position_buffer.clear()
                    print("Position buffer reset")
                elif key == ord('h'):
                    self.print_controls()
                
                self.frame_count += 1
                
                # Maintain target FPS
                frame_time = time.time() - frame_start
                target_frame_time = 1.0 / 30  # 30 FPS
                if frame_time < target_frame_time:
                    time.sleep(target_frame_time - frame_time)
        
        except KeyboardInterrupt:
            print("\n⏹️  Stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logging.error(f"Application error: {e}", exc_info=True)
        finally:
            self.cleanup()
    
    def draw_ui_info(self, frame):
        """Draw UI information on frame"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        info_lines = [
            f"FPS: {fps:.1f}",
            f"Sensitivity: {self.sensitivity:.1f}",
            f"Frames: {self.frame_count}",
            f"Mouse active: {time.time() - self.last_mouse_move < 1.0}",
            "Press 'h' for help"
        ]
        
        for i, line in enumerate(info_lines):
            cv2.putText(frame, line, (10, 30 + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    def cleanup(self):
        """Clean up resources"""
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        print("✅ Cleanup completed")

def main():
    """Main entry point"""
    try:
        eye_mouse = FixedEyeMouse()
        eye_mouse.run()
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        logging.error(f"Startup error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
