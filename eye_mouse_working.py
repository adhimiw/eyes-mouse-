#!/usr/bin/env python3
"""
Working Eye-Controlled Mouse with Comprehensive Debugging
This version will actually move the mouse cursor with detailed error tracking
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

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class WorkingEyeMouse:
    def __init__(self):
        """Initialize with comprehensive debugging and error handling"""
        print("🚀 Initializing Working Eye Mouse with Full Debugging...")
        
        # Test xdotool functionality first
        self.test_xdotool()
        
        # Get screen size
        self.screen_w, self.screen_h = self.get_screen_size()
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
        self.sensitivity = 1.0  # Start with 1.0 for testing
        self.dead_zone = 0.05   # Larger dead zone for testing
        
        # Smoothing
        self.position_buffer = deque(maxlen=5)  # Smaller buffer for responsiveness
        self.blink_buffer = deque(maxlen=5)
        
        # Performance and debugging
        self.frame_count = 0
        self.start_time = time.time()
        self.mouse_move_count = 0
        self.mouse_move_success = 0
        self.last_mouse_pos = None
        
        # Blink detection
        self.blink_threshold = 0.004
        self.last_click_time = 0
        self.click_cooldown = 1.0
        
        print("✅ Working Eye Mouse initialized!")
        self.print_controls()
    
    def test_xdotool(self):
        """Comprehensive xdotool testing"""
        print("🔧 Testing xdotool functionality...")
        
        try:
            # Test 1: Get current position
            result = subprocess.run(['xdotool', 'getmouselocation'], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Current mouse position: {result.stdout.strip()}")
            
            # Test 2: Simple movement
            print("🔧 Testing mouse movement...")
            subprocess.run(['xdotool', 'mousemove', '500', '500'], 
                         capture_output=True, check=True)
            
            # Verify movement
            result = subprocess.run(['xdotool', 'getmouselocation'], 
                                  capture_output=True, text=True, check=True)
            new_pos = result.stdout.strip()
            print(f"✅ After movement: {new_pos}")
            
            if "x:500 y:500" in new_pos:
                print("✅ xdotool mouse movement WORKING!")
            else:
                print("⚠️  xdotool movement may have issues")
            
        except Exception as e:
            print(f"❌ xdotool test failed: {e}")
            sys.exit(1)
    
    def get_screen_size(self):
        """Get screen size using xdotool"""
        try:
            result = subprocess.run(['xdotool', 'getdisplaygeometry'], 
                                  capture_output=True, text=True, check=True)
            width, height = map(int, result.stdout.strip().split())
            return (width, height)
        except Exception as e:
            print(f"❌ Screen size detection failed: {e}")
            return (1920, 1080)  # Fallback
    
    def move_mouse_debug(self, x, y):
        """Move mouse with comprehensive debugging"""
        self.mouse_move_count += 1
        
        try:
            # Ensure coordinates are integers and within bounds
            x = max(0, min(self.screen_w - 1, int(x)))
            y = max(0, min(self.screen_h - 1, int(y)))
            
            # Log every movement attempt
            if self.mouse_move_count % 10 == 0:  # Log every 10th movement
                print(f"🖱️  Attempting to move mouse to: ({x}, {y})")
            
            # Execute xdotool command
            result = subprocess.run(['xdotool', 'mousemove', str(x), str(y)], 
                                  capture_output=True, text=True, check=True, timeout=0.1)
            
            # Verify movement (every 30 attempts)
            if self.mouse_move_count % 30 == 0:
                verify_result = subprocess.run(['xdotool', 'getmouselocation'], 
                                             capture_output=True, text=True, check=True)
                actual_pos = verify_result.stdout.strip()
                print(f"🔍 Verification - Sent: ({x}, {y}), Actual: {actual_pos}")
            
            self.mouse_move_success += 1
            self.last_mouse_pos = (x, y)
            return True
            
        except subprocess.TimeoutExpired:
            logging.error(f"Mouse movement timeout: ({x}, {y})")
            return False
        except subprocess.CalledProcessError as e:
            logging.error(f"xdotool error: {e.stderr}")
            return False
        except Exception as e:
            logging.error(f"Mouse movement error: {e}")
            return False
    
    def click_mouse_debug(self):
        """Click mouse with debugging"""
        try:
            print("👆 Attempting mouse click...")
            subprocess.run(['xdotool', 'click', '1'], 
                         capture_output=True, check=True, timeout=0.5)
            print("✅ Mouse click successful!")
            return True
        except Exception as e:
            logging.error(f"Mouse click error: {e}")
            return False
    
    def get_iris_position(self, landmarks):
        """Get iris position with multiple fallback methods"""
        try:
            # Method 1: Right iris center (primary)
            if len(landmarks) > 475:
                right_iris = landmarks[475]
                
                # Method 2: Average both iris centers for stability
                if len(landmarks) > 468:
                    left_iris = landmarks[468]
                    
                    # Simple average for now
                    avg_x = (right_iris.x + left_iris.x) / 2
                    avg_y = (right_iris.y + left_iris.y) / 2
                    
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
        """Simple smoothing to reduce jitter"""
        self.position_buffer.append(position)
        
        if len(self.position_buffer) < 2:
            return position
        
        # Simple moving average
        avg_x = sum(pos[0] for pos in self.position_buffer) / len(self.position_buffer)
        avg_y = sum(pos[1] for pos in self.position_buffer) / len(self.position_buffer)
        
        return (avg_x, avg_y)
    
    def map_to_screen(self, eye_pos):
        """Map eye position to screen coordinates with debugging"""
        eye_x, eye_y = eye_pos
        
        # Apply dead zone around center
        center_x, center_y = 0.5, 0.5
        offset_x = eye_x - center_x
        offset_y = eye_y - center_y
        
        # Apply dead zone
        if abs(offset_x) < self.dead_zone:
            offset_x = 0
        if abs(offset_y) < self.dead_zone:
            offset_y = 0
        
        # Direct mapping with sensitivity
        screen_x = (center_x + offset_x) * self.screen_w * self.sensitivity
        screen_y = (center_y + offset_y) * self.screen_h * self.sensitivity
        
        # Clamp to screen bounds
        screen_x = max(0, min(self.screen_w - 1, screen_x))
        screen_y = max(0, min(self.screen_h - 1, screen_y))
        
        # Debug output every 30 frames
        if self.frame_count % 30 == 0:
            print(f"🎯 Mapping: Eye({eye_x:.3f}, {eye_y:.3f}) -> Offset({offset_x:.3f}, {offset_y:.3f}) -> Screen({screen_x:.0f}, {screen_y:.0f})")
        
        return (int(screen_x), int(screen_y))
    
    def detect_blink(self, landmarks):
        """Simple blink detection"""
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
        print("- Press 't' to test mouse movement")
        print("- Press 'r' to reset smoothing")
    
    def test_mouse_movement(self):
        """Test mouse movement in a pattern"""
        print("🔧 Testing mouse movement pattern...")
        
        test_positions = [
            (100, 100),
            (500, 300),
            (1000, 600),
            (1500, 800),
            (800, 400)
        ]
        
        for i, (x, y) in enumerate(test_positions):
            print(f"Moving to position {i+1}: ({x}, {y})")
            success = self.move_mouse_debug(x, y)
            print(f"Result: {'✅ Success' if success else '❌ Failed'}")
            time.sleep(0.5)
        
        print("🔧 Mouse movement test completed")
    
    def run(self):
        """Main application loop with comprehensive debugging"""
        print("\n🚀 Starting eye tracking with full debugging...")
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
                        success = self.move_mouse_debug(screen_x, screen_y)
                        
                        # Debug output every 30 frames
                        if self.frame_count % 30 == 0:
                            success_rate = (self.mouse_move_success / self.mouse_move_count * 100) if self.mouse_move_count > 0 else 0
                            print(f"📊 Stats: Moves: {self.mouse_move_count}, Success: {self.mouse_move_success} ({success_rate:.1f}%)")
                    
                    # Detect blinks
                    current_time = time.time()
                    if (self.detect_blink(landmarks) and 
                        current_time - self.last_click_time > self.click_cooldown):
                        
                        if self.click_mouse_debug():
                            self.last_click_time = current_time
                    
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
                cv2.imshow('Working Eye Mouse', frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('+'):
                    self.sensitivity = min(3.0, self.sensitivity + 0.1)
                    print(f"Sensitivity: {self.sensitivity:.1f}")
                elif key == ord('-'):
                    self.sensitivity = max(0.1, self.sensitivity - 0.1)
                    print(f"Sensitivity: {self.sensitivity:.1f}")
                elif key == ord('t'):
                    self.test_mouse_movement()
                elif key == ord('r'):
                    self.position_buffer.clear()
                    print("Smoothing reset")
                
                self.frame_count += 1
        
        except KeyboardInterrupt:
            print("\n⏹️  Stopped by user")
        finally:
            self.cleanup()
    
    def draw_ui_info(self, frame):
        """Draw comprehensive UI information"""
        elapsed = time.time() - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        success_rate = (self.mouse_move_success / self.mouse_move_count * 100) if self.mouse_move_count > 0 else 0
        
        info_lines = [
            f"FPS: {fps:.1f}",
            f"Sensitivity: {self.sensitivity:.1f}",
            f"Mouse Moves: {self.mouse_move_count}",
            f"Success Rate: {success_rate:.1f}%",
            f"Last Pos: {self.last_mouse_pos}",
            "Press 't' to test mouse"
        ]
        
        for i, line in enumerate(info_lines):
            cv2.putText(frame, line, (10, 30 + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    def cleanup(self):
        """Clean up resources and print final stats"""
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        
        print("\n📊 Final Statistics:")
        print(f"Total frames processed: {self.frame_count}")
        print(f"Mouse movement attempts: {self.mouse_move_count}")
        print(f"Successful movements: {self.mouse_move_success}")
        if self.mouse_move_count > 0:
            success_rate = (self.mouse_move_success / self.mouse_move_count * 100)
            print(f"Success rate: {success_rate:.1f}%")
        print("✅ Cleanup completed")

def main():
    """Main entry point"""
    try:
        eye_mouse = WorkingEyeMouse()
        eye_mouse.run()
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        logging.error(f"Startup error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
