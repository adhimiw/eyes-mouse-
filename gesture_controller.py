"""
Advanced Gesture Recognition and Control System
Handles blink detection, eye gestures, and system control actions with improved sensitivity
"""

import time
import pyautogui
import math
from typing import Dict, Any, Optional, Tuple, List
from collections import deque
import logging
from enum import Enum
from eye_gesture_advanced import AdvancedEyeGestureDetector

class GestureType(Enum):
    SINGLE_BLINK = "single_blink"
    DOUBLE_BLINK = "double_blink"
    LONG_BLINK = "long_blink"
    DWELL_CLICK = "dwell_click"
    EYE_GESTURE = "eye_gesture"
    GAZE_SCROLL = "gaze_scroll"
    LEFT_WINK = "left_wink"
    RIGHT_WINK = "right_wink"
    HEAD_TILT = "head_tilt"
    INTENTIONAL_BLINK = "intentional_blink"

class GestureController:
    def __init__(self, config_manager):
        self.config = config_manager

        # Initialize advanced gesture detector
        self.advanced_detector = AdvancedEyeGestureDetector(config_manager)

        # Gesture state tracking
        self.last_blink_time = 0
        self.blink_count = 0
        self.long_blink_start = None
        self.dwell_start_time = None
        self.dwell_position = None
        self.last_action_time = 0

        # Gesture history for pattern recognition
        self.gesture_history = deque(maxlen=10)
        self.position_history = deque(maxlen=20)

        # Control zones for special actions
        self.screen_zones = self._initialize_screen_zones()

        # Gesture cooldown to prevent accidental triggers (increased from 0.3 to 1.0)
        self.gesture_cooldown = self.config.get_setting("gestures", "gesture_cooldown", 1.0)

        # Disable pyautogui failsafe for smooth operation
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01

        # Performance tracking
        self.gesture_stats = {
            "left_clicks": 0,
            "right_clicks": 0,
            "middle_clicks": 0,
            "scrolls": 0,
            "false_positives_prevented": 0
        }

        logging.info("Enhanced gesture controller initialized with advanced detection")

    def _initialize_screen_zones(self) -> Dict[str, Dict[str, float]]:
        """Initialize screen zones for special gestures"""
        screen_w, screen_h = pyautogui.size()

        return {
            "top_edge": {"x1": 0, "y1": 0, "x2": screen_w, "y2": 50},
            "bottom_edge": {"x1": 0, "y1": screen_h-50, "x2": screen_w, "y2": screen_h},
            "left_edge": {"x1": 0, "y1": 0, "x2": 50, "y2": screen_h},
            "right_edge": {"x1": screen_w-50, "y1": 0, "x2": screen_w, "y2": screen_h},
            "top_left": {"x1": 0, "y1": 0, "x2": 100, "y2": 100},
            "top_right": {"x1": screen_w-100, "y1": 0, "x2": screen_w, "y2": 100},
            "bottom_left": {"x1": 0, "y1": screen_h-100, "x2": 100, "y2": screen_h},
            "bottom_right": {"x1": screen_w-100, "y1": screen_h-100, "x2": screen_w, "y2": screen_h}
        }

    def process_tracking_data(self, tracking_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process eye tracking data and generate gesture events with advanced detection"""
        current_time = time.time()
        actions = []

        if not tracking_data.get("eye_position"):
            return actions

        eye_position = tracking_data["eye_position"]
        screen_pos = self._eye_to_screen_coords(eye_position)

        # Update position history
        self.position_history.append((screen_pos, current_time))

        # Move cursor
        self._move_cursor(screen_pos)

        # Use advanced gesture detection instead of simple blink detection
        advanced_actions = self.advanced_detector.process_eye_data(tracking_data)
        for action in advanced_actions:
            processed_action = self._execute_advanced_gesture(action)
            if processed_action:
                actions.append(processed_action)

        # Process dwell clicking only if enabled
        if self.config.get_setting("gestures", "enable_dwell_click", False):
            dwell_action = self._process_dwell_click(screen_pos, current_time)
            if dwell_action:
                actions.append(dwell_action)

        # Process gaze-based scrolling (legacy - now handled by head tilt)
        if not self.config.get_setting("gestures", "enable_head_tilt_scroll", True):
            scroll_action = self._process_gaze_scroll(screen_pos, current_time)
            if scroll_action:
                actions.append(scroll_action)

        # Process screen zone gestures
        zone_action = self._process_screen_zones(screen_pos, current_time)
        if zone_action:
            actions.append(zone_action)

        return actions

    def _eye_to_screen_coords(self, eye_position: Tuple[float, float]) -> Tuple[int, int]:
        """Convert normalized eye position to screen coordinates"""
        screen_w, screen_h = pyautogui.size()

        # Apply sensitivity and acceleration
        sensitivity = self.config.get_setting("tracking", "sensitivity", 1.0)

        x = int(eye_position[0] * screen_w * sensitivity)
        y = int(eye_position[1] * screen_h * sensitivity)

        # Clamp to screen bounds
        x = max(0, min(screen_w - 1, x))
        y = max(0, min(screen_h - 1, y))

        return (x, y)

    def _move_cursor(self, position: Tuple[int, int]):
        """Move cursor with optimized performance"""
        try:
            # Performance optimization: Use direct movement with no duration
            # This eliminates the latency caused by PyAutoGUI's built-in smoothing
            pyautogui.moveTo(position[0], position[1])

        except Exception as e:
            logging.error(f"Error moving cursor: {e}")

    def _process_blink(self, current_time: float) -> List[Dict[str, Any]]:
        """Process blink detection and generate appropriate actions"""
        actions = []

        # Check cooldown
        if current_time - self.last_action_time < self.gesture_cooldown:
            return actions

        # Determine blink type
        time_since_last_blink = current_time - self.last_blink_time
        double_blink_timeout = self.config.get_setting("gestures", "double_blink_timeout", 0.5)

        if time_since_last_blink < double_blink_timeout:
            # Double blink detected
            self.blink_count += 1
            if self.blink_count >= 2:
                actions.append({
                    "type": GestureType.DOUBLE_BLINK,
                    "action": "right_click",
                    "timestamp": current_time
                })
                self._perform_right_click()
                self.blink_count = 0
                self.last_action_time = current_time
        else:
            # Single blink
            if self.blink_count == 0:
                self.blink_count = 1
                # Wait to see if it becomes a double blink
                self.last_blink_time = current_time
            else:
                # Previous single blink, execute it now
                actions.append({
                    "type": GestureType.SINGLE_BLINK,
                    "action": "left_click",
                    "timestamp": current_time
                })
                self._perform_left_click()
                self.blink_count = 1
                self.last_blink_time = current_time
                self.last_action_time = current_time

        return actions

    def _process_dwell_click(self, position: Tuple[int, int], current_time: float) -> Optional[Dict[str, Any]]:
        """Process dwell-time clicking"""
        dwell_time = self.config.get_setting("gestures", "dwell_time", 1.5)
        dwell_threshold = 30  # pixels

        if self.dwell_position is None:
            self.dwell_position = position
            self.dwell_start_time = current_time
            return None

        # Check if cursor has moved significantly
        distance = math.sqrt((position[0] - self.dwell_position[0])**2 +
                           (position[1] - self.dwell_position[1])**2)

        if distance > dwell_threshold:
            # Reset dwell timer
            self.dwell_position = position
            self.dwell_start_time = current_time
            return None

        # Check if dwell time has elapsed
        if current_time - self.dwell_start_time >= dwell_time:
            # Perform dwell click
            self._perform_left_click()
            self.dwell_position = None
            self.dwell_start_time = None
            self.last_action_time = current_time

            return {
                "type": GestureType.DWELL_CLICK,
                "action": "left_click",
                "position": position,
                "timestamp": current_time
            }

        return None

    def _process_gaze_scroll(self, position: Tuple[int, int], current_time: float) -> Optional[Dict[str, Any]]:
        """Process gaze-based scrolling"""
        if len(self.position_history) < 5:
            return None

        # Analyze recent movement for scroll patterns
        recent_positions = list(self.position_history)[-5:]

        # Check for consistent vertical movement
        y_movements = [pos[0][1] - recent_positions[0][0][1] for pos in recent_positions[1:]]

        if all(movement > 10 for movement in y_movements):
            # Scrolling down
            pyautogui.scroll(-3)
            return {
                "type": GestureType.GAZE_SCROLL,
                "action": "scroll_down",
                "timestamp": current_time
            }
        elif all(movement < -10 for movement in y_movements):
            # Scrolling up
            pyautogui.scroll(3)
            return {
                "type": GestureType.GAZE_SCROLL,
                "action": "scroll_up",
                "timestamp": current_time
            }

        return None

    def _process_screen_zones(self, position: Tuple[int, int], current_time: float) -> Optional[Dict[str, Any]]:
        """Process screen zone gestures for special actions"""
        for zone_name, zone_coords in self.screen_zones.items():
            if (zone_coords["x1"] <= position[0] <= zone_coords["x2"] and
                zone_coords["y1"] <= position[1] <= zone_coords["y2"]):

                # Check if gaze has been sustained in this zone
                sustained_time = 2.0  # seconds
                zone_positions = [pos for pos in self.position_history
                                if current_time - pos[1] <= sustained_time and
                                zone_coords["x1"] <= pos[0][0] <= zone_coords["x2"] and
                                zone_coords["y1"] <= pos[0][1] <= zone_coords["y2"]]

                if len(zone_positions) >= 10:  # Sustained gaze
                    action = self._get_zone_action(zone_name)
                    if action:
                        self.last_action_time = current_time
                        return {
                            "type": GestureType.EYE_GESTURE,
                            "action": action,
                            "zone": zone_name,
                            "timestamp": current_time
                        }

        return None

    def _get_zone_action(self, zone_name: str) -> Optional[str]:
        """Get action for specific screen zone"""
        zone_actions = {
            "top_edge": "fullscreen_toggle",
            "bottom_edge": "minimize_window",
            "top_left": "close_window",
            "top_right": "maximize_window",
            "left_edge": "previous_window",
            "right_edge": "next_window"
        }

        action = zone_actions.get(zone_name)
        if action:
            self._perform_zone_action(action)

        return action

    def _execute_advanced_gesture(self, action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute advanced gesture actions with proper logging and stats"""
        try:
            action_type = action.get("action")
            gesture_type = action.get("type")

            if action_type == "left_click":
                self._perform_left_click()
                self.gesture_stats["left_clicks"] += 1
                logging.info(f"Executed left click via {gesture_type}")

            elif action_type == "right_click":
                self._perform_right_click()
                self.gesture_stats["right_clicks"] += 1
                logging.info(f"Executed right click via {gesture_type}")

            elif action_type == "middle_click":
                self._perform_middle_click()
                self.gesture_stats["middle_clicks"] += 1
                logging.info(f"Executed middle click via {gesture_type}")

            elif action_type in ["scroll_up", "scroll_down", "scroll_left", "scroll_right"]:
                self._perform_scroll_action(action_type, action.get("angle", 0))
                self.gesture_stats["scrolls"] += 1
                logging.info(f"Executed {action_type} via {gesture_type}")

            else:
                logging.warning(f"Unknown action type: {action_type}")
                return None

            return action

        except Exception as e:
            logging.error(f"Error executing advanced gesture {action}: {e}")
            return None

    def _perform_left_click(self):
        """Perform left mouse click with enhanced error handling"""
        try:
            pyautogui.click()
            logging.debug("Left click executed successfully")
        except Exception as e:
            logging.error(f"Error performing left click: {e}")

    def _perform_right_click(self):
        """Perform right mouse click with enhanced error handling"""
        try:
            pyautogui.rightClick()
            logging.debug("Right click executed successfully")
        except Exception as e:
            logging.error(f"Error performing right click: {e}")

    def _perform_middle_click(self):
        """Perform middle mouse click"""
        try:
            pyautogui.middleClick()
            logging.debug("Middle click executed successfully")
        except Exception as e:
            logging.error(f"Error performing middle click: {e}")

    def _perform_scroll_action(self, action_type: str, angle: float = 0):
        """Perform scrolling actions based on head tilt or gaze"""
        try:
            scroll_amount = 3

            if action_type == "scroll_up":
                pyautogui.scroll(scroll_amount)
            elif action_type == "scroll_down":
                pyautogui.scroll(-scroll_amount)
            elif action_type == "scroll_left":
                pyautogui.hscroll(-scroll_amount)
            elif action_type == "scroll_right":
                pyautogui.hscroll(scroll_amount)

            logging.debug(f"Scroll action {action_type} executed (angle: {angle:.1f}°)")
        except Exception as e:
            logging.error(f"Error performing scroll action {action_type}: {e}")

    def _perform_zone_action(self, action: str):
        """Perform zone-specific actions"""
        try:
            if action == "fullscreen_toggle":
                pyautogui.press('f11')
            elif action == "minimize_window":
                pyautogui.hotkey('alt', 'f9')
            elif action == "close_window":
                pyautogui.hotkey('alt', 'f4')
            elif action == "maximize_window":
                pyautogui.hotkey('alt', 'f10')
            elif action == "previous_window":
                pyautogui.hotkey('alt', 'shift', 'tab')
            elif action == "next_window":
                pyautogui.hotkey('alt', 'tab')
        except Exception as e:
            logging.error(f"Error performing zone action {action}: {e}")

    def emergency_disable(self):
        """Emergency disable all gesture recognition"""
        self.gesture_cooldown = float('inf')
        self.advanced_detector.reset_cooldowns()
        logging.warning("Gesture recognition emergency disabled")

    def enable(self):
        """Re-enable gesture recognition"""
        self.gesture_cooldown = self.config.get_setting("gestures", "gesture_cooldown", 1.0)
        logging.info("Gesture recognition enabled")

    def get_gesture_stats(self) -> Dict[str, Any]:
        """Get current gesture statistics"""
        return {
            **self.gesture_stats,
            "total_gestures": sum(self.gesture_stats.values()),
            "gesture_cooldown": self.gesture_cooldown,
            "advanced_detection_enabled": True
        }

    def reset_stats(self):
        """Reset gesture statistics"""
        self.gesture_stats = {
            "left_clicks": 0,
            "right_clicks": 0,
            "middle_clicks": 0,
            "scrolls": 0,
            "false_positives_prevented": 0
        }
        logging.info("Gesture statistics reset")
