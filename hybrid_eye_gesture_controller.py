#!/usr/bin/env python3
"""
Hybrid Eye + Gesture Controlled Mouse with Reinforcement Learning
Combines eye tracking for cursor movement with hand gestures for actions
"""

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time
import json
import logging
from enum import IntEnum
from collections import deque
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Disable PyAutoGUI failsafe
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.001

class ControlMode(IntEnum):
    """Control modes for the hybrid system"""
    EYE_ONLY = 0
    GESTURE_ONLY = 1
    HYBRID = 2

class GestureType(IntEnum):
    """Gesture types for hand recognition"""
    FIST = 0
    INDEX = 1
    MIDDLE = 2
    PEACE = 3
    PALM = 4
    PINCH = 5
    THUMBS_UP = 6

class HybridController:
    """Hybrid controller combining eye tracking and hand gestures"""

    def __init__(self):
        print("🚀 Initializing Hybrid Eye + Gesture Controller...")

        # MediaPipe setup
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        # Initialize MediaPipe models
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()

        # Control settings
        self.control_mode = ControlMode.HYBRID
        self.eye_sensitivity = 1.2
        self.gesture_sensitivity = 1.0
        self.smoothing_factor = 0.6

        # Eye tracking state
        self.eye_position_history = deque(maxlen=5)
        self.blink_history = deque(maxlen=3)
        self.blink_threshold = 0.004
        self.last_blink_time = 0
        self.blink_cooldown = 0.8

        # Gesture tracking state
        self.current_gesture = GestureType.PALM
        self.gesture_history = deque(maxlen=5)
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.5
        self.drag_mode = False

        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()

        # Reinforcement learning data
        self.gesture_success_rates = {}
        self.gesture_attempts = {}
        self.learning_rate = 0.1

        # Load previous learning data
        self.load_learning_data()

        print(f"✅ Hybrid Controller Initialized")
        print(f"   Screen: {self.screen_w}x{self.screen_h}")
        print(f"   Mode: {ControlMode(self.control_mode).name}")
        print("\n🎮 Controls:")
        print("   👁️  Eyes - Move cursor")
        print("   👆 Index finger - Left click")
        print("   🖕 Middle finger - Right click")
        print("   ✌️  Peace sign - Double click")
        print("   👊 Fist - Drag mode")
        print("   🤏 Pinch - Scroll")
        print("   👍 Thumbs up - Toggle mode")
        print("   😉 Blink - Click (eye mode)")
        print("\n⌨️  Keyboard:")
        print("   'q' - Quit")
        print("   'm' - Toggle mode")
        print("   's' - Adjust sensitivity")
        print("   'r' - Reset drag mode")

    def detect_blink(self, landmarks):
        """Detect eye blinks for clicking"""
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

        return avg_ratio < self.blink_threshold

    def get_eye_position(self, landmarks):
        """Get eye position for cursor control - FIXED VERSION"""
        if len(landmarks) > 475:
            # Use right iris center (landmark 475) - same as working simple_eye_mouse.py
            iris_center = landmarks[475]

            # Convert to screen coordinates with sensitivity (same as working version)
            raw_x = iris_center.x * self.screen_w * self.eye_sensitivity
            raw_y = iris_center.y * self.screen_h * self.eye_sensitivity

            return raw_x, raw_y
        return None, None

    def smooth_eye_position(self, new_pos):
        """Apply smoothing to eye position"""
        if new_pos[0] is None or new_pos[1] is None:
            return None, None

        self.eye_position_history.append(new_pos)

        if len(self.eye_position_history) < 2:
            return new_pos

        # Weighted average smoothing
        weights = np.linspace(0.2, 1.0, len(self.eye_position_history))
        weights /= weights.sum()

        smooth_x = sum(w * pos[0] for w, pos in zip(weights, self.eye_position_history))
        smooth_y = sum(w * pos[1] for w, pos in zip(weights, self.eye_position_history))

        return smooth_x, smooth_y

    def recognize_hand_gesture(self, hand_landmarks):
        """Recognize hand gesture from landmarks"""
        if not hand_landmarks:
            return GestureType.PALM

        # Get finger tip and joint positions
        landmarks = hand_landmarks.landmark

        # Finger tip landmarks: thumb, index, middle, ring, pinky
        finger_tips = [4, 8, 12, 16, 20]
        finger_joints = [3, 6, 10, 14, 18]

        # Check which fingers are extended
        fingers_up = []

        # Thumb (different logic due to orientation)
        if landmarks[finger_tips[0]].x > landmarks[finger_joints[0]].x:
            fingers_up.append(1)
        else:
            fingers_up.append(0)

        # Other fingers
        for i in range(1, 5):
            if landmarks[finger_tips[i]].y < landmarks[finger_joints[i]].y:
                fingers_up.append(1)
            else:
                fingers_up.append(0)

        # Recognize gestures based on finger states
        total_fingers = sum(fingers_up)

        if total_fingers == 0:
            return GestureType.FIST
        elif total_fingers == 1 and fingers_up[1] == 1:  # Only index
            return GestureType.INDEX
        elif total_fingers == 1 and fingers_up[2] == 1:  # Only middle
            return GestureType.MIDDLE
        elif total_fingers == 2 and fingers_up[1] == 1 and fingers_up[2] == 1:  # Index + middle
            return GestureType.PEACE
        elif total_fingers == 1 and fingers_up[0] == 1:  # Only thumb
            return GestureType.THUMBS_UP
        elif total_fingers == 5:
            return GestureType.PALM
        else:
            # Check for pinch gesture
            thumb_index_dist = math.sqrt(
                (landmarks[4].x - landmarks[8].x)**2 +
                (landmarks[4].y - landmarks[8].y)**2
            )
            if thumb_index_dist < 0.05:
                return GestureType.PINCH

        return GestureType.PALM

    def execute_gesture_action(self, gesture):
        """Execute action based on recognized gesture"""
        current_time = time.time()

        # Check cooldown
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return

        success = False

        try:
            if gesture == GestureType.INDEX:
                # Left click
                pyautogui.click()
                print("🖱️ Left Click")
                success = True
                self.last_gesture_time = current_time

            elif gesture == GestureType.MIDDLE:
                # Right click
                pyautogui.rightClick()
                print("🖱️ Right Click")
                success = True
                self.last_gesture_time = current_time

            elif gesture == GestureType.PEACE:
                # Double click
                pyautogui.doubleClick()
                print("🖱️ Double Click")
                success = True
                self.last_gesture_time = current_time

            elif gesture == GestureType.FIST:
                # Toggle drag mode
                self.drag_mode = not self.drag_mode
                if self.drag_mode:
                    pyautogui.mouseDown()
                    print("🔒 Drag Mode ON")
                else:
                    pyautogui.mouseUp()
                    print("🔓 Drag Mode OFF")
                success = True
                self.last_gesture_time = current_time

            elif gesture == GestureType.THUMBS_UP:
                # Toggle control mode
                self.control_mode = (self.control_mode + 1) % 3
                mode_name = ControlMode(self.control_mode).name
                print(f"🔄 Mode: {mode_name}")
                success = True
                self.last_gesture_time = current_time

            elif gesture == GestureType.PINCH:
                # Scroll (placeholder - would need position tracking)
                print("📜 Scroll gesture detected")
                success = True

        except Exception as e:
            logging.error(f"Error executing gesture {gesture}: {e}")
            success = False

        # Record for reinforcement learning
        self.record_gesture_attempt(gesture, success)

    def record_gesture_attempt(self, gesture, success):
        """Record gesture attempt for reinforcement learning"""
        if gesture not in self.gesture_attempts:
            self.gesture_attempts[gesture] = 0
            self.gesture_success_rates[gesture] = 0.5

        self.gesture_attempts[gesture] += 1

        # Update success rate
        current_rate = self.gesture_success_rates[gesture]
        new_rate = current_rate + self.learning_rate * (1.0 if success else 0.0 - current_rate)
        self.gesture_success_rates[gesture] = max(0.1, min(0.9, new_rate))

    def load_learning_data(self):
        """Load reinforcement learning data"""
        try:
            with open('hybrid_learning.json', 'r') as f:
                data = json.load(f)
                self.gesture_success_rates = data.get('success_rates', {})
                self.gesture_attempts = data.get('attempts', {})
        except FileNotFoundError:
            logging.info("No previous learning data found")

    def save_learning_data(self):
        """Save reinforcement learning data"""
        data = {
            'success_rates': self.gesture_success_rates,
            'attempts': self.gesture_attempts
        }
        with open('hybrid_learning.json', 'w') as f:
            json.dump(data, f)

    def draw_ui_info(self, image):
        """Draw UI information on the image"""
        h, w, _ = image.shape

        # Performance info
        current_time = time.time()
        elapsed = current_time - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0

        # Status information
        status_lines = [
            f"FPS: {fps:.1f}",
            f"Mode: {ControlMode(self.control_mode).name}",
            f"Gesture: {GestureType(self.current_gesture).name}",
            f"Drag: {'ON' if self.drag_mode else 'OFF'}",
            f"Eye Sens: {self.eye_sensitivity:.1f}",
            f"Frames: {self.frame_count}"
        ]

        # Draw status
        for i, line in enumerate(status_lines):
            cv2.putText(image, line, (10, 30 + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Draw crosshair at center for eye tracking reference
        center_x, center_y = w // 2, h // 2
        cv2.line(image, (center_x - 20, center_y), (center_x + 20, center_y), (0, 255, 255), 2)
        cv2.line(image, (center_x, center_y - 20), (center_x, center_y + 20), (0, 255, 255), 2)

        return image

    def run(self):
        """Main control loop"""
        print("\n🚀 Starting Hybrid Eye + Gesture Controller...")
        print("   Look around to move cursor (eye mode)")
        print("   Use hand gestures for actions")

        try:
            while True:
                success, image = self.cap.read()
                if not success:
                    continue

                # Flip image horizontally for mirror effect
                image = cv2.flip(image, 1)

                # Convert BGR to RGB for MediaPipe
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                rgb_image.flags.writeable = False

                # Process face and hands
                face_results = self.face_mesh.process(rgb_image)
                hand_results = self.hands.process(rgb_image)

                # Convert back to BGR
                rgb_image.flags.writeable = True
                image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)

                # Process eye tracking - EXACT SAME AS SIMPLE_EYE_MOUSE.PY
                if (face_results.multi_face_landmarks and
                    self.control_mode in [ControlMode.EYE_ONLY, ControlMode.HYBRID]):

                    landmarks = face_results.multi_face_landmarks[0].landmark

                    # EXACT SAME METHOD AS simple_eye_mouse.py
                    if len(landmarks) > 475:
                        iris_center = landmarks[475]  # Right iris center

                        # Convert to screen coordinates
                        raw_x = iris_center.x * self.screen_w * self.eye_sensitivity
                        raw_y = iris_center.y * self.screen_h * self.eye_sensitivity

                        # Clamp to screen bounds
                        screen_x = max(0, min(self.screen_w - 1, int(raw_x)))
                        screen_y = max(0, min(self.screen_h - 1, int(raw_y)))

                        # Move cursor directly (EXACT SAME AS simple_eye_mouse.py)
                        pyautogui.moveTo(screen_x, screen_y)

                    # Detect blinks for clicking (eye-only mode)
                    if self.control_mode == ControlMode.EYE_ONLY:
                        current_time = time.time()
                        if (self.detect_blink(landmarks) and
                            current_time - self.last_blink_time > self.blink_cooldown):

                            pyautogui.click()
                            self.last_blink_time = current_time
                            print("😉 Blink Click!")

                # Process hand gestures
                if (hand_results.multi_hand_landmarks and
                    self.control_mode in [ControlMode.GESTURE_ONLY, ControlMode.HYBRID]):

                    for hand_landmarks in hand_results.multi_hand_landmarks:
                        # Recognize gesture
                        gesture = self.recognize_hand_gesture(hand_landmarks)
                        self.gesture_history.append(gesture)

                        # Stabilize gesture recognition
                        if len(self.gesture_history) >= 3:
                            # Use most common gesture in recent history
                            gesture_counts = {}
                            for g in list(self.gesture_history)[-3:]:
                                gesture_counts[g] = gesture_counts.get(g, 0) + 1

                            stable_gesture = max(gesture_counts, key=gesture_counts.get)

                            if stable_gesture != self.current_gesture:
                                self.current_gesture = stable_gesture

                                # Execute gesture action
                                if self.current_gesture != GestureType.PALM:
                                    self.execute_gesture_action(self.current_gesture)

                        # Draw hand landmarks
                        self.mp_drawing.draw_landmarks(
                            image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                # Draw UI information
                image = self.draw_ui_info(image)

                # Display image
                cv2.imshow('Hybrid Eye + Gesture Controller', image)

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC
                    break
                elif key == ord('m'):
                    # Toggle control mode
                    self.control_mode = (self.control_mode + 1) % 3
                    mode_name = ControlMode(self.control_mode).name
                    print(f"🔄 Mode: {mode_name}")
                elif key == ord('s'):
                    # Adjust eye sensitivity
                    self.eye_sensitivity = (self.eye_sensitivity + 0.2) % 3.0 + 0.5
                    print(f"👁️ Eye Sensitivity: {self.eye_sensitivity:.1f}")
                elif key == ord('r'):
                    # Reset drag mode
                    if self.drag_mode:
                        pyautogui.mouseUp()
                        self.drag_mode = False
                        print("🔓 Drag Mode Reset")
                elif key == ord(' '):
                    # Center cursor
                    pyautogui.moveTo(self.screen_w // 2, self.screen_h // 2)
                    print("🎯 Cursor Centered")

                self.frame_count += 1

        except KeyboardInterrupt:
            print("\n⏹️ Stopping...")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")

        # Release mouse if in drag mode
        if self.drag_mode:
            pyautogui.mouseUp()

        # Save learning data
        self.save_learning_data()

        # Release camera and close windows
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

        # Final statistics
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0

        print(f"📊 Session Statistics:")
        print(f"   Runtime: {elapsed:.1f}s")
        print(f"   Frames: {self.frame_count}")
        print(f"   Average FPS: {avg_fps:.1f}")
        print(f"   Gesture attempts: {sum(self.gesture_attempts.values())}")
        print("✅ Cleanup completed")

def main():
    """Main entry point"""
    try:
        controller = HybridController()
        controller.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Application error: {e}")

if __name__ == "__main__":
    main()
