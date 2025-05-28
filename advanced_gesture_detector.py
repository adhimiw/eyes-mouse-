#!/usr/bin/env python3
"""
Advanced Eye and Head Gesture Detection System
Implements sophisticated gesture recognition for eye winks and head movements
"""

import numpy as np
import cv2
import time
import math
from typing import Dict, List, Tuple, Optional
from collections import deque
from enum import Enum

class GestureType(Enum):
    LEFT_WINK = "left_wink"
    RIGHT_WINK = "right_wink"
    BOTH_BLINK = "both_blink"
    HEAD_TILT_DOWN = "head_tilt_down"
    HEAD_TILT_UP = "head_tilt_up"
    HEAD_TILT_LEFT = "head_tilt_left"
    HEAD_TILT_RIGHT = "head_tilt_right"

class AdvancedGestureDetector:
    def __init__(self):
        """Initialize advanced gesture detection system"""

        # Eye landmark indices for MediaPipe face mesh
        self.LEFT_EYE_LANDMARKS = {
            'upper': [159, 158, 157, 173],
            'lower': [145, 144, 163, 7],
            'left_corner': 33,
            'right_corner': 133
        }

        self.RIGHT_EYE_LANDMARKS = {
            'upper': [386, 385, 384, 398],
            'lower': [374, 373, 390, 249],
            'left_corner': 362,
            'right_corner': 263
        }

        # Head pose landmarks
        self.HEAD_POSE_LANDMARKS = {
            'nose_tip': 1,
            'chin': 18,
            'left_ear': 234,
            'right_ear': 454,
            'forehead': 10
        }

        # Detection thresholds
        self.EYE_ASPECT_RATIO_THRESHOLD = 0.25  # For normal blink detection
        self.WINK_THRESHOLD = 0.15  # Less sensitive for deliberate winks only
        self.HEAD_TILT_THRESHOLD = 25.0  # Degrees - Increased for less sensitivity

        # Gesture state tracking
        self.gesture_history = deque(maxlen=10)
        self.last_gesture_time = {}
        self.gesture_cooldowns = {
            GestureType.LEFT_WINK: 1.0,
            GestureType.RIGHT_WINK: 1.0,
            GestureType.BOTH_BLINK: 1.5,
            GestureType.HEAD_TILT_DOWN: 1.0,
            GestureType.HEAD_TILT_UP: 1.0,
            GestureType.HEAD_TILT_LEFT: 1.0,
            GestureType.HEAD_TILT_RIGHT: 1.0
        }

        # Initialize gesture timing
        for gesture_type in GestureType:
            self.last_gesture_time[gesture_type] = 0

        # Smoothing buffers
        self.left_eye_ratio_buffer = deque(maxlen=5)
        self.right_eye_ratio_buffer = deque(maxlen=5)
        self.head_pose_buffer = deque(maxlen=3)

        print("✅ Advanced Gesture Detector initialized")

    def calculate_eye_aspect_ratio(self, eye_landmarks, landmarks, frame_shape):
        """Calculate eye aspect ratio for blink/wink detection"""
        try:
            frame_h, frame_w = frame_shape[:2]

            # Get eye points
            upper_points = [landmarks[i] for i in eye_landmarks['upper']]
            lower_points = [landmarks[i] for i in eye_landmarks['lower']]
            left_corner = landmarks[eye_landmarks['left_corner']]
            right_corner = landmarks[eye_landmarks['right_corner']]

            # Calculate vertical distances
            vertical_distances = []
            for upper, lower in zip(upper_points, lower_points):
                dist = abs(upper.y - lower.y)
                vertical_distances.append(dist)

            # Calculate horizontal distance
            horizontal_distance = abs(right_corner.x - left_corner.x)

            # Eye aspect ratio
            avg_vertical = sum(vertical_distances) / len(vertical_distances)
            ear = avg_vertical / horizontal_distance if horizontal_distance > 0 else 0

            return ear

        except Exception as e:
            return 0.0

    def detect_eye_states(self, landmarks, frame_shape):
        """Detect individual eye states (open/closed/wink)"""
        try:
            # Calculate eye aspect ratios
            left_ear = self.calculate_eye_aspect_ratio(
                self.LEFT_EYE_LANDMARKS, landmarks, frame_shape
            )
            right_ear = self.calculate_eye_aspect_ratio(
                self.RIGHT_EYE_LANDMARKS, landmarks, frame_shape
            )

            # Add to smoothing buffers
            self.left_eye_ratio_buffer.append(left_ear)
            self.right_eye_ratio_buffer.append(right_ear)

            # Calculate smoothed ratios
            if len(self.left_eye_ratio_buffer) >= 3:
                left_ear_smooth = sum(self.left_eye_ratio_buffer) / len(self.left_eye_ratio_buffer)
                right_ear_smooth = sum(self.right_eye_ratio_buffer) / len(self.right_eye_ratio_buffer)
            else:
                left_ear_smooth = left_ear
                right_ear_smooth = right_ear

            # Determine eye states
            left_eye_closed = left_ear_smooth < self.WINK_THRESHOLD
            right_eye_closed = right_ear_smooth < self.WINK_THRESHOLD

            return {
                'left_eye_closed': left_eye_closed,
                'right_eye_closed': right_eye_closed,
                'left_ear': left_ear_smooth,
                'right_ear': right_ear_smooth
            }

        except Exception as e:
            return {
                'left_eye_closed': False,
                'right_eye_closed': False,
                'left_ear': 0.0,
                'right_ear': 0.0
            }

    def calculate_head_pose(self, landmarks, frame_shape):
        """Calculate head pose angles for tilt detection"""
        try:
            frame_h, frame_w = frame_shape[:2]

            # Get key facial landmarks
            nose_tip = landmarks[self.HEAD_POSE_LANDMARKS['nose_tip']]
            chin = landmarks[self.HEAD_POSE_LANDMARKS['chin']]
            left_ear = landmarks[self.HEAD_POSE_LANDMARKS['left_ear']]
            right_ear = landmarks[self.HEAD_POSE_LANDMARKS['right_ear']]
            forehead = landmarks[self.HEAD_POSE_LANDMARKS['forehead']]

            # Convert to pixel coordinates
            nose_tip_px = (nose_tip.x * frame_w, nose_tip.y * frame_h)
            chin_px = (chin.x * frame_w, chin.y * frame_h)
            left_ear_px = (left_ear.x * frame_w, left_ear.y * frame_h)
            right_ear_px = (right_ear.x * frame_w, right_ear.y * frame_h)
            forehead_px = (forehead.x * frame_w, forehead.y * frame_h)

            # Calculate roll angle (left/right tilt)
            ear_vector = (right_ear_px[0] - left_ear_px[0], right_ear_px[1] - left_ear_px[1])
            roll_angle = math.degrees(math.atan2(ear_vector[1], ear_vector[0]))

            # Calculate pitch angle (up/down tilt)
            face_vector = (nose_tip_px[0] - chin_px[0], nose_tip_px[1] - chin_px[1])
            pitch_angle = math.degrees(math.atan2(face_vector[1], face_vector[0])) - 90

            # Normalize angles
            roll_angle = self.normalize_angle(roll_angle)
            pitch_angle = self.normalize_angle(pitch_angle)

            return {
                'roll': roll_angle,
                'pitch': pitch_angle,
                'landmarks_detected': True
            }

        except Exception as e:
            return {
                'roll': 0.0,
                'pitch': 0.0,
                'landmarks_detected': False
            }

    def normalize_angle(self, angle):
        """Normalize angle to [-180, 180] range"""
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        return angle

    def detect_gestures(self, landmarks, frame_shape):
        """Main gesture detection function"""
        current_time = time.time()
        detected_gestures = []

        # Detect eye states
        eye_states = self.detect_eye_states(landmarks, frame_shape)

        # Detect head pose
        head_pose = self.calculate_head_pose(landmarks, frame_shape)

        # Add to head pose buffer for smoothing
        self.head_pose_buffer.append(head_pose)

        # Smooth head pose
        if len(self.head_pose_buffer) >= 2:
            avg_roll = sum(pose['roll'] for pose in self.head_pose_buffer) / len(self.head_pose_buffer)
            avg_pitch = sum(pose['pitch'] for pose in self.head_pose_buffer) / len(self.head_pose_buffer)
        else:
            avg_roll = head_pose['roll']
            avg_pitch = head_pose['pitch']

        # Eye gesture detection
        left_closed = eye_states['left_eye_closed']
        right_closed = eye_states['right_eye_closed']

        # Left wink detection (left eye closed, right eye open)
        if (left_closed and not right_closed and
            current_time - self.last_gesture_time[GestureType.LEFT_WINK] > self.gesture_cooldowns[GestureType.LEFT_WINK]):
            detected_gestures.append({
                'type': GestureType.LEFT_WINK,
                'confidence': 1.0 - eye_states['left_ear'],
                'timestamp': current_time
            })
            self.last_gesture_time[GestureType.LEFT_WINK] = current_time

        # Right wink detection (right eye closed, left eye open)
        if (right_closed and not left_closed and
            current_time - self.last_gesture_time[GestureType.RIGHT_WINK] > self.gesture_cooldowns[GestureType.RIGHT_WINK]):
            detected_gestures.append({
                'type': GestureType.RIGHT_WINK,
                'confidence': 1.0 - eye_states['right_ear'],
                'timestamp': current_time
            })
            self.last_gesture_time[GestureType.RIGHT_WINK] = current_time

        # Both eyes blink detection
        if (left_closed and right_closed and
            current_time - self.last_gesture_time[GestureType.BOTH_BLINK] > self.gesture_cooldowns[GestureType.BOTH_BLINK]):
            detected_gestures.append({
                'type': GestureType.BOTH_BLINK,
                'confidence': (2.0 - eye_states['left_ear'] - eye_states['right_ear']) / 2,
                'timestamp': current_time
            })
            self.last_gesture_time[GestureType.BOTH_BLINK] = current_time

        # Head tilt gesture detection
        if head_pose['landmarks_detected']:
            # Head tilt down (positive pitch)
            if (avg_pitch > self.HEAD_TILT_THRESHOLD and
                current_time - self.last_gesture_time[GestureType.HEAD_TILT_DOWN] > self.gesture_cooldowns[GestureType.HEAD_TILT_DOWN]):
                detected_gestures.append({
                    'type': GestureType.HEAD_TILT_DOWN,
                    'confidence': min(1.0, abs(avg_pitch) / 30.0),
                    'angle': avg_pitch,
                    'timestamp': current_time
                })
                self.last_gesture_time[GestureType.HEAD_TILT_DOWN] = current_time

            # Head tilt up (negative pitch)
            if (avg_pitch < -self.HEAD_TILT_THRESHOLD and
                current_time - self.last_gesture_time[GestureType.HEAD_TILT_UP] > self.gesture_cooldowns[GestureType.HEAD_TILT_UP]):
                detected_gestures.append({
                    'type': GestureType.HEAD_TILT_UP,
                    'confidence': min(1.0, abs(avg_pitch) / 30.0),
                    'angle': avg_pitch,
                    'timestamp': current_time
                })
                self.last_gesture_time[GestureType.HEAD_TILT_UP] = current_time

            # Head tilt left (negative roll)
            if (avg_roll < -self.HEAD_TILT_THRESHOLD and
                current_time - self.last_gesture_time[GestureType.HEAD_TILT_LEFT] > self.gesture_cooldowns[GestureType.HEAD_TILT_LEFT]):
                detected_gestures.append({
                    'type': GestureType.HEAD_TILT_LEFT,
                    'confidence': min(1.0, abs(avg_roll) / 30.0),
                    'angle': avg_roll,
                    'timestamp': current_time
                })
                self.last_gesture_time[GestureType.HEAD_TILT_LEFT] = current_time

            # Head tilt right (positive roll)
            if (avg_roll > self.HEAD_TILT_THRESHOLD and
                current_time - self.last_gesture_time[GestureType.HEAD_TILT_RIGHT] > self.gesture_cooldowns[GestureType.HEAD_TILT_RIGHT]):
                detected_gestures.append({
                    'type': GestureType.HEAD_TILT_RIGHT,
                    'confidence': min(1.0, abs(avg_roll) / 30.0),
                    'angle': avg_roll,
                    'timestamp': current_time
                })
                self.last_gesture_time[GestureType.HEAD_TILT_RIGHT] = current_time

        # Add to gesture history
        for gesture in detected_gestures:
            self.gesture_history.append(gesture)

        return detected_gestures, eye_states, head_pose

    def get_debug_info(self):
        """Get debug information for the gesture detector"""
        return {
            'gesture_history': list(self.gesture_history),
            'last_gesture_times': {k.value: v for k, v in self.last_gesture_time.items()},
            'buffer_sizes': {
                'left_eye': len(self.left_eye_ratio_buffer),
                'right_eye': len(self.right_eye_ratio_buffer),
                'head_pose': len(self.head_pose_buffer)
            }
        }
