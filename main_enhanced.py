#!/usr/bin/env python3
"""
Enhanced Main Application for Eye-Controlled Computer Interface
Comprehensive system with bug catcher, gesture control, and all working components
"""

import sys
import threading
import time
import logging
import traceback
import subprocess
import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Any, List
from collections import deque
import tkinter as tk
from tkinter import messagebox, ttk

# Import advanced gesture detection modules
from advanced_gesture_detector import AdvancedGestureDetector, GestureType
from gesture_action_processor import GestureActionProcessor

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eye_tracking_enhanced.log'),
        logging.StreamHandler()
    ]
)

class EnhancedEyeControlledInterface:
    def __init__(self):
        """Initialize the enhanced eye-controlled interface system"""
        print("🚀 Initializing Enhanced Eye-Controlled Interface...")

        # Initialize components
        self.setup_mouse_backend()
        self.initialize_mediapipe()
        self.initialize_camera()
        self.setup_tracking_parameters()
        self.setup_gesture_recognition()
        self.setup_advanced_gestures()
        self.setup_bug_catcher()
        self.setup_ui()

        # State management
        self.is_running = False
        self.tracking_thread = None
        self.frame_count = 0
        self.start_time = time.time()

        print("✅ Enhanced Eye-Controlled Interface initialized!")
        self.print_controls()

    def setup_mouse_backend(self):
        """Setup the best available mouse control backend"""
        try:
            subprocess.run(['xdotool', '--version'], capture_output=True, check=True)
            self.mouse_backend = 'xdotool'
            print("✅ Using xdotool backend (Wayland compatible)")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.mouse_backend = 'pyautogui'
            print("⚠️  Using PyAutoGUI backend")

        # Get screen size
        if self.mouse_backend == 'xdotool':
            result = subprocess.run(['xdotool', 'getdisplaygeometry'],
                                  capture_output=True, text=True, check=True)
            self.screen_w, self.screen_h = map(int, result.stdout.strip().split())
        else:
            import pyautogui
            self.screen_w, self.screen_h = pyautogui.size()

        print(f"Screen resolution: {self.screen_w}x{self.screen_h}")

    def initialize_mediapipe(self):
        """Initialize MediaPipe with optimal settings"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        print("✅ MediaPipe initialized")

    def initialize_camera(self):
        """Initialize camera with error handling"""
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            print("❌ Cannot open camera")
            sys.exit(1)

        # Configure camera
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        print("✅ Camera initialized")

    def setup_tracking_parameters(self):
        """Setup tracking parameters"""
        self.sensitivity = 1.0
        self.dead_zone = 0.01
        self.smoothing_factor = 0.8

        # Buffers for smoothing and gesture detection
        self.position_buffer = deque(maxlen=8)
        self.blink_buffer = deque(maxlen=5)
        self.gesture_buffer = deque(maxlen=10)

        # Performance monitoring
        self.mouse_move_count = 0
        self.mouse_move_success = 0
        self.gesture_count = 0

        # Blink detection
        self.blink_threshold = 0.004
        self.last_click_time = 0
        self.click_cooldown = 1.0

        print("✅ Tracking parameters configured")

    def setup_gesture_recognition(self):
        """Setup advanced gesture recognition"""
        self.gesture_patterns = {
            'single_blink': {'action': 'left_click', 'cooldown': 0.5},
            'double_blink': {'action': 'right_click', 'cooldown': 1.0},
            'long_blink': {'action': 'drag_start', 'cooldown': 1.5},
            'eye_left': {'action': 'scroll_left', 'cooldown': 0.3},
            'eye_right': {'action': 'scroll_right', 'cooldown': 0.3},
            'eye_up': {'action': 'scroll_up', 'cooldown': 0.3},
            'eye_down': {'action': 'scroll_down', 'cooldown': 0.3}
        }

        self.last_gesture_time = {}
        for gesture in self.gesture_patterns:
            self.last_gesture_time[gesture] = 0

        print("✅ Gesture recognition configured")

    def setup_advanced_gestures(self):
        """Setup advanced eye and head gesture detection"""
        self.advanced_gesture_detector = AdvancedGestureDetector()
        self.gesture_action_processor = GestureActionProcessor(self.mouse_backend)

        # Advanced gesture statistics
        self.advanced_gesture_stats = {
            'left_winks': 0,
            'right_winks': 0,
            'both_blinks': 0,
            'head_tilts': 0,
            'total_advanced_gestures': 0
        }

        # Visual feedback for gestures
        self.last_gesture_feedback = ""
        self.gesture_feedback_time = 0

        print("✅ Advanced gesture detection configured")

    def setup_bug_catcher(self):
        """Setup comprehensive bug catching and debugging"""
        self.debug_data = {
            'face_detected': [],
            'eye_positions': [],
            'mouse_movements': [],
            'gestures_detected': [],
            'errors': [],
            'performance_metrics': []
        }

        self.debug_mode = True
        self.save_debug_interval = 100  # Save debug data every 100 frames

        print("✅ Bug catcher initialized")

    def setup_ui(self):
        """Setup enhanced UI with comprehensive controls"""
        self.root = tk.Tk()
        self.root.title("Enhanced Eye-Controlled Interface")
        self.root.geometry("800x600")

        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Control buttons
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.start_button = ttk.Button(control_frame, text="Start Tracking", command=self.start_tracking)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(control_frame, text="Stop Tracking", command=self.stop_tracking)
        self.stop_button.grid(row=0, column=1, padx=5)

        self.debug_button = ttk.Button(control_frame, text="Save Debug Data", command=self.save_debug_data)
        self.debug_button.grid(row=0, column=2, padx=5)

        # Status display
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.status_label = ttk.Label(status_frame, text="Ready to start")
        self.status_label.grid(row=0, column=0, sticky=tk.W)

        # Performance metrics
        metrics_frame = ttk.LabelFrame(main_frame, text="Performance Metrics", padding="10")
        metrics_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.fps_label = ttk.Label(metrics_frame, text="FPS: 0")
        self.fps_label.grid(row=0, column=0, sticky=tk.W)

        self.mouse_success_label = ttk.Label(metrics_frame, text="Mouse Success: 0%")
        self.mouse_success_label.grid(row=1, column=0, sticky=tk.W)

        self.gesture_label = ttk.Label(metrics_frame, text="Gestures: 0")
        self.gesture_label.grid(row=2, column=0, sticky=tk.W)

        self.advanced_gesture_label = ttk.Label(metrics_frame, text="Advanced Gestures: 0")
        self.advanced_gesture_label.grid(row=3, column=0, sticky=tk.W)

        self.gesture_feedback_label = ttk.Label(metrics_frame, text="Last Gesture: None", foreground="blue")
        self.gesture_feedback_label.grid(row=4, column=0, sticky=tk.W)

        # Settings
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(settings_frame, text="Sensitivity:").grid(row=0, column=0, sticky=tk.W)
        self.sensitivity_var = tk.DoubleVar(value=self.sensitivity)
        sensitivity_scale = ttk.Scale(settings_frame, from_=0.1, to=3.0, variable=self.sensitivity_var,
                                    orient=tk.HORIZONTAL, command=self.update_sensitivity)
        sensitivity_scale.grid(row=0, column=1, sticky=(tk.W, tk.E))

        print("✅ UI initialized")

    def move_mouse(self, x, y):
        """Move mouse using the best available backend"""
        try:
            self.mouse_move_count += 1

            if self.mouse_backend == 'xdotool':
                result = subprocess.run(['xdotool', 'mousemove', str(int(x)), str(int(y))],
                             capture_output=True, check=True, timeout=0.05)
                # Debug: Print any xdotool errors
                if result.stderr:
                    print(f"⚠️  xdotool stderr: {result.stderr.decode()}")
            else:
                import pyautogui
                pyautogui.moveTo(x, y)

            self.mouse_move_success += 1

            # Debug: Print successful moves occasionally
            if self.mouse_move_count % 60 == 0:
                print(f"🖱️  Mouse moved to ({int(x)}, {int(y)}) - Success rate: {self.mouse_move_success/self.mouse_move_count*100:.1f}%")

            return True
        except Exception as e:
            print(f"❌ Mouse movement failed: {e}")
            if self.debug_mode:
                self.debug_data['errors'].append({
                    'type': 'mouse_movement',
                    'error': str(e),
                    'timestamp': time.time()
                })
            return False

    def click_mouse(self, button='left'):
        """Click mouse using the best available backend"""
        try:
            if self.mouse_backend == 'xdotool':
                button_map = {'left': '1', 'right': '3', 'middle': '2'}
                subprocess.run(['xdotool', 'click', button_map.get(button, '1')],
                             capture_output=True, check=True, timeout=0.5)
            else:
                import pyautogui
                if button == 'left':
                    pyautogui.click()
                elif button == 'right':
                    pyautogui.rightClick()
                elif button == 'middle':
                    pyautogui.middleClick()

            return True
        except Exception as e:
            if self.debug_mode:
                self.debug_data['errors'].append({
                    'type': 'mouse_click',
                    'error': str(e),
                    'timestamp': time.time()
                })
            return False

    def get_iris_position(self, landmarks):
        """Get iris position with multiple fallback methods"""
        try:
            if len(landmarks) > 475:
                right_iris = landmarks[475]
                if len(landmarks) > 468:
                    left_iris = landmarks[468]
                    # Weighted average
                    avg_x = right_iris.x * 0.7 + left_iris.x * 0.3
                    avg_y = right_iris.y * 0.7 + left_iris.y * 0.3
                    return (avg_x, avg_y)
                else:
                    return (right_iris.x, right_iris.y)
        except Exception as e:
            if self.debug_mode:
                self.debug_data['errors'].append({
                    'type': 'iris_detection',
                    'error': str(e),
                    'timestamp': time.time()
                })
        return None

    def apply_smoothing(self, position):
        """Apply smoothing to reduce jitter"""
        self.position_buffer.append(position)

        if len(self.position_buffer) < 2:
            return position

        # Exponential weighted average
        weights = np.exp(np.linspace(-1, 0, len(self.position_buffer)))
        weights /= weights.sum()

        smooth_x = sum(w * pos[0] for w, pos in zip(weights, self.position_buffer))
        smooth_y = sum(w * pos[1] for w, pos in zip(weights, self.position_buffer))

        return (smooth_x, smooth_y)

    def map_to_screen(self, eye_pos):
        """Map eye position to screen coordinates"""
        eye_x, eye_y = eye_pos

        # Apply dead zone
        center_x, center_y = 0.5, 0.5
        offset_x = eye_x - center_x
        offset_y = eye_y - center_y

        if abs(offset_x) < self.dead_zone:
            offset_x = 0
        if abs(offset_y) < self.dead_zone:
            offset_y = 0

        # Direct mapping with sensitivity
        screen_x = eye_x * self.screen_w * self.sensitivity
        screen_y = eye_y * self.screen_h * self.sensitivity

        # Clamp to bounds
        screen_x = max(0, min(self.screen_w - 1, screen_x))
        screen_y = max(0, min(self.screen_h - 1, screen_y))

        return (int(screen_x), int(screen_y))

    def detect_blink(self, landmarks):
        """Detect blinks for clicking"""
        try:
            left_ratio = abs(landmarks[159].y - landmarks[145].y)
            right_ratio = abs(landmarks[386].y - landmarks[374].y)
            avg_ratio = (left_ratio + right_ratio) / 2

            self.blink_buffer.append(avg_ratio)

            if len(self.blink_buffer) < 3:
                return False

            current_avg = sum(self.blink_buffer) / len(self.blink_buffer)
            return current_avg < self.blink_threshold

        except Exception as e:
            if self.debug_mode:
                self.debug_data['errors'].append({
                    'type': 'blink_detection',
                    'error': str(e),
                    'timestamp': time.time()
                })
            return False

    def detect_gestures(self, eye_pos, landmarks):
        """Detect advanced eye gestures"""
        current_time = time.time()
        gestures_detected = []

        # Eye movement gestures
        if len(self.position_buffer) >= 5:
            recent_positions = list(self.position_buffer)[-5:]

            # Detect horizontal movement
            x_movement = recent_positions[-1][0] - recent_positions[0][0]
            if abs(x_movement) > 0.1:
                if x_movement > 0 and current_time - self.last_gesture_time['eye_right'] > 0.3:
                    gestures_detected.append('eye_right')
                    self.last_gesture_time['eye_right'] = current_time
                elif x_movement < 0 and current_time - self.last_gesture_time['eye_left'] > 0.3:
                    gestures_detected.append('eye_left')
                    self.last_gesture_time['eye_left'] = current_time

            # Detect vertical movement
            y_movement = recent_positions[-1][1] - recent_positions[0][1]
            if abs(y_movement) > 0.1:
                if y_movement > 0 and current_time - self.last_gesture_time['eye_down'] > 0.3:
                    gestures_detected.append('eye_down')
                    self.last_gesture_time['eye_down'] = current_time
                elif y_movement < 0 and current_time - self.last_gesture_time['eye_up'] > 0.3:
                    gestures_detected.append('eye_up')
                    self.last_gesture_time['eye_up'] = current_time

        return gestures_detected

    def process_gestures(self, gestures):
        """Process detected gestures and perform actions"""
        for gesture in gestures:
            if gesture in self.gesture_patterns:
                action = self.gesture_patterns[gesture]['action']

                if action == 'scroll_left':
                    self.scroll_horizontal(-3)
                elif action == 'scroll_right':
                    self.scroll_horizontal(3)
                elif action == 'scroll_up':
                    self.scroll_vertical(3)
                elif action == 'scroll_down':
                    self.scroll_vertical(-3)

                self.gesture_count += 1

                if self.debug_mode:
                    self.debug_data['gestures_detected'].append({
                        'gesture': gesture,
                        'action': action,
                        'timestamp': time.time()
                    })

    def scroll_horizontal(self, amount):
        """Perform horizontal scrolling"""
        try:
            if self.mouse_backend == 'xdotool':
                if amount > 0:
                    subprocess.run(['xdotool', 'key', 'Right'], capture_output=True)
                else:
                    subprocess.run(['xdotool', 'key', 'Left'], capture_output=True)
            else:
                import pyautogui
                pyautogui.hscroll(amount)
        except Exception as e:
            logging.error(f"Horizontal scroll error: {e}")

    def scroll_vertical(self, amount):
        """Perform vertical scrolling"""
        try:
            if self.mouse_backend == 'xdotool':
                if amount > 0:
                    subprocess.run(['xdotool', 'key', 'Up'], capture_output=True)
                else:
                    subprocess.run(['xdotool', 'key', 'Down'], capture_output=True)
            else:
                import pyautogui
                pyautogui.scroll(amount)
        except Exception as e:
            logging.error(f"Vertical scroll error: {e}")

    def process_advanced_gestures(self, advanced_gestures, eye_states, head_pose):
        """Process advanced eye and head gestures"""
        current_time = time.time()

        for gesture_data in advanced_gestures:
            gesture_type = gesture_data['type']

            # Execute the gesture action
            success = self.gesture_action_processor.execute_gesture_action(gesture_data)

            if success:
                # Update statistics
                self.advanced_gesture_stats['total_advanced_gestures'] += 1

                if gesture_type == GestureType.LEFT_WINK:
                    self.advanced_gesture_stats['left_winks'] += 1
                    self.last_gesture_feedback = "👈 Left Wink → Left Click"
                elif gesture_type == GestureType.RIGHT_WINK:
                    self.advanced_gesture_stats['right_winks'] += 1
                    self.last_gesture_feedback = "👉 Right Wink → Right Click"
                elif gesture_type == GestureType.BOTH_BLINK:
                    self.advanced_gesture_stats['both_blinks'] += 1
                    if self.gesture_action_processor.is_drag_active():
                        self.last_gesture_feedback = "🖱️  Both Blink → Drag Active"
                    else:
                        self.last_gesture_feedback = "🖱️  Both Blink → Drag End"
                elif gesture_type in [GestureType.HEAD_TILT_DOWN, GestureType.HEAD_TILT_UP,
                                    GestureType.HEAD_TILT_LEFT, GestureType.HEAD_TILT_RIGHT]:
                    self.advanced_gesture_stats['head_tilts'] += 1
                    angle = gesture_data.get('angle', 0.0)
                    direction = gesture_type.value.replace('head_tilt_', '').replace('_', ' ').title()
                    self.last_gesture_feedback = f"🎯 Head {direction} ({angle:.1f}°) → Scroll"

                self.gesture_feedback_time = current_time

                # Add to debug data
                if self.debug_mode:
                    self.debug_data['gestures_detected'].append({
                        'gesture': gesture_type.value,
                        'confidence': gesture_data.get('confidence', 0.0),
                        'angle': gesture_data.get('angle', 0.0),
                        'eye_states': eye_states,
                        'head_pose': head_pose,
                        'timestamp': current_time
                    })

    def start_tracking(self):
        """Start the eye tracking system"""
        if self.is_running:
            return

        self.is_running = True
        self.tracking_thread = threading.Thread(target=self.tracking_loop, daemon=True)
        self.tracking_thread.start()

        self.status_label.config(text="Tracking active")
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')

        print("🚀 Eye tracking started!")

    def stop_tracking(self):
        """Stop the eye tracking system"""
        self.is_running = False

        if self.tracking_thread and self.tracking_thread.is_alive():
            self.tracking_thread.join(timeout=2.0)

        self.status_label.config(text="Tracking stopped")
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

        print("⏹️  Eye tracking stopped")

    def tracking_loop(self):
        """Main tracking loop with comprehensive functionality"""
        try:
            while self.is_running:
                frame_start = time.time()

                ret, frame = self.camera.read()
                if not ret:
                    continue

                # Process frame
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(rgb_frame)

                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark

                    # Log face detection
                    if self.debug_mode:
                        self.debug_data['face_detected'].append({
                            'detected': True,
                            'timestamp': time.time(),
                            'frame': self.frame_count
                        })

                    # Get iris position
                    iris_pos = self.get_iris_position(landmarks)
                    if iris_pos:
                        # Apply smoothing and mapping
                        smooth_pos = self.apply_smoothing(iris_pos)
                        screen_x, screen_y = self.map_to_screen(smooth_pos)

                        # Move cursor
                        success = self.move_mouse(screen_x, screen_y)

                        # Log eye position and mouse movement
                        if self.debug_mode:
                            self.debug_data['eye_positions'].append({
                                'eye_pos': iris_pos,
                                'screen_pos': (screen_x, screen_y),
                                'timestamp': time.time()
                            })

                            if success:
                                self.debug_data['mouse_movements'].append({
                                    'position': (screen_x, screen_y),
                                    'timestamp': time.time()
                                })

                        # Detect and process basic gestures
                        gestures = self.detect_gestures(iris_pos, landmarks)
                        if gestures:
                            self.process_gestures(gestures)

                        # Detect and process advanced gestures (SELECTIVE - only winks enabled)
                        advanced_gestures, eye_states, head_pose = self.advanced_gesture_detector.detect_gestures(
                            landmarks, frame.shape
                        )

                        if advanced_gestures:
                            # Filter to only allow wink gestures, block head tilts
                            filtered_gestures = [g for g in advanced_gestures if 'wink' in g['type'].value]
                            if filtered_gestures:
                                self.process_advanced_gestures(filtered_gestures, eye_states, head_pose)

                        # Debug output every 30 frames
                        if self.frame_count % 30 == 0:
                            print(f"👁️  Eye: ({iris_pos[0]:.3f}, {iris_pos[1]:.3f}) -> 🖱️  Screen: ({screen_x}, {screen_y})")

                    # Detect blinks for clicking
                    current_time = time.time()
                    if (self.detect_blink(landmarks) and
                        current_time - self.last_click_time > self.click_cooldown):

                        if self.click_mouse('left'):
                            self.last_click_time = current_time
                            print("👆 Click detected!")

                    # Draw landmarks
                    self.mp_drawing.draw_landmarks(
                        frame, results.multi_face_landmarks[0],
                        self.mp_face_mesh.FACEMESH_IRISES,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                    )

                else:
                    # No face detected
                    if self.debug_mode:
                        self.debug_data['face_detected'].append({
                            'detected': False,
                            'timestamp': time.time(),
                            'frame': self.frame_count
                        })

                # Update performance metrics
                frame_time = time.time() - frame_start
                if self.debug_mode:
                    self.debug_data['performance_metrics'].append({
                        'frame_time': frame_time * 1000,  # ms
                        'timestamp': time.time()
                    })

                # Update UI every 10 frames
                if self.frame_count % 10 == 0:
                    self.update_ui_metrics()

                # Save debug data periodically
                if self.debug_mode and self.frame_count % self.save_debug_interval == 0:
                    self.save_debug_data()

                # Draw advanced gesture feedback on frame
                self.draw_gesture_feedback(frame)

                # Display frame
                cv2.imshow('Enhanced Eye Tracking', frame)

                # Handle OpenCV window events
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.stop_tracking()
                    break
                elif key == ord('+'):
                    self.sensitivity = min(3.0, self.sensitivity + 0.1)
                    self.sensitivity_var.set(self.sensitivity)
                elif key == ord('-'):
                    self.sensitivity = max(0.1, self.sensitivity - 0.1)
                    self.sensitivity_var.set(self.sensitivity)

                self.frame_count += 1

                # Maintain target FPS
                target_frame_time = 1.0 / 30  # 30 FPS
                if frame_time < target_frame_time:
                    time.sleep(target_frame_time - frame_time)

        except Exception as e:
            logging.error(f"Error in tracking loop: {e}")
            logging.error(traceback.format_exc())
            if self.debug_mode:
                self.debug_data['errors'].append({
                    'type': 'tracking_loop',
                    'error': str(e),
                    'traceback': traceback.format_exc(),
                    'timestamp': time.time()
                })
        finally:
            cv2.destroyAllWindows()

    def draw_gesture_feedback(self, frame):
        """Draw gesture feedback and eye state information on frame"""
        try:
            current_time = time.time()

            # Draw gesture feedback (show for 2 seconds)
            if current_time - self.gesture_feedback_time < 2.0 and self.last_gesture_feedback:
                cv2.putText(frame, self.last_gesture_feedback, (10, frame.shape[0] - 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Draw drag mode indicator
            if hasattr(self, 'gesture_action_processor') and self.gesture_action_processor.is_drag_active():
                cv2.putText(frame, "DRAG MODE ACTIVE", (10, frame.shape[0] - 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # Draw advanced gesture statistics
            stats_text = f"Advanced Gestures: {self.advanced_gesture_stats['total_advanced_gestures']}"
            cv2.putText(frame, stats_text, (frame.shape[1] - 300, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

            # Draw individual gesture counts
            y_offset = 55
            for gesture_type, count in self.advanced_gesture_stats.items():
                if gesture_type != 'total_advanced_gestures' and count > 0:
                    text = f"{gesture_type}: {count}"
                    cv2.putText(frame, text, (frame.shape[1] - 200, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                    y_offset += 20

        except Exception as e:
            logging.error(f"Error drawing gesture feedback: {e}")

    def update_ui_metrics(self):
        """Update UI with current performance metrics"""
        try:
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0

            success_rate = (self.mouse_move_success / self.mouse_move_count * 100) if self.mouse_move_count > 0 else 0

            self.fps_label.config(text=f"FPS: {fps:.1f}")
            self.mouse_success_label.config(text=f"Mouse Success: {success_rate:.1f}%")
            self.gesture_label.config(text=f"Gestures: {self.gesture_count}")

            # Update advanced gesture metrics
            total_advanced = self.advanced_gesture_stats['total_advanced_gestures']
            self.advanced_gesture_label.config(text=f"Advanced Gestures: {total_advanced}")

            # Update gesture feedback (show for 3 seconds)
            current_time = time.time()
            if current_time - self.gesture_feedback_time < 3.0 and self.last_gesture_feedback:
                self.gesture_feedback_label.config(text=f"Last: {self.last_gesture_feedback}")
            else:
                self.gesture_feedback_label.config(text="Last Gesture: None")
        except Exception as e:
            logging.error(f"UI update error: {e}")

    def update_sensitivity(self, value):
        """Update sensitivity from UI"""
        self.sensitivity = float(value)

    def save_debug_data(self):
        """Save comprehensive debug data"""
        try:
            import json

            filename = f"eye_tracking_debug_{int(time.time())}.json"

            # Calculate statistics
            stats = {
                'total_frames': self.frame_count,
                'runtime': time.time() - self.start_time,
                'mouse_moves': self.mouse_move_count,
                'mouse_success_rate': (self.mouse_move_success / self.mouse_move_count * 100) if self.mouse_move_count > 0 else 0,
                'gestures_detected': self.gesture_count,
                'advanced_gestures': self.advanced_gesture_stats,
                'gesture_action_stats': self.gesture_action_processor.get_action_statistics(),
                'errors_count': len(self.debug_data['errors']),
                'face_detection_rate': len([x for x in self.debug_data['face_detected'] if x['detected']]) / len(self.debug_data['face_detected']) if self.debug_data['face_detected'] else 0
            }

            debug_export = {
                'stats': stats,
                'debug_data': self.debug_data,
                'settings': {
                    'sensitivity': self.sensitivity,
                    'dead_zone': self.dead_zone,
                    'screen_size': {'w': self.screen_w, 'h': self.screen_h},
                    'mouse_backend': self.mouse_backend
                }
            }

            with open(filename, 'w') as f:
                json.dump(debug_export, f, indent=2)

            print(f"📊 Debug data saved to {filename}")
            print(f"   Mouse success rate: {stats['mouse_success_rate']:.1f}%")
            print(f"   Face detection rate: {stats['face_detection_rate']:.1%}")
            print(f"   Gestures detected: {stats['gestures_detected']}")

        except Exception as e:
            logging.error(f"Error saving debug data: {e}")

    def print_controls(self):
        """Print control instructions"""
        print("\n🎮 Enhanced Controls:")
        print("- Look around to move cursor")
        print("- Blink to click (fallback)")
        print("- Look left/right quickly to scroll horizontally")
        print("- Look up/down quickly to scroll vertically")
        print("- Use UI buttons to start/stop tracking")
        print("- Press 'q' in video window to quit")
        print("- Press '+/-' to adjust sensitivity")
        print("\n👁️  Advanced Eye Gestures:")
        print("- Left eye wink (left eye closed, right open) → Left click")
        print("- Right eye wink (right eye closed, left open) → Right click")
        print("- Both eyes blink → Middle click / Toggle drag mode")
        print("\n🎯 Head Movement Gestures:")
        print("- Head tilt down (chin toward chest) → Scroll down")
        print("- Head tilt up (chin away from chest) → Scroll up")
        print("- Head tilt left → Scroll left")
        print("- Head tilt right → Scroll right")

    def cleanup(self):
        """Clean up resources"""
        self.is_running = False
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        print("✅ Cleanup completed")

    def run(self):
        """Run the main application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
            logging.error(f"Application error: {e}")
            logging.error(traceback.format_exc())
        finally:
            self.cleanup()

    def on_closing(self):
        """Handle application closing"""
        self.stop_tracking()
        self.save_debug_data()
        self.cleanup()
        self.root.destroy()

def main():
    """Main entry point"""
    try:
        app = EnhancedEyeControlledInterface()
        app.run()
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        logging.error(f"Startup error: {e}", exc_info=True)

if __name__ == "__main__":
    main()