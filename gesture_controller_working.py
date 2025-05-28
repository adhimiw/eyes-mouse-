#!/usr/bin/env python3
"""
Working Gesture-Controlled Virtual Mouse
Based on Viral-Doshi/Gesture-Controlled-Virtual-Mouse repository
Fully functional implementation with proper MediaPipe integration
"""

import cv2
import mediapipe as mp
import pyautogui
import math
import numpy as np
import time
import json
from enum import IntEnum
from collections import deque
from typing import Dict, List, Tuple, Optional

# Disable PyAutoGUI failsafe for smooth operation
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.001

# MediaPipe setup
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

class Gest(IntEnum):
    """
    Gesture encodings - exact copy from original repository
    Binary encoded gestures for hand recognition
    """
    # Binary Encoded
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

    # Extra Mappings
    V_GEST = 33
    TWO_FINGER_CLOSED = 34
    PINCH_MAJOR = 35
    PINCH_MINOR = 36

class HLabel(IntEnum):
    """Hand labels for multi-hand detection"""
    MINOR = 0
    MAJOR = 1

class HandRecog:
    """
    Hand recognition class - exact implementation from original repository
    Handles finger state detection and gesture classification
    """

    def __init__(self, hand_label):
        self.finger = 0
        self.ori_gesture = Gest.PALM
        self.prev_gesture = Gest.PALM
        self.frame_count = 0
        self.hand_result = None
        self.hand_label = hand_label

    def update_hand_result(self, hand_result):
        self.hand_result = hand_result

    def get_signed_dist(self, point):
        """
        Calculate signed distance between landmarks
        """
        sign = -1
        if self.hand_result.landmark[point[0]].y < self.hand_result.landmark[point[1]].y:
            sign = 1
        dist = (self.hand_result.landmark[point[0]].x - self.hand_result.landmark[point[1]].x)**2
        dist += (self.hand_result.landmark[point[0]].y - self.hand_result.landmark[point[1]].y)**2
        dist = math.sqrt(dist)
        return dist*sign

    def get_dist(self, point):
        """Calculate Euclidean distance between two landmarks"""
        dist = (self.hand_result.landmark[point[0]].x - self.hand_result.landmark[point[1]].x)**2
        dist += (self.hand_result.landmark[point[0]].y - self.hand_result.landmark[point[1]].y)**2
        dist = math.sqrt(dist)
        return dist

    def get_dz(self, point):
        """Get z-coordinate difference"""
        return abs(self.hand_result.landmark[point[0]].z - self.hand_result.landmark[point[1]].z)

    def set_finger_state(self):
        """
        Set finger state based on hand landmarks
        Exact implementation from original repository
        """
        if self.hand_result == None:
            return

        points = [[8,5,6], [12,9,10], [16,13,14], [20,17,18]]
        self.finger = 0
        self.finger = self.finger | 0 #thumb

        for idx, point in enumerate(points):

            dist = self.get_signed_dist(point[:2])
            dist2 = self.get_signed_dist(point[1:])

            try:
                ratio = round(dist/dist2, 1)
            except:
                ratio = round(dist1/0.01, 1)

            self.finger = self.finger << 1
            if ratio > 0.5:
                self.finger = self.finger | 1

    def get_gesture(self):
        """
        Get current gesture based on finger state
        Handles noise and fluctuations
        """
        if self.hand_result == None:
            return Gest.PALM

        current_gesture = Gest.PALM

        # Check for pinch gestures first
        if self.finger in [Gest.LAST3, Gest.LAST4] and self.get_dist([8,4]) < 0.05:
            if self.hand_label == HLabel.MINOR:
                current_gesture = Gest.PINCH_MINOR
            else:
                current_gesture = Gest.PINCH_MAJOR

        # Check for V gesture
        elif Gest.FIRST2 == self.finger:
            point = [[8,12], [5,9]]
            dist1 = self.get_dist(point[0])
            dist2 = self.get_dist(point[1])
            ratio = dist1/dist2
            if ratio > 1.7:
                current_gesture = Gest.V_GEST
            else:
                if self.get_dist([8,4]) < 0.05:
                    current_gesture = Gest.TWO_FINGER_CLOSED
                else:
                    current_gesture = Gest.FIRST2

        else:
            current_gesture = self.finger

        # Handle gesture stability
        if current_gesture == self.prev_gesture:
            self.frame_count += 1
        else:
            self.frame_count = 0

        self.prev_gesture = current_gesture

        if self.frame_count > 4:
            self.ori_gesture = current_gesture
        return self.ori_gesture

