"""
UI Overlay for Eye Tracking Visualization and Control
Provides real-time feedback and settings interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
import threading
import time
from typing import Dict, Any, Optional, Callable
import logging

try:
    from PIL import Image, ImageTk
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logging.warning("PIL/ImageTk not available, video display disabled")

class EyeTrackingOverlay:
    def __init__(self, config_manager, eye_tracker, gesture_controller):
        self.config = config_manager
        self.eye_tracker = eye_tracker
        self.gesture_controller = gesture_controller

        # Main window
        self.root = tk.Tk()
        self.root.title("Eye-Controlled Interface")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Overlay window for real-time feedback
        self.overlay_window = None
        self.show_overlay = self.config.get_setting("display", "show_overlay", True)

        # UI state
        self.is_running = False
        self.is_calibrating = False
        self.calibration_step = 0
        self.calibration_points = []

        # Performance metrics
        self.fps_counter = 0
        self.last_fps_time = time.time()
        self.current_fps = 0

        # Create UI components
        self.create_main_interface()
        self.create_overlay_window()

        # Callbacks
        self.on_start_callback = None
        self.on_stop_callback = None
        self.on_calibrate_callback = None

    def create_main_interface(self):
        """Create the main control interface"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control tab
        self.create_control_tab(notebook)

        # Settings tab
        self.create_settings_tab(notebook)

        # Calibration tab
        self.create_calibration_tab(notebook)

        # Performance tab
        self.create_performance_tab(notebook)

        # Status bar
        self.create_status_bar()

    def create_control_tab(self, parent):
        """Create the main control tab"""
        control_frame = ttk.Frame(parent)
        parent.add(control_frame, text="Control")

        # Main controls
        controls_frame = ttk.LabelFrame(control_frame, text="Eye Tracking Control")
        controls_frame.pack(fill=tk.X, padx=10, pady=10)

        # Start/Stop buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Tracking",
                                     command=self.start_tracking, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop Tracking",
                                    command=self.stop_tracking, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.calibrate_button = ttk.Button(button_frame, text="Calibrate",
                                         command=self.start_calibration)
        self.calibrate_button.pack(side=tk.LEFT, padx=5)

        # Emergency stop
        emergency_frame = ttk.Frame(controls_frame)
        emergency_frame.pack(pady=10)

        self.emergency_button = ttk.Button(emergency_frame, text="EMERGENCY STOP",
                                         command=self.emergency_stop,
                                         style="Emergency.TButton")
        self.emergency_button.pack()

        # Status indicators
        status_frame = ttk.LabelFrame(control_frame, text="Status")
        status_frame.pack(fill=tk.X, padx=10, pady=10)

        # Tracking quality indicator
        quality_frame = ttk.Frame(status_frame)
        quality_frame.pack(fill=tk.X, pady=5)

        ttk.Label(quality_frame, text="Tracking Quality:").pack(side=tk.LEFT)
        self.quality_progress = ttk.Progressbar(quality_frame, length=200, mode='determinate')
        self.quality_progress.pack(side=tk.LEFT, padx=10)
        self.quality_label = ttk.Label(quality_frame, text="0%")
        self.quality_label.pack(side=tk.LEFT)

        # FPS indicator
        fps_frame = ttk.Frame(status_frame)
        fps_frame.pack(fill=tk.X, pady=5)

        ttk.Label(fps_frame, text="FPS:").pack(side=tk.LEFT)
        self.fps_label = ttk.Label(fps_frame, text="0")
        self.fps_label.pack(side=tk.LEFT, padx=10)

        # Active gestures
        gesture_frame = ttk.LabelFrame(control_frame, text="Active Gestures")
        gesture_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.gesture_listbox = tk.Listbox(gesture_frame, height=6)
        self.gesture_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(gesture_frame, orient=tk.VERTICAL, command=self.gesture_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.gesture_listbox.config(yscrollcommand=scrollbar.set)

    def create_settings_tab(self, parent):
        """Create the settings configuration tab"""
        settings_frame = ttk.Frame(parent)
        parent.add(settings_frame, text="Settings")

        # Create scrollable frame
        canvas = tk.Canvas(settings_frame)
        scrollbar = ttk.Scrollbar(settings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Tracking settings
        tracking_frame = ttk.LabelFrame(scrollable_frame, text="Tracking Settings")
        tracking_frame.pack(fill=tk.X, padx=10, pady=5)

        # Sensitivity
        sens_frame = ttk.Frame(tracking_frame)
        sens_frame.pack(fill=tk.X, pady=2)
        ttk.Label(sens_frame, text="Sensitivity:").pack(side=tk.LEFT)
        self.sensitivity_var = tk.DoubleVar(value=self.config.get_setting("tracking", "sensitivity", 1.0))
        sensitivity_scale = ttk.Scale(sens_frame, from_=0.1, to=2.0, variable=self.sensitivity_var,
                                    orient=tk.HORIZONTAL, command=self.update_sensitivity)
        sensitivity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.sensitivity_label = ttk.Label(sens_frame, text=f"{self.sensitivity_var.get():.1f}")
        self.sensitivity_label.pack(side=tk.LEFT)

        # Smoothing
        smooth_frame = ttk.Frame(tracking_frame)
        smooth_frame.pack(fill=tk.X, pady=2)
        ttk.Label(smooth_frame, text="Smoothing:").pack(side=tk.LEFT)
        self.smoothing_var = tk.DoubleVar(value=self.config.get_setting("tracking", "smoothing", 0.7))
        smoothing_scale = ttk.Scale(smooth_frame, from_=0.0, to=1.0, variable=self.smoothing_var,
                                  orient=tk.HORIZONTAL, command=self.update_smoothing)
        smoothing_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.smoothing_label = ttk.Label(smooth_frame, text=f"{self.smoothing_var.get():.1f}")
        self.smoothing_label.pack(side=tk.LEFT)

        # Gesture settings
        gesture_frame = ttk.LabelFrame(scrollable_frame, text="Gesture Settings")
        gesture_frame.pack(fill=tk.X, padx=10, pady=5)

        # Blink threshold
        blink_frame = ttk.Frame(gesture_frame)
        blink_frame.pack(fill=tk.X, pady=2)
        ttk.Label(blink_frame, text="Blink Threshold:").pack(side=tk.LEFT)
        self.blink_var = tk.DoubleVar(value=self.config.get_setting("gestures", "blink_threshold", 0.004))
        blink_scale = ttk.Scale(blink_frame, from_=0.001, to=0.01, variable=self.blink_var,
                              orient=tk.HORIZONTAL, command=self.update_blink_threshold)
        blink_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.blink_label = ttk.Label(blink_frame, text=f"{self.blink_var.get():.3f}")
        self.blink_label.pack(side=tk.LEFT)

        # Dwell time
        dwell_frame = ttk.Frame(gesture_frame)
        dwell_frame.pack(fill=tk.X, pady=2)
        ttk.Label(dwell_frame, text="Dwell Time (s):").pack(side=tk.LEFT)
        self.dwell_var = tk.DoubleVar(value=self.config.get_setting("gestures", "dwell_time", 1.5))
        dwell_scale = ttk.Scale(dwell_frame, from_=0.5, to=3.0, variable=self.dwell_var,
                              orient=tk.HORIZONTAL, command=self.update_dwell_time)
        dwell_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.dwell_label = ttk.Label(dwell_frame, text=f"{self.dwell_var.get():.1f}")
        self.dwell_label.pack(side=tk.LEFT)

        # Display settings
        display_frame = ttk.LabelFrame(scrollable_frame, text="Display Settings")
        display_frame.pack(fill=tk.X, padx=10, pady=5)

        self.overlay_var = tk.BooleanVar(value=self.config.get_setting("display", "show_overlay", True))
        overlay_check = ttk.Checkbutton(display_frame, text="Show Overlay",
                                      variable=self.overlay_var, command=self.toggle_overlay)
        overlay_check.pack(anchor=tk.W, pady=2)

        self.feedback_var = tk.BooleanVar(value=self.config.get_setting("display", "visual_feedback", True))
        feedback_check = ttk.Checkbutton(display_frame, text="Visual Feedback",
                                       variable=self.feedback_var, command=self.toggle_feedback)
        feedback_check.pack(anchor=tk.W, pady=2)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_calibration_tab(self, parent):
        """Create the calibration tab"""
        calibration_frame = ttk.Frame(parent)
        parent.add(calibration_frame, text="Calibration")

        # Calibration instructions
        instructions = ttk.LabelFrame(calibration_frame, text="Instructions")
        instructions.pack(fill=tk.X, padx=10, pady=10)

        instruction_text = """
        1. Click 'Start Calibration' to begin
        2. Look at each calibration point for 3 seconds
        3. Keep your head still during calibration
        4. Ensure good lighting on your face
        5. Complete all calibration points
        """

        ttk.Label(instructions, text=instruction_text, justify=tk.LEFT).pack(padx=10, pady=10)

        # Calibration controls
        cal_controls = ttk.LabelFrame(calibration_frame, text="Calibration Control")
        cal_controls.pack(fill=tk.X, padx=10, pady=10)

        cal_button_frame = ttk.Frame(cal_controls)
        cal_button_frame.pack(pady=10)

        self.cal_start_button = ttk.Button(cal_button_frame, text="Start Calibration",
                                         command=self.start_calibration)
        self.cal_start_button.pack(side=tk.LEFT, padx=5)

        self.cal_reset_button = ttk.Button(cal_button_frame, text="Reset Calibration",
                                         command=self.reset_calibration)
        self.cal_reset_button.pack(side=tk.LEFT, padx=5)

        # Calibration progress
        progress_frame = ttk.Frame(cal_controls)
        progress_frame.pack(fill=tk.X, pady=10)

        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT)
        self.cal_progress = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        self.cal_progress.pack(side=tk.LEFT, padx=10)

        # Calibration status
        self.cal_status_label = ttk.Label(cal_controls, text="Not calibrated")
        self.cal_status_label.pack(pady=5)

    def create_performance_tab(self, parent):
        """Create the performance monitoring tab"""
        performance_frame = ttk.Frame(parent)
        parent.add(performance_frame, text="Performance")

        # Performance metrics
        metrics_frame = ttk.LabelFrame(performance_frame, text="Performance Metrics")
        metrics_frame.pack(fill=tk.X, padx=10, pady=10)

        # Create metrics display
        self.metrics_text = tk.Text(metrics_frame, height=15, width=60)
        self.metrics_text.pack(padx=10, pady=10)

        # Refresh button
        refresh_button = ttk.Button(metrics_frame, text="Refresh", command=self.update_performance_metrics)
        refresh_button.pack(pady=5)

    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Connection status
        self.connection_label = ttk.Label(self.status_bar, text="Camera: Disconnected")
        self.connection_label.pack(side=tk.RIGHT, padx=5)

    def create_overlay_window(self):
        """Create the overlay window for real-time feedback"""
        if not self.show_overlay:
            return

        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.title("Eye Tracking Overlay")
        self.overlay_window.geometry("400x300")
        self.overlay_window.attributes("-topmost", True)
        self.overlay_window.attributes("-alpha", 0.8)

        if PILLOW_AVAILABLE:
            # Video display
            self.video_label = ttk.Label(self.overlay_window)
            self.video_label.pack(fill=tk.BOTH, expand=True)
        else:
            # Text-based status display when video is not available
            status_frame = ttk.Frame(self.overlay_window)
            status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            ttk.Label(status_frame, text="Eye Tracking Status", font=("Arial", 14, "bold")).pack(pady=10)

            self.overlay_status_label = ttk.Label(status_frame, text="Initializing...", font=("Arial", 12))
            self.overlay_status_label.pack(pady=5)

            self.overlay_quality_label = ttk.Label(status_frame, text="Quality: 0%", font=("Arial", 10))
            self.overlay_quality_label.pack(pady=5)

    def update_video_display(self, frame: np.ndarray):
        """Update the video display with current frame"""
        if not self.overlay_window or not self.show_overlay or not PILLOW_AVAILABLE:
            return

        try:
            # Resize frame for display
            display_frame = cv2.resize(frame, (400, 300))

            # Convert to RGB
            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

            # Convert to PIL Image
            pil_image = Image.fromarray(rgb_frame)

            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)

            # Update label
            self.video_label.configure(image=photo)
            self.video_label.image = photo  # Keep a reference

        except Exception as e:
            logging.error(f"Error updating video display: {e}")

    def update_tracking_status(self, tracking_data: Dict[str, Any]):
        """Update tracking status indicators"""
        # Update quality indicator
        quality = tracking_data.get("tracking_quality", 0.0)
        self.quality_progress['value'] = quality * 100
        self.quality_label.config(text=f"{quality*100:.0f}%")

        # Update FPS
        self.fps_counter += 1
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_label.config(text=str(self.current_fps))
            self.fps_counter = 0
            self.last_fps_time = current_time

        # Update text-based overlay if video is not available
        if not PILLOW_AVAILABLE and hasattr(self, 'overlay_status_label') and hasattr(self, 'overlay_quality_label'):
            try:
                eye_pos = tracking_data.get("eye_position")
                if eye_pos:
                    self.overlay_status_label.config(text=f"Tracking: Active\nPosition: ({eye_pos[0]:.2f}, {eye_pos[1]:.2f})")
                else:
                    self.overlay_status_label.config(text="Tracking: No eyes detected")

                self.overlay_quality_label.config(text=f"Quality: {quality*100:.0f}% | FPS: {self.current_fps}")
            except:
                pass

    def add_gesture_event(self, gesture_info: Dict[str, Any]):
        """Add gesture event to the display"""
        timestamp = time.strftime("%H:%M:%S")
        gesture_text = f"[{timestamp}] {gesture_info.get('action', 'Unknown')}"

        self.gesture_listbox.insert(0, gesture_text)

        # Keep only last 50 entries
        if self.gesture_listbox.size() > 50:
            self.gesture_listbox.delete(50, tk.END)

    # Event handlers
    def start_tracking(self):
        """Start eye tracking"""
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Tracking active")

        if self.on_start_callback:
            self.on_start_callback()

    def stop_tracking(self):
        """Stop eye tracking"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Tracking stopped")

        if self.on_stop_callback:
            self.on_stop_callback()

    def emergency_stop(self):
        """Emergency stop all tracking"""
        self.stop_tracking()
        self.gesture_controller.emergency_disable()
        messagebox.showwarning("Emergency Stop", "Eye tracking has been emergency stopped!")

    def start_calibration(self):
        """Start calibration process"""
        self.is_calibrating = True
        self.calibration_step = 0
        self.cal_progress['value'] = 0
        self.cal_status_label.config(text="Calibrating...")

        if self.on_calibrate_callback:
            self.on_calibrate_callback()

    def reset_calibration(self):
        """Reset calibration"""
        self.is_calibrating = False
        self.calibration_step = 0
        self.cal_progress['value'] = 0
        self.cal_status_label.config(text="Not calibrated")

    def update_sensitivity(self, value):
        """Update sensitivity setting"""
        val = float(value)
        self.sensitivity_label.config(text=f"{val:.1f}")
        self.config.set_setting("tracking", "sensitivity", val)

    def update_smoothing(self, value):
        """Update smoothing setting"""
        val = float(value)
        self.smoothing_label.config(text=f"{val:.1f}")
        self.config.set_setting("tracking", "smoothing", val)

    def update_blink_threshold(self, value):
        """Update blink threshold setting"""
        val = float(value)
        self.blink_label.config(text=f"{val:.3f}")
        self.config.set_setting("gestures", "blink_threshold", val)

    def update_dwell_time(self, value):
        """Update dwell time setting"""
        val = float(value)
        self.dwell_label.config(text=f"{val:.1f}")
        self.config.set_setting("gestures", "dwell_time", val)

    def toggle_overlay(self):
        """Toggle overlay display"""
        self.show_overlay = self.overlay_var.get()
        self.config.set_setting("display", "show_overlay", self.show_overlay)

        if self.show_overlay and not self.overlay_window:
            self.create_overlay_window()
        elif not self.show_overlay and self.overlay_window:
            self.overlay_window.destroy()
            self.overlay_window = None

    def toggle_feedback(self):
        """Toggle visual feedback"""
        feedback = self.feedback_var.get()
        self.config.set_setting("display", "visual_feedback", feedback)

    def update_performance_metrics(self):
        """Update performance metrics display"""
        if hasattr(self.eye_tracker, 'get_performance_stats'):
            stats = self.eye_tracker.get_performance_stats()

            metrics_text = "Performance Metrics:\n\n"
            metrics_text += f"FPS: {stats.get('fps', 0):.1f}\n"
            metrics_text += f"Processing Time: {stats.get('avg_processing_time', 0)*1000:.1f}ms\n"
            metrics_text += f"Tracking Quality: {stats.get('tracking_quality', 0)*100:.1f}%\n"

            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(1.0, metrics_text)

    def set_callbacks(self, on_start: Callable = None, on_stop: Callable = None,
                     on_calibrate: Callable = None):
        """Set callback functions"""
        self.on_start_callback = on_start
        self.on_stop_callback = on_stop
        self.on_calibrate_callback = on_calibrate

    def run(self):
        """Run the UI main loop"""
        self.root.mainloop()

    def on_closing(self):
        """Handle window closing"""
        if self.is_running:
            self.stop_tracking()

        if self.overlay_window:
            self.overlay_window.destroy()

        self.root.destroy()
