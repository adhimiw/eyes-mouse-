"""
Advanced Eye Gesture Detection System
Provides sophisticated wink detection, head tilt recognition, and intentional gesture filtering
"""

import time
import math
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from collections import deque
import logging

class AdvancedEyeGestureDetector:
    def __init__(self, config_manager):
        self.config = config_manager

        # Gesture state tracking
        self.last_wink_time = {"left": 0, "right": 0}
        self.last_head_tilt_time = 0
        self.last_intentional_blink_time = 0

        # Eye state history for pattern analysis
        self.left_eye_history = deque(maxlen=15)
        self.right_eye_history = deque(maxlen=15)
        self.head_pose_history = deque(maxlen=10)

        # Gesture detection parameters
        self.blink_threshold = self.config.get_setting("gestures", "blink_threshold", 0.008)
        self.wink_threshold = self.config.get_setting("gestures", "wink_threshold", 0.006)
        self.head_tilt_threshold = self.config.get_setting("gestures", "head_tilt_threshold", 15.0)

        # Cooldown periods
        self.gesture_cooldown = self.config.get_setting("gestures", "gesture_cooldown", 1.0)
        self.wink_cooldown = self.config.get_setting("gestures", "wink_cooldown", 0.8)
        self.head_tilt_cooldown = self.config.get_setting("gestures", "head_tilt_cooldown", 1.0)

        # Feature flags - Default to False for safety
        self.enable_wink_clicks = self.config.get_setting("gestures", "enable_wink_clicks", False)
        self.enable_head_tilt_scroll = self.config.get_setting("gestures", "enable_head_tilt_scroll", False)

        logging.info("Advanced eye gesture detector initialized")

    def process_eye_data(self, tracking_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process eye tracking data and detect advanced gestures"""
        current_time = time.time()
        actions = []

        if not tracking_data.get("landmarks"):
            return actions

        landmarks = tracking_data["landmarks"]

        # Calculate individual eye ratios
        left_ratio = tracking_data.get("left_eye_ratio", 0.0)
        right_ratio = tracking_data.get("right_eye_ratio", 0.0)

        # Update eye state history
        self.left_eye_history.append((left_ratio, current_time))
        self.right_eye_history.append((right_ratio, current_time))

        # Calculate head pose for tilt detection
        head_pose = self._calculate_head_pose(landmarks)
        if head_pose:
            self.head_pose_history.append((head_pose, current_time))

        # Detect winks (if enabled)
        if self.enable_wink_clicks:
            wink_actions = self._detect_winks(current_time)
            actions.extend(wink_actions)

        # Detect head tilts for scrolling (if enabled)
        if self.enable_head_tilt_scroll:
            tilt_action = self._detect_head_tilt_scroll(current_time)
            if tilt_action:
                actions.append(tilt_action)

        # Detect intentional blinks (both eyes, deliberate duration)
        intentional_blink = self._detect_intentional_blink(current_time)
        if intentional_blink:
            actions.append(intentional_blink)

        return actions

    def _detect_winks(self, current_time: float) -> List[Dict[str, Any]]:
        """Detect left and right eye winks for clicking"""
        actions = []

        if len(self.left_eye_history) < 5 or len(self.right_eye_history) < 5:
            return actions

        # Check for left eye wink (right eye stays open)
        left_wink = self._is_wink_pattern(self.left_eye_history, self.right_eye_history, "left")
        if left_wink and current_time - self.last_wink_time["left"] > self.wink_cooldown:
            actions.append({
                "type": "left_wink",
                "action": "left_click",
                "timestamp": current_time,
                "confidence": left_wink
            })
            self.last_wink_time["left"] = current_time
            logging.info("Left wink detected -> Left click")

        # Check for right eye wink (left eye stays open)
        right_wink = self._is_wink_pattern(self.right_eye_history, self.left_eye_history, "right")
        if right_wink and current_time - self.last_wink_time["right"] > self.wink_cooldown:
            actions.append({
                "type": "right_wink",
                "action": "right_click",
                "timestamp": current_time,
                "confidence": right_wink
            })
            self.last_wink_time["right"] = current_time
            logging.info("Right wink detected -> Right click")

        return actions

    def _is_wink_pattern(self, winking_eye: deque, other_eye: deque, eye_name: str) -> Optional[float]:
        """Check if eye pattern matches a deliberate wink"""
        if len(winking_eye) < 5 or len(other_eye) < 5:
            return None

        # Get recent ratios
        wink_ratios = [ratio for ratio, _ in list(winking_eye)[-5:]]
        other_ratios = [ratio for ratio, _ in list(other_eye)[-5:]]

        # Check if winking eye is closed
        wink_avg = sum(wink_ratios) / len(wink_ratios)
        wink_closed = wink_avg < self.wink_threshold

        # Check if other eye is open
        other_avg = sum(other_ratios) / len(other_ratios)
        other_open = other_avg > self.blink_threshold * 1.5

        # Check for deliberate pattern (closed for right duration)
        if wink_closed and other_open:
            # Check duration of wink
            wink_duration = self._calculate_gesture_duration(winking_eye, self.wink_threshold)
            if 0.2 <= wink_duration <= 0.6:  # Deliberate wink duration
                confidence = min(1.0, (other_avg - wink_avg) * 100)
                return confidence

        return None

    def _detect_intentional_blink(self, current_time: float) -> Optional[Dict[str, Any]]:
        """Detect intentional blinks (both eyes closed deliberately)"""
        if len(self.left_eye_history) < 8 or len(self.right_eye_history) < 8:
            return None

        # Check cooldown
        if current_time - self.last_intentional_blink_time < self.gesture_cooldown:
            return None

        # Get recent ratios
        left_ratios = [ratio for ratio, _ in list(self.left_eye_history)[-8:]]
        right_ratios = [ratio for ratio, _ in list(self.right_eye_history)[-8:]]

        # Check if both eyes are closed
        left_avg = sum(left_ratios) / len(left_ratios)
        right_avg = sum(right_ratios) / len(right_ratios)

        both_closed = left_avg < self.blink_threshold and right_avg < self.blink_threshold

        if both_closed:
            # Check for intentional duration
            blink_duration = self._calculate_gesture_duration(self.left_eye_history, self.blink_threshold)
            min_duration = self.config.get_setting("gestures", "intentional_blink_duration", 0.3)
            max_duration = self.config.get_setting("gestures", "max_blink_duration", 0.8)

            if min_duration <= blink_duration <= max_duration:
                self.last_intentional_blink_time = current_time
                return {
                    "type": "intentional_blink",
                    "action": "middle_click",
                    "timestamp": current_time,
                    "duration": blink_duration
                }

        return None

    def _calculate_head_pose(self, landmarks) -> Optional[Dict[str, float]]:
        """Calculate head pose angles from facial landmarks"""
        try:
            # Use key facial landmarks for pose estimation
            nose_tip = landmarks[1]  # Nose tip
            left_eye = landmarks[33]  # Left eye corner
            right_eye = landmarks[362]  # Right eye corner
            chin = landmarks[175]  # Chin

            # Calculate roll (head tilt left/right)
            eye_center_x = (left_eye.x + right_eye.x) / 2
            eye_center_y = (left_eye.y + right_eye.y) / 2

            # Calculate angle between eye line and horizontal
            eye_angle = math.atan2(right_eye.y - left_eye.y, right_eye.x - left_eye.x)
            roll_degrees = math.degrees(eye_angle)

            # Calculate pitch (head tilt up/down) - Fixed calculation
            face_height = abs(chin.y - nose_tip.y)
            nose_offset = nose_tip.y - eye_center_y
            pitch_degrees = math.degrees(math.atan2(nose_offset, face_height))

            return {
                "roll": roll_degrees,
                "pitch": pitch_degrees,
                "yaw": 0.0  # Not implemented for now
            }
        except Exception as e:
            logging.error(f"Error calculating head pose: {e}")
            return None

    def _detect_head_tilt_scroll(self, current_time: float) -> Optional[Dict[str, Any]]:
        """Detect head tilt gestures for scrolling"""
        if len(self.head_pose_history) < 5:
            return None

        # Check cooldown
        if current_time - self.last_head_tilt_time < self.head_tilt_cooldown:
            return None

        # Get recent head poses
        recent_poses = list(self.head_pose_history)[-5:]

        # Calculate average tilt
        avg_roll = sum(pose[0]["roll"] for pose in recent_poses) / len(recent_poses)
        avg_pitch = sum(pose[0]["pitch"] for pose in recent_poses) / len(recent_poses)

        # Check for significant tilt
        if abs(avg_roll) > self.head_tilt_threshold:
            self.last_head_tilt_time = current_time

            if avg_roll > self.head_tilt_threshold:
                return {
                    "type": "head_tilt",
                    "action": "scroll_right",
                    "timestamp": current_time,
                    "angle": avg_roll
                }
            elif avg_roll < -self.head_tilt_threshold:
                return {
                    "type": "head_tilt",
                    "action": "scroll_left",
                    "timestamp": current_time,
                    "angle": avg_roll
                }

        if abs(avg_pitch) > self.head_tilt_threshold:
            self.last_head_tilt_time = current_time

            if avg_pitch > self.head_tilt_threshold:
                return {
                    "type": "head_tilt",
                    "action": "scroll_down",
                    "timestamp": current_time,
                    "angle": avg_pitch
                }
            elif avg_pitch < -self.head_tilt_threshold:
                return {
                    "type": "head_tilt",
                    "action": "scroll_up",
                    "timestamp": current_time,
                    "angle": avg_pitch
                }

        return None

    def _calculate_gesture_duration(self, eye_history: deque, threshold: float) -> float:
        """Calculate how long an eye has been in a particular state"""
        if len(eye_history) < 2:
            return 0.0

        # Find the start of the current state
        current_state = eye_history[-1][0] < threshold
        duration = 0.0

        for i in range(len(eye_history) - 1, 0, -1):
            ratio, timestamp = eye_history[i]
            prev_ratio, prev_timestamp = eye_history[i-1]

            state = ratio < threshold
            if state == current_state:
                duration += timestamp - prev_timestamp
            else:
                break

        return duration

    def reset_cooldowns(self):
        """Reset all gesture cooldowns (for testing/debugging)"""
        current_time = time.time()
        self.last_wink_time = {"left": 0, "right": 0}
        self.last_head_tilt_time = 0
        self.last_intentional_blink_time = 0
        logging.info("All gesture cooldowns reset")
