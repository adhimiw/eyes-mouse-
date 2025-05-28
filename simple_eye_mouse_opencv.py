#!/usr/bin/env python3
"""
Simple Eye-Controlled Mouse (OpenCV Version)
A basic implementation using OpenCV for face/eye detection instead of MediaPipe
"""

import cv2
import pyautogui
import numpy as np
import time
import sys
from config_manager import ConfigManager
from eye_tracker_opencv import EyeTrackerOpenCV

# Disable PyAutoGUI failsafe for demo
pyautogui.FAILSAFE = False

class SimpleEyeMouseOpenCV:
    def __init__(self):
        self.config = ConfigManager()
        self.eye_tracker = EyeTrackerOpenCV(self.config)
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Click detection
        self.last_blink_time = 0
        self.blink_cooldown = 1.0  # 1 second cooldown between clicks
        
        print(f"Screen resolution: {self.screen_width}x{self.screen_height}")
        print("Controls:")
        print("- Move your eyes to control the cursor")
        print("- Blink to click")
        print("- Press ESC to exit")
        print("- Press 'c' to toggle cursor control")
        print("- Press 's' to show/hide statistics")
        
    def run(self):
        """Main application loop"""
        if not self.eye_tracker.initialize_camera():
            print("Error: Could not initialize camera")
            return
        
        cursor_enabled = True
        show_stats = True
        
        try:
            while True:
                frame, tracking_data = self.eye_tracker.process_frame()
                
                if frame is None:
                    continue
                
                # Process eye tracking data
                if tracking_data.get("eye_position") and cursor_enabled:
                    eye_x, eye_y = tracking_data["eye_position"]
                    
                    # Map to screen coordinates
                    screen_x, screen_y = self.eye_tracker.map_eye_to_screen(
                        (eye_x, eye_y), (self.screen_width, self.screen_height)
                    )
                    
                    # Move cursor
                    try:
                        pyautogui.moveTo(screen_x, screen_y)
                    except:
                        pass  # Ignore any PyAutoGUI errors
                    
                    # Handle blink detection for clicking
                    if tracking_data.get("blink_detected"):
                        current_time = time.time()
                        if current_time - self.last_blink_time > self.blink_cooldown:
                            try:
                                pyautogui.click()
                                self.last_blink_time = current_time
                                print("Click detected!")
                            except:
                                pass
                
                # Draw UI elements
                self._draw_ui(frame, tracking_data, cursor_enabled, show_stats)
                
                # Display frame
                cv2.imshow('Eye-Controlled Mouse (OpenCV)', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC key
                    break
                elif key == ord('c'):
                    cursor_enabled = not cursor_enabled
                    print(f"Cursor control: {'ON' if cursor_enabled else 'OFF'}")
                elif key == ord('s'):
                    show_stats = not show_stats
                    print(f"Statistics: {'ON' if show_stats else 'OFF'}")
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()
    
    def _draw_ui(self, frame, tracking_data, cursor_enabled, show_stats):
        """Draw UI elements on the frame"""
        height, width = frame.shape[:2]
        
        # Status indicators
        status_color = (0, 255, 0) if cursor_enabled else (0, 0, 255)
        cv2.putText(frame, f"Cursor: {'ON' if cursor_enabled else 'OFF'}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Tracking quality
        quality = tracking_data.get("tracking_quality", 0.0)
        quality_color = (0, 255, 0) if quality > 0.7 else (0, 255, 255) if quality > 0.3 else (0, 0, 255)
        cv2.putText(frame, f"Quality: {quality:.2f}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, quality_color, 2)
        
        # Eye position indicator
        if tracking_data.get("eye_position"):
            eye_x, eye_y = tracking_data["eye_position"]
            indicator_x = int(eye_x * width)
            indicator_y = int(eye_y * height)
            cv2.circle(frame, (indicator_x, indicator_y), 10, (255, 255, 0), 2)
            cv2.circle(frame, (indicator_x, indicator_y), 3, (255, 255, 0), -1)
        
        # Blink indicator
        if tracking_data.get("blink_detected"):
            cv2.putText(frame, "BLINK!", (width - 150, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Statistics
        if show_stats:
            stats = self.eye_tracker.get_performance_stats()
            y_offset = height - 100
            
            if "fps" in stats:
                cv2.putText(frame, f"FPS: {stats['fps']:.1f}", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                y_offset += 25
            
            if "avg_processing_time" in stats:
                cv2.putText(frame, f"Process: {stats['avg_processing_time']*1000:.1f}ms", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Instructions
        cv2.putText(frame, "ESC: Exit | C: Toggle cursor | S: Toggle stats", 
                   (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def cleanup(self):
        """Clean up resources"""
        self.eye_tracker.cleanup()
        cv2.destroyAllWindows()

def main():
    """Main entry point"""
    print("Starting Simple Eye-Controlled Mouse (OpenCV Version)...")
    
    # Check if camera is available
    test_camera = cv2.VideoCapture(0)
    if not test_camera.isOpened():
        print("Error: No camera detected. Please connect a camera and try again.")
        return
    test_camera.release()
    
    # Run the application
    app = SimpleEyeMouseOpenCV()
    app.run()

if __name__ == "__main__":
    main()
