#!/usr/bin/env python3
"""
Advanced Gesture-Controlled Virtual Mouse with Reinforcement Learning
Based on MediaPipe Hand Detection with Eye Tracking Integration
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

# Disable PyAutoGUI failsafe for smooth operation
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.001

class GestureType(IntEnum):
    """Gesture encodings for hand gestures"""
    FIST = 0
    PINKY = 1
    RING = 2
    MID = 4
    LAST3 = 7
    INDEX = 8
    FIRST2 = 12
    LAST4 = 15
    THUMB = 16
    PALM = 31

    # Special gestures
    V_GESTURE = 33
    TWO_FINGER_CLOSED = 34
    PINCH_MAJOR = 35
    PINCH_MINOR = 36
    PEACE = 37
    OK_SIGN = 38

class HandLabel(IntEnum):
    """Hand labels for multi-hand detection"""
    LEFT = 0
    RIGHT = 1

class ReinforcementLearner:
    """Simple reinforcement learning for gesture adaptation"""

    def __init__(self):
        self.gesture_success_rates = {}
        self.gesture_attempts = {}
        self.learning_rate = 0.1
        self.confidence_threshold = 0.7

    def record_gesture_attempt(self, gesture: int, success: bool):
        """Record gesture attempt and success/failure"""
        if gesture not in self.gesture_attempts:
            self.gesture_attempts[gesture] = 0
            self.gesture_success_rates[gesture] = 0.5

        self.gesture_attempts[gesture] += 1

        # Update success rate using exponential moving average
        current_rate = self.gesture_success_rates[gesture]
        new_rate = current_rate + self.learning_rate * (1.0 if success else 0.0 - current_rate)
        self.gesture_success_rates[gesture] = max(0.1, min(0.9, new_rate))

    def get_gesture_confidence(self, gesture: int) -> float:
        """Get confidence level for a gesture"""
        return self.gesture_success_rates.get(gesture, 0.5)

    def should_execute_gesture(self, gesture: int) -> bool:
        """Determine if gesture should be executed based on confidence"""
        return self.get_gesture_confidence(gesture) >= self.confidence_threshold

    def save_learning_data(self, filepath: str):
        """Save learning data to file"""
        data = {
            'success_rates': self.gesture_success_rates,
            'attempts': self.gesture_attempts
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)

    def load_learning_data(self, filepath: str):
        """Load learning data from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.gesture_success_rates = data.get('success_rates', {})
                self.gesture_attempts = data.get('attempts', {})
        except FileNotFoundError:
            logging.info("No previous learning data found, starting fresh")

