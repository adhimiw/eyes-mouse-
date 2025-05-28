"""
OpenCV-based Eye Tracking Engine (MediaPipe Alternative)
Provides eye tracking using OpenCV's built-in face and eye detection
"""

import cv2
import numpy as np
import time
import math
from typing import Tuple, List, Optional, Dict, Any
import logging
from collections import deque

class EyeTrackerOpenCV:
    def __init__(self, config_manager):
        self.config = config_manager

        # Load OpenCV cascade classifiers
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        except Exception as e:
            logging.error(f"Failed to load cascade classifiers: {e}")
            raise

        # Camera setup
        self.camera = None
        self.frame_width = 640
        self.frame_height = 480

        # Tracking state
        self.is_calibrated = False
        self.calibration_data = {}
        self.tracking_quality = 0.0
        self.last_eye_position = None

        # Smoothing and filtering
        self.position_history = deque(maxlen=10)
        self.velocity_history = deque(maxlen=5)

        # Blink detection
        self.left_eye_ratio_history = deque(maxlen=5)
        self.right_eye_ratio_history = deque(maxlen=5)
        self.blink_threshold = self.config.get_setting("gestures", "blink_threshold", 0.25)

        # Performance monitoring
        self.frame_times = deque(maxlen=30)
        self.processing_times = deque(maxlen=30)

        # Eye tracking state
        self.last_face_rect = None
        self.face_lost_frames = 0

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
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        tracking_data = {
            "frame": frame,
            "face_rect": None,
            "eyes": [],
            "eye_position": None,
            "blink_detected": False,
            "tracking_quality": 0.0,
            "left_eye_ratio": 0.0,
            "right_eye_ratio": 0.0
        }

        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            # Use the largest face
            face = max(faces, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = face
            tracking_data["face_rect"] = face
            self.last_face_rect = face
            self.face_lost_frames = 0

            # Extract face region
            face_gray = gray[y:y+h, x:x+w]
            face_color = frame[y:y+h, x:x+w]

            # Detect eyes within face region
            eyes = self.eye_cascade.detectMultiScale(face_gray, 1.1, 5)

            if len(eyes) >= 2:
                # Sort eyes by x-coordinate (left to right)
                eyes = sorted(eyes, key=lambda eye: eye[0])
                tracking_data["eyes"] = eyes

                # Calculate eye position
                eye_position = self._calculate_eye_position_from_eyes(eyes, face, frame.shape)
                if eye_position:
                    # Apply smoothing
                    smoothed_position = self._apply_smoothing(eye_position)
                    tracking_data["eye_position"] = smoothed_position

                    # Calculate tracking quality
                    tracking_data["tracking_quality"] = self._calculate_tracking_quality(len(eyes))

                    # Detect blinks (simplified for OpenCV)
                    left_ratio, right_ratio = self._calculate_eye_ratios_opencv(eyes, face_gray)
                    tracking_data["left_eye_ratio"] = left_ratio
                    tracking_data["right_eye_ratio"] = right_ratio
                    tracking_data["blink_detected"] = self._detect_blink(left_ratio, right_ratio)

                    # Draw debug information
                    self._draw_debug_info(frame, face, eyes)
        else:
            self.face_lost_frames += 1
            # Use last known face position for a few frames
            if self.last_face_rect is not None and self.face_lost_frames < 10:
                tracking_data["face_rect"] = self.last_face_rect

        # Update performance metrics
        processing_time = time.time() - start_time
        self.processing_times.append(processing_time)

        return frame, tracking_data

    def _calculate_eye_position_from_eyes(self, eyes, face_rect, frame_shape) -> Optional[Tuple[float, float]]:
        """Calculate normalized eye position from detected eyes"""
        try:
            if len(eyes) < 2:
                return None

            frame_h, frame_w = frame_shape[:2]
            face_x, face_y, face_w, face_h = face_rect

            # Use the center point between the two eyes
            left_eye = eyes[0]  # Leftmost eye
            right_eye = eyes[1]  # Rightmost eye

            # Calculate centers of each eye
            left_center_x = face_x + left_eye[0] + left_eye[2] // 2
            left_center_y = face_y + left_eye[1] + left_eye[3] // 2

            right_center_x = face_x + right_eye[0] + right_eye[2] // 2
            right_center_y = face_y + right_eye[1] + right_eye[3] // 2

            # Average position between eyes
            center_x = (left_center_x + right_center_x) / 2
            center_y = (left_center_y + right_center_y) / 2

            # Normalize to 0-1 range
            norm_x = center_x / frame_w
            norm_y = center_y / frame_h

            return (norm_x, norm_y)
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

    def _calculate_eye_ratios_opencv(self, eyes, face_gray) -> Tuple[float, float]:
        """Calculate eye aspect ratios for blink detection using OpenCV"""
        try:
            if len(eyes) < 2:
                return 0.0, 0.0

            left_eye = eyes[0]
            right_eye = eyes[1]

            # Calculate aspect ratios (height/width)
            left_ratio = left_eye[3] / left_eye[2] if left_eye[2] > 0 else 0.0
            right_ratio = right_eye[3] / right_eye[2] if right_eye[2] > 0 else 0.0

            return left_ratio, right_ratio
        except Exception as e:
            logging.error(f"Error calculating eye ratios: {e}")
            return 0.0, 0.0

    def _detect_blink(self, left_ratio: float, right_ratio: float) -> bool:
        """Detect blink based on eye aspect ratios"""
        self.left_eye_ratio_history.append(left_ratio)
        self.right_eye_ratio_history.append(right_ratio)

        if len(self.left_eye_ratio_history) < 3:
            return False

        # Average ratio for stability
        avg_left = sum(self.left_eye_ratio_history) / len(self.left_eye_ratio_history)
        avg_right = sum(self.right_eye_ratio_history) / len(self.right_eye_ratio_history)

        # Detect blink if both eyes are below threshold (smaller aspect ratio = more closed)
        blink_threshold = self.config.get_setting("gestures", "blink_threshold", 0.25)
        return avg_left < blink_threshold and avg_right < blink_threshold

    def _calculate_tracking_quality(self, num_eyes_detected: int) -> float:
        """Calculate tracking quality score (0.0 to 1.0)"""
        try:
            # Base quality on number of eyes detected
            quality = min(num_eyes_detected / 2.0, 1.0)

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

    def _draw_debug_info(self, frame, face_rect, eyes):
        """Draw debug information on frame"""
        x, y, w, h = face_rect
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 255, 0), 2)

    def map_eye_to_screen(self, eye_position: Tuple[float, float], screen_size: Tuple[int, int]) -> Tuple[int, int]:
        """Map eye position to screen coordinates"""
        # Simple direct mapping
        screen_x = int(eye_position[0] * screen_size[0])
        screen_y = int(eye_position[1] * screen_size[1])

        # Apply dead zone
        dead_zone = self.config.get_setting("tracking", "dead_zone_radius", 10)
        if self.last_eye_position:
            last_screen_x = int(self.last_eye_position[0] * screen_size[0])
            last_screen_y = int(self.last_eye_position[1] * screen_size[1])
            distance = math.sqrt((screen_x - last_screen_x)**2 + (screen_y - last_screen_y)**2)
            if distance < dead_zone:
                return (last_screen_x, last_screen_y)

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

    def start_calibration(self, num_points: int = 9) -> List[Tuple[float, float]]:
        """Start calibration process and return calibration points"""
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
            # Simple calibration completion for OpenCV version
            self.is_calibrated = True
            return True
        return False

    def cleanup(self):
        """Clean up resources"""
        if self.camera:
            self.camera.release()
            self.camera = None
