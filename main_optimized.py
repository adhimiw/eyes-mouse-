#!/usr/bin/env python3
"""
Performance-Optimized Eye-Controlled Interface
Based on simple_eye_mouse.py but with enhanced features
"""

import cv2
import numpy as np
import pyautogui
import mediapipe as mp
import time
import logging
from collections import deque
from config_manager import ConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OptimizedEyeInterface:
    def __init__(self):
        """Initialize optimized eye interface"""
        print("Initializing Optimized Eye-Controlled Interface...")
        
        # Configuration
        self.config = ConfigManager()
        
        # MediaPipe setup
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Camera setup - optimized settings
        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cam.set(cv2.CAP_PROP_FPS, 30)
        self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for lower latency
        
        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Performance optimizations
        self.position_history = deque(maxlen=3)  # Reduced for lower latency
        self.blink_history = deque(maxlen=3)
        
        # Settings from config with fallbacks
        self.sensitivity = self.config.get_setting("tracking", "sensitivity", 1.2)
        self.smoothing = self.config.get_setting("tracking", "smoothing", 0.5)  # Reduced for responsiveness
        self.blink_threshold = self.config.get_setting("tracking", "blink_threshold", 0.004)
        self.click_cooldown = self.config.get_setting("tracking", "click_cooldown", 0.8)
        
        # State tracking
        self.last_click_time = 0
        self.frame_count = 0
        self.start_time = time.time()
        self.cursor_enabled = True
        self.show_ui = True
        
        # PyAutoGUI optimizations
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.001  # Minimal pause for maximum responsiveness
        
        # Center cursor initially
        pyautogui.moveTo(self.screen_w // 2, self.screen_h // 2)
        
        print(f"✅ Optimized interface initialized")
        print(f"   Screen: {self.screen_w}x{self.screen_h}")
        print(f"   Sensitivity: {self.sensitivity}")
        print(f"   Camera: {self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)}x{self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        print("\n🎮 Controls:")
        print("   - Look around to move cursor")
        print("   - Blink to click")
        print("   - Press 'q' to quit")
        print("   - Press 'c' to toggle cursor control")
        print("   - Press 's' to adjust sensitivity")
        print("   - Press 'h' to toggle UI display")
        print("   - Press SPACE to center cursor")
    
    def smooth_position(self, new_pos):
        """Apply lightweight smoothing to cursor position"""
        self.position_history.append(new_pos)
        
        if len(self.position_history) < 2:
            return new_pos
        
        # Simple weighted average - optimized for performance
        if len(self.position_history) == 2:
            prev_pos = self.position_history[-2]
            return (
                prev_pos[0] * self.smoothing + new_pos[0] * (1 - self.smoothing),
                prev_pos[1] * self.smoothing + new_pos[1] * (1 - self.smoothing)
            )
        else:
            # Use last 3 positions with decreasing weights
            weights = [0.2, 0.3, 0.5]  # Most recent gets highest weight
            smooth_x = sum(w * pos[0] for w, pos in zip(weights, self.position_history))
            smooth_y = sum(w * pos[1] for w, pos in zip(weights, self.position_history))
            return (smooth_x, smooth_y)
    
    def detect_blink(self, landmarks):
        """Optimized blink detection"""
        # Left eye landmarks
        left_top = landmarks[159].y
        left_bottom = landmarks[145].y
        left_ratio = abs(left_top - left_bottom)
        
        # Right eye landmarks  
        right_top = landmarks[386].y
        right_bottom = landmarks[374].y
        right_ratio = abs(right_top - right_bottom)
        
        # Average ratio
        avg_ratio = (left_ratio + right_ratio) / 2
        self.blink_history.append(avg_ratio)
        
        # Detect blink with threshold
        return avg_ratio < self.blink_threshold
    
    def draw_ui_info(self, frame):
        """Draw minimal UI information"""
        if not self.show_ui:
            return frame
        
        h, w = frame.shape[:2]
        
        # Performance info
        current_time = time.time()
        elapsed = current_time - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        # Status text
        status_text = [
            f"FPS: {fps:.1f}",
            f"Cursor: {'ON' if self.cursor_enabled else 'OFF'}",
            f"Sensitivity: {self.sensitivity:.1f}",
            f"Frames: {self.frame_count}"
        ]
        
        # Draw status
        for i, text in enumerate(status_text):
            cv2.putText(frame, text, (10, 30 + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Draw crosshair at center
        center_x, center_y = w // 2, h // 2
        cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), (0, 255, 255), 2)
        cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), (0, 255, 255), 2)
        
        return frame
    
    def adjust_sensitivity(self):
        """Interactive sensitivity adjustment"""
        print(f"\nCurrent sensitivity: {self.sensitivity:.1f}")
        try:
            new_sensitivity = float(input("Enter new sensitivity (0.1-3.0): "))
            if 0.1 <= new_sensitivity <= 3.0:
                self.sensitivity = new_sensitivity
                print(f"✅ Sensitivity set to {self.sensitivity:.1f}")
            else:
                print("❌ Invalid range. Using current value.")
        except ValueError:
            print("❌ Invalid input. Using current value.")
    
    def run(self):
        """Main optimized tracking loop"""
        if not self.cam.isOpened():
            print("❌ Error: Could not open camera")
            return
        
        print("\n🚀 Starting optimized eye tracking...")
        print("   Look at the center crosshair to center cursor")
        
        try:
            while True:
                loop_start = time.time()
                
                # Capture frame
                ret, frame = self.cam.read()
                if not ret:
                    continue
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Convert to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process with MediaPipe
                results = self.face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks and self.cursor_enabled:
                    landmarks = results.multi_face_landmarks[0].landmark
                    
                    # Get iris position (right iris center for better tracking)
                    if len(landmarks) > 475:
                        iris_center = landmarks[475]  # Right iris center
                        
                        # Convert to screen coordinates with sensitivity
                        raw_x = iris_center.x * self.screen_w * self.sensitivity
                        raw_y = iris_center.y * self.screen_h * self.sensitivity
                        
                        # Apply smoothing
                        smooth_x, smooth_y = self.smooth_position((raw_x, raw_y))
                        
                        # Clamp to screen bounds
                        screen_x = max(0, min(self.screen_w - 1, int(smooth_x)))
                        screen_y = max(0, min(self.screen_h - 1, int(smooth_y)))
                        
                        # Move cursor directly - no extra processing
                        pyautogui.moveTo(screen_x, screen_y)
                    
                    # Detect blinks for clicking
                    current_time = time.time()
                    if (self.detect_blink(landmarks) and 
                        current_time - self.last_click_time > self.click_cooldown):
                        
                        pyautogui.click()
                        self.last_click_time = current_time
                        print("🖱️  Click!")
                
                # Draw UI
                frame = self.draw_ui_info(frame)
                
                # Display frame
                cv2.imshow('Optimized Eye Interface', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC
                    break
                elif key == ord('c'):
                    self.cursor_enabled = not self.cursor_enabled
                    print(f"🖱️  Cursor control: {'ON' if self.cursor_enabled else 'OFF'}")
                elif key == ord('s'):
                    cv2.destroyAllWindows()
                    self.adjust_sensitivity()
                    cv2.namedWindow('Optimized Eye Interface')
                elif key == ord('h'):
                    self.show_ui = not self.show_ui
                    print(f"📊 UI display: {'ON' if self.show_ui else 'OFF'}")
                elif key == ord(' '):  # Space bar
                    pyautogui.moveTo(self.screen_w // 2, self.screen_h // 2)
                    print("🎯 Cursor centered")
                
                # Update performance counter
                self.frame_count += 1
                
                # Optional: Maintain target FPS (comment out for maximum performance)
                # loop_time = time.time() - loop_start
                # target_time = 1.0 / 30  # 30 FPS
                # if loop_time < target_time:
                #     time.sleep(target_time - loop_time)
        
        except KeyboardInterrupt:
            print("\n⏹️  Stopping...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")
        if self.cam:
            self.cam.release()
        cv2.destroyAllWindows()
        
        # Final stats
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0
        print(f"📊 Final stats:")
        print(f"   Frames processed: {self.frame_count}")
        print(f"   Runtime: {elapsed:.1f}s")
        print(f"   Average FPS: {avg_fps:.1f}")
        print("✅ Cleanup completed")

def main():
    """Main function"""
    try:
        app = OptimizedEyeInterface()
        app.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Application error: {e}")

if __name__ == "__main__":
    main()