class HandGestureRecognizer:
    """Advanced hand gesture recognition with MediaPipe"""

    def __init__(self, hand_label: int):
        self.hand_label = hand_label
        self.finger_state = 0
        self.current_gesture = GestureType.PALM
        self.previous_gesture = GestureType.PALM
        self.frame_count = 0
        self.hand_landmarks = None
        self.gesture_history = deque(maxlen=5)

    def update_landmarks(self, landmarks):
        """Update hand landmarks"""
        self.hand_landmarks = landmarks

    def get_distance(self, point1: int, point2: int) -> float:
        """Calculate Euclidean distance between two landmarks"""
        if not self.hand_landmarks:
            return 0.0

        p1 = self.hand_landmarks.landmark[point1]
        p2 = self.hand_landmarks.landmark[point2]

        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    def get_signed_distance(self, point1: int, point2: int) -> float:
        """Calculate signed distance (considering y-axis direction)"""
        if not self.hand_landmarks:
            return 0.0

        p1 = self.hand_landmarks.landmark[point1]
        p2 = self.hand_landmarks.landmark[point2]

        sign = 1 if p1.y < p2.y else -1
        dist = math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
        return dist * sign

    def detect_finger_states(self):
        """Detect which fingers are extended"""
        if not self.hand_landmarks:
            return

        # Finger tip and joint landmarks
        finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        finger_joints = [3, 6, 10, 14, 18]

        self.finger_state = 0

        # Check each finger
        for i, (tip, joint) in enumerate(zip(finger_tips, finger_joints)):
            if i == 0:  # Thumb (different logic)
                if self.hand_landmarks.landmark[tip].x > self.hand_landmarks.landmark[joint].x:
                    self.finger_state |= (1 << i)
            else:  # Other fingers
                if self.hand_landmarks.landmark[tip].y < self.hand_landmarks.landmark[joint].y:
                    self.finger_state |= (1 << i)

    def recognize_gesture(self) -> int:
        """Recognize current gesture based on finger states and positions"""
        if not self.hand_landmarks:
            return GestureType.PALM

        self.detect_finger_states()

        # Gesture recognition logic
        current_gesture = GestureType.PALM

        # Check for specific gestures
        if self.finger_state == 0:  # All fingers closed
            current_gesture = GestureType.FIST
        elif self.finger_state == 6:  # Index and middle finger up
            # Check if it's V gesture or peace sign
            index_middle_dist = self.get_distance(8, 12)
            if index_middle_dist > 0.05:
                current_gesture = GestureType.V_GESTURE
            else:
                current_gesture = GestureType.TWO_FINGER_CLOSED
        elif self.finger_state == 2:  # Only index finger up
            current_gesture = GestureType.INDEX
        elif self.finger_state == 4:  # Only middle finger up
            current_gesture = GestureType.MID
        elif self.finger_state == 31:  # All fingers up
            current_gesture = GestureType.PALM
        else:
            # Check for pinch gestures
            thumb_index_dist = self.get_distance(4, 8)
            if thumb_index_dist < 0.05:
                if self.hand_label == HandLabel.RIGHT:
                    current_gesture = GestureType.PINCH_MAJOR
                else:
                    current_gesture = GestureType.PINCH_MINOR

        # Gesture stabilization
        self.gesture_history.append(current_gesture)

        if current_gesture == self.previous_gesture:
            self.frame_count += 1
        else:
            self.frame_count = 0

        self.previous_gesture = current_gesture

        # Only update gesture if it's stable for multiple frames
        if self.frame_count > 3:
            self.current_gesture = current_gesture

        return self.current_gesture

