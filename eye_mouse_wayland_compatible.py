#!/usr/bin/env python3
"""
Wayland-Compatible Eye-Controlled Mouse
Uses multiple backends for maximum compatibility across different display servers
"""

import cv2
import mediapipe as mp
import time
import numpy as np
import logging
import os
import sys
import subprocess
from collections import deque

# Try different mouse control backends
MOUSE_BACKEND = None

def setup_mouse_backend():
    """Setup the best available mouse control backend"""
    global MOUSE_BACKEND
    
    # Try xdotool first (works well with Wayland)
    try:
        subprocess.run(['xdotool', '--version'], capture_output=True, check=True)
        MOUSE_BACKEND = 'xdotool'
        print("✅ Using xdotool backend (Wayland compatible)")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try PyAutoGUI
    try:
        import pyautogui
        # Test if it actually works
        pos = pyautogui.position()
        pyautogui.moveRel(1, 1)
        new_pos = pyautogui.position()
        pyautogui.moveRel(-1, -1)
        
        if pos != new_pos:  # Mouse actually moved
            MOUSE_BACKEND = 'pyautogui'
            print("✅ Using PyAutoGUI backend")
            return True
        else:
            print("⚠️  PyAutoGUI detected but mouse movement not working")
    except Exception as e:
        print(f"⚠️  PyAutoGUI not working: {e}")
    
    print("❌ No working mouse backend found!")
    print("Install xdotool: sudo dnf install xdotool")
    return False

def move_mouse(x, y):
    """Move mouse using the best available backend"""
    try:
        if MOUSE_BACKEND == 'xdotool':
            subprocess.run(['xdotool', 'mousemove', str(int(x)), str(int(y))], 
                         capture_output=True, check=True)
        elif MOUSE_BACKEND == 'pyautogui':
            import pyautogui
            pyautogui.moveTo(x, y)
        return True
    except Exception as e:
        logging.error(f"Mouse movement error: {e}")
        return False

def click_mouse():
    """Click mouse using the best available backend"""
    try:
        if MOUSE_BACKEND == 'xdotool':
            subprocess.run(['xdotool', 'click', '1'], capture_output=True, check=True)
        elif MOUSE_BACKEND == 'pyautogui':
            import pyautogui
            pyautogui.click()
        return True
    except Exception as e:
        logging.error(f"Mouse click error: {e}")
        return False

def get_screen_size():
    """Get screen size using the best available method"""
    try:
        if MOUSE_BACKEND == 'xdotool':
            result = subprocess.run(['xdotool', 'getdisplaygeometry'], 
                                  capture_output=True, text=True, check=True)
            width, height = map(int, result.stdout.strip().split())
            return (width, height)
        elif MOUSE_BACKEND == 'pyautogui':
            import pyautogui
            return pyautogui.size()
    except Exception as e:
        logging.error(f"Screen size detection error: {e}")
        return (1920, 1080)  # Fallback