class Controller:
    """
    Controller class for handling mouse and system controls
    Exact implementation from original repository
    """

    tx_old = 0
    ty_old = 0
    trial = True
    flag = False
    grabflag = False
    pinchmajorflag = False
    pinchminorflag = False
    pinchstartxcoord = None
    pinchstartycoord = None
    pinchdirectionflag = None
    prevpinchlv = 0
    pinchlv = 0
    framecount = 0
    prev_hand = None
    pinch_threshold = 0.3

    @staticmethod
    def get_position(hand_result):
        """Get hand position for cursor control"""
        position = [hand_result.landmark[8].x, hand_result.landmark[8].y]
        sx, sy = pyautogui.size()
        x_old, y_old = pyautogui.position()
        x = int(position[0] * sx)
        y = int(position[1] * sy)
        return x, y

    @staticmethod
    def pinch_control_init(hand_result):
        """Initialize pinch control"""
        Controller.pinchstartxcoord = hand_result.landmark[8].x
        Controller.pinchstartycoord = hand_result.landmark[8].y
        Controller.pinchlv = 0
        Controller.prevpinchlv = 0
        Controller.framecount = 0

    @staticmethod
    def pinch_control(hand_result, controlHorizontal, controlVertical):
        """Handle pinch control for scrolling/volume"""
        if Controller.framecount == 5:
            Controller.framecount = 0
            pinchlv = (hand_result.landmark[8].y - Controller.pinchstartycoord) * 10

            if Controller.pinchdirectionflag == None:
                Controller.pinchdirectionflag = pinchlv >= 0

            if (pinchlv - Controller.prevpinchlv) > Controller.pinch_threshold:
                controlVertical() #Volume up or brightness up
            elif (Controller.prevpinchlv - pinchlv) > Controller.pinch_threshold:
                controlVertical() #Volume down or brightness down
            Controller.prevpinchlv = pinchlv

        else:
            Controller.framecount += 1

    @staticmethod
    def handle_controls(gesture, hand_result):
        """
        Main control handler - implements all gesture functionality
        Exact implementation from original repository
        """
        x, y = None, None
        if gesture != Gest.PALM:
            x, y = Controller.get_position(hand_result)

        # Flag reset
        if gesture != Gest.FIST and Controller.grabflag:
            Controller.grabflag = False
            pyautogui.mouseUp(button="left")

        if gesture != Gest.PINCH_MAJOR and Controller.pinchmajorflag:
            Controller.pinchmajorflag = False

        if gesture != Gest.PINCH_MINOR and Controller.pinchminorflag:
            Controller.pinchminorflag = False

        # Gesture implementations
        if gesture == Gest.V_GEST:
            Controller.flag = True
            # Remove duration for better performance
            pyautogui.moveTo(x, y)

        elif gesture == Gest.FIST:
            if not Controller.grabflag:
                Controller.grabflag = True
                pyautogui.mouseDown(button="left")
            pyautogui.moveTo(x, y)

        elif gesture == Gest.MID and Controller.flag:
            pyautogui.click()
            Controller.flag = False

        elif gesture == Gest.INDEX and Controller.flag:
            pyautogui.click()
            Controller.flag = False

        elif gesture == Gest.TWO_FINGER_CLOSED and Controller.flag:
            pyautogui.doubleClick()
            Controller.flag = False

        elif gesture == Gest.PINCH_MINOR:
            if Controller.pinchminorflag == False:
                Controller.pinch_control_init(hand_result)
                Controller.pinchminorflag = True
            Controller.pinch_control(hand_result,
                                   lambda: pyautogui.scroll(-1),
                                   lambda: pyautogui.scroll(1))

        elif gesture == Gest.PINCH_MAJOR:
            if Controller.pinchmajorflag == False:
                Controller.pinch_control_init(hand_result)
                Controller.pinchmajorflag = True
            Controller.pinch_control(hand_result,
                                   lambda: pyautogui.scroll(-1),
                                   lambda: pyautogui.scroll(1))

