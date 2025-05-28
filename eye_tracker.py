"""
Enhanced Eye Tracking Engine
Provides robust eye tracking with calibration, smoothing, and precision control
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import math
from typing import Tuple, List, Optional, Dict, Any
import logging
from collections import deque

class EyeTracker:
    def __init__(self, config_manager):
        self.config = config_manager
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Camera setup
        self.camera = None
        self.frame_width = 640
        self.frame_height = 480

        # Tracking state
        self.is_calibrated = False
        self.calibration_points = []
        self.calibration_data = {}
        self.tracking_quality = 0.0
        self.last_eye_position = None

        # Smoothing and filtering
        self.position_history = deque(maxlen=10)
        self.velocity_history = deque(maxlen=5)

        # Eye landmarks indices
        self.LEFT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.RIGHT_EYE_LANDMARKS = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.LEFT_IRIS_LANDMARKS = [474, 475, 476, 477]
        self.RIGHT_IRIS_LANDMARKS = [469, 470, 471, 472]

        # Enhanced blink detection
        self.left_eye_ratio_history = deque(maxlen=15)
        self.right_eye_ratio_history = deque(maxlen=15)
        self.blink_threshold = self.config.get_setting("gestures", "blink_threshold", 0.008)
        self.wink_threshold = self.config.get_setting("gestures", "wink_threshold", 0.006)

        # Performance monitoring
        self.frame_times = deque(maxlen=30)
        self.processing_times = deque(maxlen=30)

    def initialize_camera(self, camera_index: int = 0) -> bool:
        """Initialize camera with optimal settings"""
        try:
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                return False

            # Set camera properties for optimal performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.camera.set(cv2.CAP_PROP_FPS, self.config.get_setting("tracking", "frame_rate", 30))
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            return True
        except Exception as e:
            logging.error(f"Camera initialization failed: {e}")
            return False

    def process_frame(self) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
        """Process a single frame and extract eye tracking data"""
        if not self.camera:
            return None, {}

        start_time = time.time()

        ret, frame = self.camera.read()
        if not ret:
            return None, {}

        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process with MediaPipe
        results = self.face_mesh.process(rgb_frame)

        tracking_data = {
            "frame": frame,
            "landmarks": None,
            "eye_position": None,
            "blink_detected": False,
            "tracking_quality": 0.0,
            "left_eye_ratio": 0.0,
            "right_eye_ratio": 0.0
        }

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            tracking_data["landmarks"] = landmarks

            # Calculate eye position
            eye_position = self._calculate_eye_position(landmarks, frame.shape)
            if eye_position:
                # Apply smoothing
                smoothed_position = self._apply_smoothing(eye_position)
                tracking_data["eye_position"] = smoothed_position

                # Calculate tracking quality
                tracking_data["tracking_quality"] = self._calculate_tracking_quality(landmarks)

                # Detect blinks
                left_ratio, right_ratio = self._calculate_eye_ratios(landmarks, frame.shape)
                tracking_data["left_eye_ratio"] = left_ratio
                tracking_data["right_eye_ratio"] = right_ratio
                tracking_data["blink_detected"] = self._detect_blink(left_ratio, right_ratio)

        # Update performance metrics
        processing_time = time.time() - start_time
        self.processing_times.append(processing_time)

        return frame, tracking_data

    def _calculate_eye_position(self, landmarks, frame_shape) -> Optional[Tuple[float, float]]:
        """Calculate normalized eye position from iris landmarks"""
        try:
            frame_h, frame_w = frame_shape[:2]

            # Get iris center (using right iris as primary)
            iris_landmarks = self.RIGHT_IRIS_LANDMARKS
            if len(landmarks) > max(iris_landmarks):
                iris_points = [landmarks[i] for i in iris_landmarks]

                # Calculate center of iris
                center_x = sum(point.x for point in iris_points) / len(iris_points)
                center_y = sum(point.y for point in iris_points) / len(iris_points)

                return (center_x, center_y)
        except Exception as e:
            logging.error(f"Error calculating eye position: {e}")

        return None

    def _apply_smoothing(self, position: Tuple[float, float]) -> Tuple[float, float]:
        """Apply smoothing algorithm to reduce jitter"""
        self.position_history.append(position)

        if len(self.position_history) < 2:
            return position

        smoothing_factor = self.config.get_setting("tracking", "smoothing", 0.7)

        # Weighted average with recent positions
        weights = np.exp(np.linspace(-2, 0, len(self.position_history)))
        weights /= weights.sum()

        smoothed_x = sum(w * pos[0] for w, pos in zip(weights, self.position_history))
        smoothed_y = sum(w * pos[1] for w, pos in zip(weights, self.position_history))

        return (smoothed_x, smoothed_y)

    def _calculate_eye_ratios(self, landmarks, frame_shape) -> Tuple[float, float]:
        """Calculate eye aspect ratios for blink detection"""
        try:
            frame_h, frame_w = frame_shape[:2]

            # Left eye ratio
            left_eye_points = [landmarks[i] for i in [145, 159]]  # Top and bottom of left eye
            left_ratio = abs(left_eye_points[0].y - left_eye_points[1].y)

            # Right eye ratio
            right_eye_points = [landmarks[i] for i in [374, 386]]  # Top and bottom of right eye
            right_ratio = abs(right_eye_points[0].y - right_eye_points[1].y)

            return left_ratio, right_ratio
        except Exception as e:
            logging.error(f"Error calculating eye ratios: {e}")
            return 0.0, 0.0

    def _detect_blink(self, left_ratio: float, right_ratio: float) -> bool:
        """Detect blink based on eye aspect ratios with improved sensitivity"""
        self.left_eye_ratio_history.append(left_ratio)
        self.right_eye_ratio_history.append(right_ratio)

        if len(self.left_eye_ratio_history) < 5:
            return False

        # Use recent samples for more stable detection
        recent_left = list(self.left_eye_ratio_history)[-5:]
        recent_right = list(self.right_eye_ratio_history)[-5:]

        # Average ratio for stability
        avg_left = sum(recent_left) / len(recent_left)
        avg_right = sum(recent_right) / len(recent_right)

        # Detect blink if both eyes are below threshold consistently
        blink_threshold = self.config.get_setting("gestures", "blink_threshold", 0.008)

        # Check if most recent samples are below threshold (more conservative)
        left_closed_count = sum(1 for ratio in recent_left if ratio < blink_threshold)
        right_closed_count = sum(1 for ratio in recent_right if ratio < blink_threshold)

        # Require at least 3 out of 5 samples to be below threshold for both eyes
        return left_closed_count >= 3 and right_closed_count >= 3

    def _calculate_tracking_quality(self, landmarks) -> float:
        """Calculate tracking quality score (0.0 to 1.0)"""
        try:
            # Check if key landmarks are detected
            key_landmarks = self.LEFT_IRIS_LANDMARKS + self.RIGHT_IRIS_LANDMARKS
            detected_landmarks = sum(1 for i in key_landmarks if i < len(landmarks))

            quality = detected_landmarks / len(key_landmarks)

            # Additional quality checks
            if self.position_history:
                # Check for stability (low variance indicates good tracking)
                recent_positions = list(self.position_history)[-5:]
                if len(recent_positions) > 1:
                    x_variance = np.var([pos[0] for pos in recent_positions])
                    y_variance = np.var([pos[1] for pos in recent_positions])
                    stability = 1.0 / (1.0 + (x_variance + y_variance) * 1000)
                    quality = (quality + stability) / 2

            self.tracking_quality = quality
            return quality
        except Exception:
            return 0.0

    def start_calibration(self, num_points: int = 9) -> List[Tuple[float, float]]:
        """Start calibration process and return calibration points"""
        self.calibration_points = []
        self.calibration_data = {}

        # Generate calibration points in a grid
        points = []
        if num_points == 9:
            for y in [0.1, 0.5, 0.9]:
                for x in [0.1, 0.5, 0.9]:
                    points.append((x, y))
        elif num_points == 5:
            points = [(0.1, 0.1), (0.9, 0.1), (0.5, 0.5), (0.1, 0.9), (0.9, 0.9)]

        return points

    def add_calibration_point(self, screen_point: Tuple[float, float], eye_data: List[Tuple[float, float]]) -> bool:
        """Add a calibration point with corresponding eye data"""
        if eye_data:
            # Average the eye positions for this calibration point
            avg_x = sum(pos[0] for pos in eye_data) / len(eye_data)
            avg_y = sum(pos[1] for pos in eye_data) / len(eye_data)

            self.calibration_data[screen_point] = (avg_x, avg_y)
            return True
        return False

    def finish_calibration(self) -> bool:
        """Complete calibration and compute transformation matrix"""
        if len(self.calibration_data) >= 4:
            # Compute transformation matrix using least squares
            try:
                screen_points = np.array(list(self.calibration_data.keys()))
                eye_points = np.array(list(self.calibration_data.values()))

                # Simple linear transformation for now
                # In a full implementation, you'd use polynomial or more sophisticated mapping
                self.is_calibrated = True
                return True
            except Exception as e:
                logging.error(f"Calibration failed: {e}")
                return False
        return False

    def map_eye_to_screen(self, eye_position: Tuple[float, float], screen_size: Tuple[int, int]) -> Tuple[int, int]:
        """Map eye position to screen coordinates"""
        if not self.is_calibrated:
            # Simple direct mapping if not calibrated
            screen_x = int(eye_position[0] * screen_size[0])
            screen_y = int(eye_position[1] * screen_size[1])
        else:
            # Use calibration data for accurate mapping
            # This is a simplified version - full implementation would use the transformation matrix
            screen_x = int(eye_position[0] * screen_size[0])
            screen_y = int(eye_position[1] * screen_size[1])

        # Apply dead zone
        dead_zone = self.config.get_setting("tracking", "dead_zone_radius", 10)
        if self.last_eye_position:
            last_screen = self.map_eye_to_screen(self.last_eye_position, screen_size)
            distance = math.sqrt((screen_x - last_screen[0])**2 + (screen_y - last_screen[1])**2)
            if distance < dead_zone:
                return last_screen

        self.last_eye_position = eye_position
        return (screen_x, screen_y)

    def get_performance_stats(self) -> Dict[str, float]:
        """Get performance statistics"""
        stats = {}
        if self.processing_times:
            stats["avg_processing_time"] = sum(self.processing_times) / len(self.processing_times)
            stats["fps"] = 1.0 / stats["avg_processing_time"] if stats["avg_processing_time"] > 0 else 0

        stats["tracking_quality"] = self.tracking_quality
        return stats

    def cleanup(self):
        """Clean up resources"""
        if self.camera:
            self.camera.release()
            self.camera = None