class WaylandEyeMouse:
    def __init__(self):
        """Initialize Wayland-compatible eye mouse"""
        print("🚀 Initializing Wayland-Compatible Eye Mouse...")
        
        # Setup mouse backend
        if not setup_mouse_backend():
            sys.exit(1)
        
        # Get screen size
        self.screen_w, self.screen_h = get_screen_size()
        print(f"Screen resolution: {self.screen_w}x{self.screen_h}")
        
        # Initialize MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        
        # Initialize camera
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            print("❌ Cannot open camera")
            sys.exit(1)
        
        # Configure camera
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Settings
        self.sensitivity = 2.0
        self.dead_zone = 0.02
        
        # Smoothing
        self.position_buffer = deque(maxlen=8)
        self.blink_buffer = deque(maxlen=5)
        
        # Performance
        self.frame_count = 0
        self.start_time = time.time()
        
        # Blink detection
        self.blink_threshold = 0.004
        self.last_click_time = 0
        self.click_cooldown = 1.0
        
        print("✅ Wayland Eye Mouse initialized!")
        self.print_controls()
    
    def get_iris_position(self, landmarks):
        """Get iris position with fallback methods"""
        try:
            if len(landmarks) > 475:
                right_iris = landmarks[475]
                if len(landmarks) > 468:
                    left_iris = landmarks[468]
                    # Weighted average
                    avg_x = right_iris.x * 0.7 + left_iris.x * 0.3
                    avg_y = right_iris.y * 0.7 + left_iris.y * 0.3
                    return (avg_x, avg_y)
                else:
                    return (right_iris.x, right_iris.y)
        except Exception as e:
            logging.error(f"Error getting iris position: {e}")
        return None
    
    def apply_smoothing(self, position):
        """Apply smoothing to reduce jitter"""
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
        """Map eye position to screen coordinates"""
        eye_x, eye_y = eye_pos
        
        # Apply dead zone
        center_x, center_y = 0.5, 0.5
        offset_x = eye_x - center_x
        offset_y = eye_y - center_y
        
        if abs(offset_x) < self.dead_zone:
            offset_x = 0
        if abs(offset_y) < self.dead_zone:
            offset_y = 0
        
        # Map to screen
        screen_x = (center_x + offset_x) * self.screen_w * self.sensitivity
        screen_y = (center_y + offset_y) * self.screen_h * self.sensitivity
        
        # Clamp to bounds
        screen_x = max(0, min(self.screen_w - 1, screen_x))
        screen_y = max(0, min(self.screen_h - 1, screen_y))
        
        return (int(screen_x), int(screen_y))
    
    def detect_blink(self, landmarks):
        """Detect blinks for clicking"""
        try:
            left_ratio = abs(landmarks[159].y - landmarks[145].y)
            right_ratio = abs(landmarks[386].y - landmarks[374].y)
            avg_ratio = (left_ratio + right_ratio) / 2
            
            self.blink_buffer.append(avg_ratio)
            
            if len(self.blink_buffer) < 3:
                return False
            
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
        print("- Press 'r' to reset smoothing")
    
    def run(self):
        """Main application loop"""
        print("\n🚀 Starting eye tracking...")
        print("Look at the camera and move your eyes to control the cursor")
        
        try:
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                # Process frame
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    
                    # Get iris position
                    iris_pos = self.get_iris_position(landmarks)
                    if iris_pos:
                        # Apply smoothing and mapping
                        smooth_pos = self.apply_smoothing(iris_pos)
                        screen_x, screen_y = self.map_to_screen(smooth_pos)
                        
                        # Move cursor
                        if move_mouse(screen_x, screen_y):
                            # Debug output
                            if self.frame_count % 30 == 0:
                                print(f"👁️  Eye: ({iris_pos[0]:.3f}, {iris_pos[1]:.3f}) -> 🖱️  Screen: ({screen_x}, {screen_y})")
                    
                    # Detect blinks
                    current_time = time.time()
                    if (self.detect_blink(landmarks) and 
                        current_time - self.last_click_time > self.click_cooldown):
                        
                        if click_mouse():
                            self.last_click_time = current_time
                            print("👆 Click detected!")
                    
                    # Draw landmarks
                    self.mp_drawing.draw_landmarks(
                        frame, results.multi_face_landmarks[0],
                        self.mp_face_mesh.FACEMESH_IRISES,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                    )
                
                # Draw UI
                self.draw_ui_info(frame)
                
                # Display
                cv2.imshow('Wayland Eye Mouse', frame)
                
                # Handle keys
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
                    print("Smoothing reset")
                
                self.frame_count += 1
        
        except KeyboardInterrupt:
            print("\n⏹️  Stopped by user")
        finally:
            self.cleanup()
    
    def draw_ui_info(self, frame):
        """Draw UI information"""
        elapsed = time.time() - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        info_lines = [
            f"FPS: {fps:.1f}",
            f"Backend: {MOUSE_BACKEND}",
            f"Sensitivity: {self.sensitivity:.1f}",
            f"Frames: {self.frame_count}"
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
        eye_mouse = WaylandEyeMouse()
        eye_mouse.run()
    except Exception as e:
        print(f"❌ Failed to start: {e}")

if __name__ == "__main__":
    main()