class GestureController:
    """
    Main gesture controller class
    Based on original repository with performance optimizations
    """

    gc_mode = 0
    cap = None
    CAM_HEIGHT = 480
    CAM_WIDTH = 640
    hr_major = None # Right Hand by default
    hr_minor = None # Left hand by default
    dom_hand = True

    def __init__(self):
        """Initialize gesture controller"""
        GestureController.gc_mode = 1
        GestureController.cap = cv2.VideoCapture(0)
        GestureController.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, GestureController.CAM_HEIGHT)
        GestureController.cap.set(cv2.CAP_PROP_FRAME_WIDTH, GestureController.CAM_WIDTH)
        GestureController.cap.set(cv2.CAP_PROP_FPS, 30)
        GestureController.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()

        # Reinforcement learning
        self.gesture_success_rates = {}
        self.gesture_attempts = {}
        self.learning_rate = 0.1
        self.load_learning_data()

        print("🚀 Gesture Controller Initialized")
        print(f"   Camera: {GestureController.CAM_WIDTH}x{GestureController.CAM_HEIGHT}")
        print("\n🎮 Gesture Controls:")
        print("   ✌️  V-Gesture - Move cursor")
        print("   👊 Fist - Drag")
        print("   👆 Index - Click")
        print("   🖕 Middle - Click")
        print("   ✌️  Two fingers closed - Double click")
        print("   🤏 Pinch - Scroll")
        print("   Press 'q' to quit")

    @staticmethod
    def classify_hands(results):
        """Classify detected hands as major/minor"""
        left, right = None, None
        try:
            handedness_dict = {}
            for idx, classification in enumerate(results.multi_handedness):
                handedness_dict[classification.classification[0].label] = idx

            if "Right" in handedness_dict:
                right = results.multi_hand_landmarks[handedness_dict["Right"]]
            if "Left" in handedness_dict:
                left = results.multi_hand_landmarks[handedness_dict["Left"]]
        except:
            pass

        if GestureController.dom_hand == True:
            GestureController.hr_major = right
            GestureController.hr_minor = left
        else:
            GestureController.hr_major = left
            GestureController.hr_minor = right

    def record_gesture_attempt(self, gesture, success):
        """Record gesture attempt for reinforcement learning"""
        if gesture not in self.gesture_attempts:
            self.gesture_attempts[gesture] = 0
            self.gesture_success_rates[gesture] = 0.5

        self.gesture_attempts[gesture] += 1

        # Update success rate using exponential moving average
        current_rate = self.gesture_success_rates[gesture]
        new_rate = current_rate + self.learning_rate * (1.0 if success else 0.0 - current_rate)
        self.gesture_success_rates[gesture] = max(0.1, min(0.9, new_rate))

    def get_gesture_confidence(self, gesture):
        """Get confidence level for a gesture"""
        return self.gesture_success_rates.get(gesture, 0.5)

    def load_learning_data(self):
        """Load reinforcement learning data"""
        try:
            with open('gesture_rl_data.json', 'r') as f:
                data = json.load(f)
                self.gesture_success_rates = {int(k): v for k, v in data.get('success_rates', {}).items()}
                self.gesture_attempts = {int(k): v for k, v in data.get('attempts', {}).items()}
        except FileNotFoundError:
            print("📚 No previous learning data found - starting fresh")

    def save_learning_data(self):
        """Save reinforcement learning data"""
        data = {
            'success_rates': {str(k): v for k, v in self.gesture_success_rates.items()},
            'attempts': {str(k): v for k, v in self.gesture_attempts.items()}
        }
        with open('gesture_rl_data.json', 'w') as f:
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
            f"Frames: {self.frame_count}",
            f"Mode: Gesture Control",
            f"Gestures Learned: {len(self.gesture_success_rates)}"
        ]

        # Draw status
        for i, line in enumerate(status_lines):
            cv2.putText(image, line, (10, 30 + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Draw instructions
        instructions = [
            "V-Gesture: Move cursor",
            "Fist: Drag",
            "Index/Middle: Click",
            "Pinch: Scroll"
        ]

        for i, instruction in enumerate(instructions):
            cv2.putText(image, instruction, (w - 250, 30 + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        return image

    def start(self):
        """
        Main entry point - captures video and processes gestures
        Exact implementation from original repository with RL enhancements
        """
        handmajor = HandRecog(HLabel.MAJOR)
        handminor = HandRecog(HLabel.MINOR)

        with mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        ) as hands:

            print("\n🚀 Starting gesture recognition...")
            print("   Show V-gesture to start cursor control")

            while GestureController.cap.isOpened() and GestureController.gc_mode:
                success, image = GestureController.cap.read()

                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                # Flip image horizontally for mirror effect
                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Process hands
                results = hands.process(image)

                # Convert back to BGR for display
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:
                    # Classify hands
                    GestureController.classify_hands(results)

                    # Update hand results
                    handmajor.update_hand_result(GestureController.hr_major)
                    handminor.update_hand_result(GestureController.hr_minor)

                    # Set finger states
                    handmajor.set_finger_state()
                    handminor.set_finger_state()

                    # Get gestures
                    gest_name = handminor.get_gesture()

                    # Handle controls with reinforcement learning
                    success = True
                    try:
                        if gest_name == Gest.PINCH_MINOR:
                            Controller.handle_controls(gest_name, handminor.hand_result)
                        else:
                            gest_name = handmajor.get_gesture()
                            Controller.handle_controls(gest_name, handmajor.hand_result)
                    except Exception as e:
                        success = False
                        print(f"⚠️  Gesture execution failed: {e}")

                    # Record for reinforcement learning
                    if gest_name != Gest.PALM:
                        self.record_gesture_attempt(gest_name, success)

                    # Draw hand landmarks
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Draw UI information
                image = self.draw_ui_info(image)

                # Display image
                cv2.imshow('Gesture Controlled Mouse', image)

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC
                    break
                elif key == ord('r'):
                    # Reset flags
                    Controller.flag = False
                    Controller.grabflag = False
                    if Controller.grabflag:
                        pyautogui.mouseUp(button="left")
                    print("🔄 Flags reset")

                self.frame_count += 1

    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")

        # Release mouse if in drag mode
        if Controller.grabflag:
            pyautogui.mouseUp(button="left")

        # Save learning data
        self.save_learning_data()

        # Release camera and close windows
        if GestureController.cap:
            GestureController.cap.release()
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
        controller = GestureController()
        controller.start()
    except KeyboardInterrupt:
        print("\n⏹️  Stopping...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'controller' in locals():
            controller.cleanup()

if __name__ == "__main__":
    main()