class GestureController:
    """Main controller for gesture-based mouse control"""

    def __init__(self):
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
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
        self.screen_width, self.screen_height = pyautogui.size()

        # Hand recognizers
        self.right_hand = HandGestureRecognizer(HandLabel.RIGHT)
        self.left_hand = HandGestureRecognizer(HandLabel.LEFT)

        # Control state
        self.cursor_enabled = True
        self.click_enabled = True
        self.drag_mode = False
        self.pinch_start_pos = None
        self.last_cursor_pos = None
        self.cursor_smoothing = 0.7
        self.sensitivity = 1.5

        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()

        # Reinforcement learning
        self.rl_agent = ReinforcementLearner()
        self.rl_agent.load_learning_data('gesture_learning.json')

        # Gesture timing
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.5

        print("🚀 Advanced Gesture Controller Initialized")
        print(f"   Screen: {self.screen_width}x{self.screen_height}")
        print(f"   Camera: {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        print("\n🎮 Gesture Controls:")
        print("   ✋ PALM - Move cursor")
        print("   👆 INDEX - Left click")
        print("   🖕 MIDDLE - Right click")
        print("   ✌️  V_GESTURE - Drag mode")
        print("   👊 FIST - Hold/drag")
        print("   🤏 PINCH - Scroll")
        print("   Press 'q' to quit, 'c' to toggle cursor, 's' for sensitivity")

    def get_hand_position(self, landmarks) -> Tuple[float, float]:
        """Get normalized hand position for cursor control"""
        if not landmarks:
            return None, None

        # Use index finger tip for cursor position
        index_tip = landmarks.landmark[8]
        return index_tip.x, index_tip.y

    def smooth_cursor_movement(self, new_x: float, new_y: float) -> Tuple[int, int]:
        """Apply smoothing to cursor movement"""
        if self.last_cursor_pos is None:
            self.last_cursor_pos = (new_x, new_y)

        # Apply smoothing
        smooth_x = self.last_cursor_pos[0] * self.cursor_smoothing + new_x * (1 - self.cursor_smoothing)
        smooth_y = self.last_cursor_pos[1] * self.cursor_smoothing + new_y * (1 - self.cursor_smoothing)

        self.last_cursor_pos = (smooth_x, smooth_y)

        # Convert to screen coordinates
        screen_x = int(smooth_x * self.screen_width * self.sensitivity)
        screen_y = int(smooth_y * self.screen_height * self.sensitivity)

        # Clamp to screen bounds
        screen_x = max(0, min(self.screen_width - 1, screen_x))
        screen_y = max(0, min(self.screen_height - 1, screen_y))

        return screen_x, screen_y

    def execute_gesture_action(self, gesture: int, hand_landmarks):
        """Execute action based on recognized gesture"""
        current_time = time.time()

        # Check cooldown
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return

        # Check if RL agent recommends executing this gesture
        if not self.rl_agent.should_execute_gesture(gesture):
            logging.debug(f"RL agent suggests skipping gesture {gesture}")
            return

        success = False

        try:
            if gesture == GestureType.PALM and self.cursor_enabled:
                # Move cursor
                hand_x, hand_y = self.get_hand_position(hand_landmarks)
                if hand_x is not None and hand_y is not None:
                    screen_x, screen_y = self.smooth_cursor_movement(hand_x, hand_y)
                    pyautogui.moveTo(screen_x, screen_y)
                    success = True

            elif gesture == GestureType.INDEX and self.click_enabled:
                # Left click
                pyautogui.click()
                print("🖱️ Left Click")
                success = True
                self.last_gesture_time = current_time

            elif gesture == GestureType.MID and self.click_enabled:
                # Right click
                pyautogui.rightClick()
                print("🖱️ Right Click")
                success = True
                self.last_gesture_time = current_time

            elif gesture == GestureType.V_GESTURE:
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

            elif gesture == GestureType.FIST:
                # Hold/drag
                if not self.drag_mode:
                    pyautogui.mouseDown()
                    self.drag_mode = True
                    print("👊 Drag Started")
                success = True

            elif gesture == GestureType.PINCH_MAJOR or gesture == GestureType.PINCH_MINOR:
                # Scroll functionality
                hand_x, hand_y = self.get_hand_position(hand_landmarks)
                if hand_x is not None and hand_y is not None:
                    if self.pinch_start_pos is None:
                        self.pinch_start_pos = (hand_x, hand_y)
                    else:
                        # Calculate scroll direction and amount
                        dx = hand_x - self.pinch_start_pos[0]
                        dy = hand_y - self.pinch_start_pos[1]

                        if abs(dy) > 0.02:  # Vertical scroll
                            scroll_amount = int(dy * 10)
                            pyautogui.scroll(scroll_amount)
                            print(f"📜 Scroll: {scroll_amount}")
                            self.pinch_start_pos = (hand_x, hand_y)
                            success = True

            elif gesture == GestureType.TWO_FINGER_CLOSED:
                # Double click
                pyautogui.doubleClick()
                print("🖱️ Double Click")
                success = True
                self.last_gesture_time = current_time

        except Exception as e:
            logging.error(f"Error executing gesture {gesture}: {e}")
            success = False

        # Record gesture attempt for reinforcement learning
        self.rl_agent.record_gesture_attempt(gesture, success)

    def process_hands(self, results):
        """Process detected hands and classify them"""
        if not results.multi_hand_landmarks:
            return

        # Reset hand landmarks
        self.right_hand.update_landmarks(None)
        self.left_hand.update_landmarks(None)

        # Process each detected hand
        for idx, (hand_landmarks, handedness) in enumerate(zip(results.multi_hand_landmarks, results.multi_handedness)):
            # Determine if it's left or right hand
            hand_label = handedness.classification[0].label

            if hand_label == "Right":
                self.right_hand.update_landmarks(hand_landmarks)
            else:
                self.left_hand.update_landmarks(hand_landmarks)

    def draw_landmarks(self, image, results):
        """Draw hand landmarks on the image"""
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

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
            f"Cursor: {'ON' if self.cursor_enabled else 'OFF'}",
            f"Click: {'ON' if self.click_enabled else 'OFF'}",
            f"Drag: {'ON' if self.drag_mode else 'OFF'}",
            f"Sensitivity: {self.sensitivity:.1f}",
            f"Frames: {self.frame_count}"
        ]

        # Draw status
        for i, line in enumerate(status_lines):
            cv2.putText(image, line, (10, 30 + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Draw gesture info
        right_gesture = self.right_hand.current_gesture
        left_gesture = self.left_hand.current_gesture

        gesture_info = [
            f"Right: {GestureType(right_gesture).name}",
            f"Left: {GestureType(left_gesture).name}",
            f"RL Confidence: {self.rl_agent.get_gesture_confidence(right_gesture):.2f}"
        ]

        for i, line in enumerate(gesture_info):
            cv2.putText(image, line, (w - 300, 30 + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        return image

    def run(self):
        """Main control loop"""
        print("\n🚀 Starting Gesture-Controlled Mouse...")
        print("   Show your palm to move cursor")
        print("   Point with index finger to click")
        print("   Make a fist to drag")

        try:
            while True:
                success, image = self.cap.read()
                if not success:
                    continue

                # Flip image horizontally for mirror effect
                image = cv2.flip(image, 1)

                # Convert BGR to RGB
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                rgb_image.flags.writeable = False

                # Process hands
                results = self.hands.process(rgb_image)

                # Convert back to BGR
                rgb_image.flags.writeable = True
                image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)

                # Process detected hands
                self.process_hands(results)

                # Recognize gestures and execute actions
                right_gesture = self.right_hand.recognize_gesture()
                left_gesture = self.left_hand.recognize_gesture()

                # Execute primary hand gesture (right hand priority)
                if self.right_hand.hand_landmarks:
                    self.execute_gesture_action(right_gesture, self.right_hand.hand_landmarks)
                elif self.left_hand.hand_landmarks:
                    self.execute_gesture_action(left_gesture, self.left_hand.hand_landmarks)

                # Reset pinch position if no pinch gesture
                if right_gesture not in [GestureType.PINCH_MAJOR, GestureType.PINCH_MINOR]:
                    self.pinch_start_pos = None

                # Draw landmarks and UI
                self.draw_landmarks(image, results)
                image = self.draw_ui_info(image)

                # Display image
                cv2.imshow('Advanced Gesture Controller', image)

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC
                    break
                elif key == ord('c'):
                    self.cursor_enabled = not self.cursor_enabled
                    print(f"🖱️ Cursor: {'ON' if self.cursor_enabled else 'OFF'}")
                elif key == ord('k'):
                    self.click_enabled = not self.click_enabled
                    print(f"🖱️ Click: {'ON' if self.click_enabled else 'OFF'}")
                elif key == ord('s'):
                    # Adjust sensitivity
                    self.sensitivity = (self.sensitivity + 0.2) % 3.0 + 0.5
                    print(f"🎯 Sensitivity: {self.sensitivity:.1f}")
                elif key == ord('r'):
                    # Reset drag mode
                    if self.drag_mode:
                        pyautogui.mouseUp()
                        self.drag_mode = False
                        print("🔓 Drag Mode Reset")

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
        self.rl_agent.save_learning_data('gesture_learning.json')

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
        print(f"   Gesture attempts: {sum(self.rl_agent.gesture_attempts.values())}")
        print("✅ Cleanup completed")

def main():
    """Main entry point"""
    try:
        controller = GestureController()
        controller.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Application error: {e}")

if __name__ == "__main__":
    main()
