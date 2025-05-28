"""
Improved Simple Eye-Controlled Mouse
Enhanced version of the original code with better performance and features
"""

import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np
from collections import deque
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class SimpleEyeMouse:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,  # Increased for better detection
            min_tracking_confidence=0.7
        )

        # Camera setup with better error handling
        self.cam = None
        self.initialize_camera()

        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        print(f"Screen resolution: {self.screen_w}x{self.screen_h}")

        # Smoothing and performance
        self.position_history = deque(maxlen=8)  # Increased for better smoothing
        self.blink_history = deque(maxlen=5)

        # Settings - OPTIMIZED FOR WORKING MOUSE CONTROL
        self.sensitivity = 3.0  # High sensitivity for responsive control
        self.smoothing = 0.8
        self.blink_threshold = 0.004
        self.click_cooldown = 1.0
        self.last_click_time = 0

        # Performance monitoring
        self.frame_count = 0
        self.start_time = time.time()

        # Configure PyAutoGUI for Wayland compatibility
        self.setup_pyautogui()

        # Coordinate mapping
        self.setup_coordinate_mapping()

        print("Simple Eye Mouse initialized")
        print("Controls:")
        print("- Look around to move cursor")
        print("- Blink to click")
        print("- Press 'q' to quit")
        print("- Press 's' to adjust sensitivity")
        print("- Press 'c' to calibrate blink threshold")

    def initialize_camera(self):
        """Initialize camera with error handling"""
        try:
            self.cam = cv2.VideoCapture(0)
            if not self.cam.isOpened():
                print("Error: Could not open camera")
                return False

            # Set camera properties
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cam.set(cv2.CAP_PROP_FPS, 30)
            self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce latency

            # Test camera
            ret, frame = self.cam.read()
            if not ret:
                print("Error: Could not read from camera")
                return False

            print(f"Camera initialized: {frame.shape}")
            return True
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            return False

    def setup_pyautogui(self):
        """Configure PyAutoGUI for optimal performance and Wayland compatibility"""
        # Disable failsafe for smooth operation
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.001  # Minimal pause for maximum responsiveness

        # Test mouse control
        try:
            current_pos = pyautogui.position()
            print(f"Current mouse position: {current_pos}")

            # Test small movement
            pyautogui.moveRel(1, 1)
            pyautogui.moveRel(-1, -1)
            print("Mouse control test: PASSED")
        except Exception as e:
            print(f"Mouse control test: FAILED - {e}")
            print("Note: On Wayland, you may need to run with X11 or use additional permissions")

    def setup_coordinate_mapping(self):
        """Setup coordinate mapping parameters"""
        # Calculate mapping zones for better control - OPTIMIZED
        self.center_x = 0.5
        self.center_y = 0.5
        self.dead_zone = 0.01  # Very small dead zone for responsiveness

        # Sensitivity zones (higher sensitivity at edges)
        self.edge_boost = 1.5  # Increased edge boost

        print(f"Coordinate mapping setup complete")
        print(f"Dead zone: {self.dead_zone:.3f}")

    def smooth_position(self, new_pos):
        """Apply smoothing to cursor position"""
        self.position_history.append(new_pos)

        if len(self.position_history) < 2:
            return new_pos

        # Weighted average for smoothing
        weights = np.linspace(0.1, 1.0, len(self.position_history))
        weights /= weights.sum()

        smooth_x = sum(w * pos[0] for w, pos in zip(weights, self.position_history))
        smooth_y = sum(w * pos[1] for w, pos in zip(weights, self.position_history))

        return (smooth_x, smooth_y)

    def get_eye_position(self, landmarks):
        """Get normalized eye position using multiple methods for robustness"""
        try:
            # Method 1: Use right iris center (primary)
            if len(landmarks) > 475:
                iris_center = landmarks[475]  # Right iris center
                primary_pos = (iris_center.x, iris_center.y)

                # Method 2: Average both iris centers for stability
                if len(landmarks) > 468:
                    left_iris = landmarks[468]   # Left iris center
                    right_iris = landmarks[475]  # Right iris center

                    avg_x = (left_iris.x + right_iris.x) / 2
                    avg_y = (left_iris.y + right_iris.y) / 2
                    avg_pos = (avg_x, avg_y)

                    # Blend both methods for stability
                    final_x = primary_pos[0] * 0.7 + avg_pos[0] * 0.3
                    final_y = primary_pos[1] * 0.7 + avg_pos[1] * 0.3

                    return (final_x, final_y)
                else:
                    return primary_pos

            # Fallback: Use eye corner landmarks
            elif len(landmarks) > 133:
                left_corner = landmarks[33]   # Left eye left corner
                right_corner = landmarks[133] # Left eye right corner

                eye_center_x = (left_corner.x + right_corner.x) / 2
                eye_center_y = (left_corner.y + right_corner.y) / 2

                return (eye_center_x, eye_center_y)

        except Exception as e:
            logging.error(f"Error getting eye position: {e}")

        return None

    def map_to_screen(self, eye_position):
        """Fixed mapping from eye position to screen coordinates"""
        eye_x, eye_y = eye_position

        # Apply dead zone around center
        center_offset_x = eye_x - self.center_x
        center_offset_y = eye_y - self.center_y

        # Apply dead zone
        if abs(center_offset_x) < self.dead_zone:
            center_offset_x = 0
        if abs(center_offset_y) < self.dead_zone:
            center_offset_y = 0

        # Apply edge boost for better control at screen edges - OPTIMIZED
        if abs(center_offset_x) > 0.3:  # Near edges
            center_offset_x *= self.edge_boost
        if abs(center_offset_y) > 0.3:
            center_offset_y *= self.edge_boost

        # FIXED: Direct mapping without multiplying by sensitivity twice
        screen_x = eye_x * self.screen_w
        screen_y = eye_y * self.screen_h

        return (screen_x, screen_y)

    def detect_blink(self, landmarks, frame_shape):
        """Improved blink detection"""
        try:
            frame_h, frame_w = frame_shape[:2]

            # Left eye landmarks (top and bottom)
            left_eye_top = landmarks[159]
            left_eye_bottom = landmarks[145]
            left_eye_ratio = abs(left_eye_top.y - left_eye_bottom.y)

            # Right eye landmarks (top and bottom)
            right_eye_top = landmarks[386]
            right_eye_bottom = landmarks[374]
            right_eye_ratio = abs(right_eye_top.y - right_eye_bottom.y)

            # Average both eyes for more reliable detection
            avg_ratio = (left_eye_ratio + right_eye_ratio) / 2
            self.blink_history.append(avg_ratio)

            if len(self.blink_history) < 3:
                return False

            # Check if current ratio is below threshold and previous wasn't
            current_avg = sum(self.blink_history) / len(self.blink_history)
            return current_avg < self.blink_threshold

        except Exception as e:
            logging.error(f"Blink detection error: {e}")
            return False

    def draw_eye_landmarks(self, frame, landmarks):
        """Draw eye tracking visualization"""
        frame_h, frame_w = frame.shape[:2]

        # Draw iris landmarks (right eye)
        iris_landmarks = [474, 475, 476, 477]
        for landmark_id in iris_landmarks:
            if landmark_id < len(landmarks):
                landmark = landmarks[landmark_id]
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        # Draw eye outline landmarks
        left_eye_landmarks = [145, 159]
        for landmark_id in left_eye_landmarks:
            if landmark_id < len(landmarks):
                landmark = landmarks[landmark_id]
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)

        return frame

    def draw_ui_info(self, frame):
        """Draw UI information on frame"""
        # Performance info
        current_time = time.time()
        elapsed = current_time - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0

        # Draw info text
        info_text = [
            f"FPS: {fps:.1f}",
            f"Sensitivity: {self.sensitivity:.1f}",
            f"Blink Threshold: {self.blink_threshold:.3f}",
            "Press 'q' to quit, 's' for sensitivity, 'c' for calibration"
        ]

        y_offset = 30
        for i, text in enumerate(info_text):
            cv2.putText(frame, text, (10, y_offset + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        return frame

    def adjust_sensitivity(self):
        """Interactive sensitivity adjustment"""
        print(f"\nCurrent sensitivity: {self.sensitivity:.1f}")
        print("Enter new sensitivity (0.1 - 2.0): ", end="")
        try:
            new_sensitivity = float(input())
            if 0.1 <= new_sensitivity <= 2.0:
                self.sensitivity = new_sensitivity
                print(f"Sensitivity set to: {self.sensitivity:.1f}")
            else:
                print("Invalid range. Keeping current sensitivity.")
        except ValueError:
            print("Invalid input. Keeping current sensitivity.")

    def calibrate_blink_threshold(self):
        """Interactive blink threshold calibration"""
        print("\nBlink Calibration:")
        print("Look at the camera and blink normally when prompted...")
        print("Press Enter to start calibration...")
        input()

        blink_samples = []
        normal_samples = []

        print("Phase 1: Normal eye state (don't blink) - 3 seconds...")
        start_time = time.time()

        while time.time() - start_time < 3.0:
            ret, frame = self.cam.read()
            if ret:
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(rgb_frame)

                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    left_ratio = abs(landmarks[159].y - landmarks[145].y)
                    right_ratio = abs(landmarks[386].y - landmarks[374].y)
                    avg_ratio = (left_ratio + right_ratio) / 2
                    normal_samples.append(avg_ratio)

        print("Phase 2: Blink several times - 3 seconds...")
        start_time = time.time()

        while time.time() - start_time < 3.0:
            ret, frame = self.cam.read()
            if ret:
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(rgb_frame)

                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    left_ratio = abs(landmarks[159].y - landmarks[145].y)
                    right_ratio = abs(landmarks[386].y - landmarks[374].y)
                    avg_ratio = (left_ratio + right_ratio) / 2
                    blink_samples.append(avg_ratio)

        if normal_samples and blink_samples:
            normal_avg = sum(normal_samples) / len(normal_samples)
            blink_min = min(blink_samples)

            # Set threshold between normal and blink states
            self.blink_threshold = (normal_avg + blink_min) / 2
            print(f"Calibration complete! New threshold: {self.blink_threshold:.3f}")
        else:
            print("Calibration failed. Keeping current threshold.")

    def run(self):
        """Main application loop"""
        try:
            while True:
                ret, frame = self.cam.read()
                if not ret:
                    print("Failed to read from camera")
                    break

                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Process with MediaPipe
                results = self.face_mesh.process(rgb_frame)

                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark

                    # Draw eye landmarks
                    frame = self.draw_eye_landmarks(frame, landmarks)

                    # Get iris position with improved mapping
                    eye_position = self.get_eye_position(landmarks)
                    if eye_position:
                        # Map to screen coordinates with fixed algorithm
                        screen_x, screen_y = self.map_to_screen(eye_position)

                        # Apply smoothing
                        smooth_x, smooth_y = self.smooth_position((screen_x, screen_y))

                        # Clamp to screen bounds
                        final_x = max(0, min(self.screen_w - 1, int(smooth_x)))
                        final_y = max(0, min(self.screen_h - 1, int(smooth_y)))

                        # Move cursor with xdotool for Wayland compatibility
                        try:
                            import subprocess
                            subprocess.run(['xdotool', 'mousemove', str(final_x), str(final_y)],
                                         capture_output=True, check=True, timeout=0.05)

                            # Debug output every 30 frames
                            if self.frame_count % 30 == 0:
                                print(f"👁️  Eye: ({eye_position[0]:.3f}, {eye_position[1]:.3f}) -> 🖱️  Screen: ({final_x}, {final_y})")
                        except Exception as e:
                            if self.frame_count % 60 == 0:  # Log error every 60 frames
                                logging.error(f"Mouse movement error: {e}")

                    # Detect blinks for clicking
                    current_time = time.time()
                    if (self.detect_blink(landmarks, frame.shape) and
                        current_time - self.last_click_time > self.click_cooldown):

                        # Use xdotool for clicking
                        try:
                            subprocess.run(['xdotool', 'click', '1'],
                                         capture_output=True, check=True, timeout=0.5)
                            self.last_click_time = current_time
                            print("👆 Click detected!")
                        except Exception as e:
                            logging.error(f"Click error: {e}")

                # Draw UI information
                frame = self.draw_ui_info(frame)

                # Display frame
                cv2.imshow('Simple Eye Mouse', frame)

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    cv2.destroyAllWindows()
                    self.adjust_sensitivity()
                    cv2.namedWindow('Simple Eye Mouse')
                elif key == ord('c'):
                    cv2.destroyAllWindows()
                    self.calibrate_blink_threshold()
                    cv2.namedWindow('Simple Eye Mouse')

                # Update performance counter
                self.frame_count += 1

        except KeyboardInterrupt:
            print("\nApplication stopped by user")
        except Exception as e:
            print(f"Error: {e}")
            logging.error(f"Application error: {e}", exc_info=True)
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        self.cam.release()
        cv2.destroyAllWindows()
        print("Cleanup completed")

def main():
    """Main entry point"""
    print("Starting Simple Eye Mouse...")

    try:
        eye_mouse = SimpleEyeMouse()
        eye_mouse.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        logging.error(f"Startup error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
