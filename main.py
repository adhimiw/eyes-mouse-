"""
Main Application for Eye-Controlled Computer Interface
Comprehensive eye tracking system with streaming platform optimizations
"""

import sys
import threading
import time
import logging
import traceback
from typing import Dict, Any, List
import tkinter as tk
from tkinter import messagebox
import pyautogui

# Import our modules
from config_manager import ConfigManager
try:
    from eye_tracker import EyeTracker
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    from eye_tracker_opencv import EyeTrackerOpenCV as EyeTracker
    MEDIAPIPE_AVAILABLE = False
    logging.warning("MediaPipe not available, using OpenCV fallback")

from gesture_controller import GestureController
from ui_overlay import EyeTrackingOverlay
from performance_monitor import PerformanceMonitor
from streaming_plugins.netflix_plugin import NetflixPlugin
from streaming_plugins.youtube_plugin import YouTubePlugin
from streaming_plugins.base_plugin import StreamingPlugin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eye_tracking.log'),
        logging.StreamHandler()
    ]
)

class EyeControlledInterface:
    def __init__(self):
        """Initialize the eye-controlled interface system"""
        try:
            # Initialize configuration
            self.config = ConfigManager()

            # Optimize PyAutoGUI for performance
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0.001  # Minimal pause for maximum responsiveness
            logging.info("PyAutoGUI optimized for performance")

            # Initialize core components
            self.eye_tracker = EyeTracker(self.config)
            tracker_type = "MediaPipe" if MEDIAPIPE_AVAILABLE else "OpenCV"
            logging.info(f"Using {tracker_type} eye tracker")

            self.gesture_controller = GestureController(self.config)
            self.performance_monitor = PerformanceMonitor(self.config)

            # Initialize streaming plugins
            self.streaming_plugins = []
            self.load_streaming_plugins()

            # Initialize UI
            self.ui = EyeTrackingOverlay(self.config, self.eye_tracker, self.gesture_controller)
            self.ui.set_callbacks(
                on_start=self.start_tracking,
                on_stop=self.stop_tracking,
                on_calibrate=self.start_calibration
            )

            # Tracking state
            self.is_running = False
            self.tracking_thread = None
            self.calibration_thread = None

            # Performance monitoring
            self.frame_count = 0
            self.start_time = time.time()

            logging.info("Eye-controlled interface initialized successfully")

        except Exception as e:
            logging.error(f"Failed to initialize application: {e}")
            messagebox.showerror("Initialization Error", f"Failed to start application:\n{str(e)}")
            sys.exit(1)

    def load_streaming_plugins(self):
        """Load and initialize streaming platform plugins"""
        try:
            # Load Netflix plugin
            netflix_plugin = NetflixPlugin(self.config)
            self.streaming_plugins.append(netflix_plugin)

            # Load YouTube plugin
            youtube_plugin = YouTubePlugin(self.config)
            self.streaming_plugins.append(youtube_plugin)

            logging.info(f"Loaded {len(self.streaming_plugins)} streaming plugins")

        except Exception as e:
            logging.error(f"Error loading streaming plugins: {e}")

    def start_tracking(self):
        """Start the eye tracking system"""
        if self.is_running:
            return

        try:
            # Initialize camera
            if not self.eye_tracker.initialize_camera():
                messagebox.showerror("Camera Error", "Failed to initialize camera")
                return

            self.is_running = True

            # Start performance monitoring
            self.performance_monitor.start_monitoring()

            # Start tracking thread
            self.tracking_thread = threading.Thread(target=self.tracking_loop, daemon=True)
            self.tracking_thread.start()

            # Update UI status
            self.ui.connection_label.config(text="Camera: Connected")

            logging.info("Eye tracking started")

        except Exception as e:
            logging.error(f"Error starting tracking: {e}")
            messagebox.showerror("Tracking Error", f"Failed to start tracking:\n{str(e)}")
            self.is_running = False

    def stop_tracking(self):
        """Stop the eye tracking system"""
        if not self.is_running:
            return

        self.is_running = False

        # Wait for tracking thread to finish
        if self.tracking_thread and self.tracking_thread.is_alive():
            self.tracking_thread.join(timeout=2.0)

        # Stop performance monitoring
        self.performance_monitor.stop_monitoring()

        # Cleanup resources
        self.eye_tracker.cleanup()

        # Update UI status
        self.ui.connection_label.config(text="Camera: Disconnected")

        logging.info("Eye tracking stopped")

    def tracking_loop(self):
        """Main tracking loop - runs in separate thread"""
        try:
            while self.is_running:
                start_time = time.time()

                # Process frame
                frame, tracking_data = self.eye_tracker.process_frame()

                if frame is not None:
                    # Update video display
                    self.ui.update_video_display(frame)

                    # Update tracking status
                    self.ui.update_tracking_status(tracking_data)

                    # Process gestures if eye position is available
                    if tracking_data.get("eye_position"):
                        gesture_actions = self.gesture_controller.process_tracking_data(tracking_data)

                        # Process streaming platform gestures
                        streaming_actions = self.process_streaming_platforms(tracking_data)
                        gesture_actions.extend(streaming_actions)

                        # Update UI with gesture events
                        for action in gesture_actions:
                            self.ui.add_gesture_event(action)

                    # Performance monitoring
                    self.frame_count += 1
                    processing_time = time.time() - start_time

                    # Update performance monitor
                    fps = 1.0 / processing_time if processing_time > 0 else 0
                    self.performance_monitor.update_fps(fps)
                    self.performance_monitor.update_latency(processing_time * 1000)  # Convert to ms

                    # Maintain target frame rate
                    target_fps = self.config.get_setting("tracking", "frame_rate", 30)
                    target_frame_time = 1.0 / target_fps

                    if processing_time < target_frame_time:
                        time.sleep(target_frame_time - processing_time)

                else:
                    # No frame available, short delay
                    time.sleep(0.01)

        except Exception as e:
            logging.error(f"Error in tracking loop: {e}")
            logging.error(traceback.format_exc())
            self.is_running = False

    def process_streaming_platforms(self, tracking_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process streaming platform specific gestures"""
        actions = []

        try:
            eye_position = tracking_data.get("eye_position")
            if not eye_position:
                return actions

            # Check each streaming plugin
            for plugin in self.streaming_plugins:
                if plugin.is_platform_active():
                    plugin_actions = plugin.process_streaming_gestures(eye_position, tracking_data)
                    actions.extend(plugin_actions)

                    # Only process one active platform at a time
                    break

        except Exception as e:
            logging.error(f"Error processing streaming platforms: {e}")

        return actions

    def start_calibration(self):
        """Start the calibration process"""
        if self.calibration_thread and self.calibration_thread.is_alive():
            return

        self.calibration_thread = threading.Thread(target=self.calibration_loop, daemon=True)
        self.calibration_thread.start()

    def calibration_loop(self):
        """Calibration process loop"""
        try:
            # Get calibration points
            calibration_points = self.eye_tracker.start_calibration(num_points=9)

            for i, point in enumerate(calibration_points):
                if not self.ui.is_calibrating:
                    break

                # Update progress
                progress = (i / len(calibration_points)) * 100
                self.ui.cal_progress['value'] = progress

                # Show calibration point (this would need a full-screen calibration window)
                # For now, we'll simulate the calibration process
                logging.info(f"Calibrating point {i+1}/{len(calibration_points)}: {point}")

                # Collect eye data for this point (simulated)
                eye_data = []
                for _ in range(30):  # Collect 30 samples
                    if not self.ui.is_calibrating:
                        break

                    _, tracking_data = self.eye_tracker.process_frame()
                    if tracking_data.get("eye_position"):
                        eye_data.append(tracking_data["eye_position"])

                    time.sleep(0.1)  # 100ms between samples

                # Add calibration point
                if eye_data:
                    self.eye_tracker.add_calibration_point(point, eye_data)

            # Finish calibration
            if self.ui.is_calibrating:
                success = self.eye_tracker.finish_calibration()
                if success:
                    self.ui.cal_status_label.config(text="Calibrated successfully")
                    self.ui.cal_progress['value'] = 100
                    logging.info("Calibration completed successfully")
                else:
                    self.ui.cal_status_label.config(text="Calibration failed")
                    logging.error("Calibration failed")

            self.ui.is_calibrating = False

        except Exception as e:
            logging.error(f"Error during calibration: {e}")
            self.ui.cal_status_label.config(text="Calibration error")
            self.ui.is_calibrating = False

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        stats = {
            "uptime": elapsed_time,
            "frames_processed": self.frame_count,
            "average_fps": self.frame_count / elapsed_time if elapsed_time > 0 else 0,
            "is_running": self.is_running,
            "active_plugins": [p.platform_name for p in self.streaming_plugins if p.is_platform_active()]
        }

        # Add eye tracker stats
        if hasattr(self.eye_tracker, 'get_performance_stats'):
            stats.update(self.eye_tracker.get_performance_stats())

        return stats

    def emergency_shutdown(self):
        """Emergency shutdown of all systems"""
        logging.warning("Emergency shutdown initiated")

        # Stop tracking
        self.stop_tracking()

        # Disable gesture controller
        self.gesture_controller.emergency_disable()

        # Deactivate all plugins
        for plugin in self.streaming_plugins:
            plugin.deactivate()

        logging.info("Emergency shutdown completed")

    def run(self):
        """Run the main application"""
        try:
            # Set up emergency shutdown handler
            def on_closing():
                if self.is_running:
                    self.stop_tracking()
                self.ui.root.destroy()

            self.ui.root.protocol("WM_DELETE_WINDOW", on_closing)

            # Start the UI
            logging.info("Starting eye-controlled interface application")
            self.ui.run()

        except KeyboardInterrupt:
            logging.info("Application interrupted by user")
        except Exception as e:
            logging.error(f"Unexpected error in main application: {e}")
            logging.error(traceback.format_exc())
        finally:
            self.emergency_shutdown()

def main():
    """Main entry point"""
    try:
        # Create and run the application
        app = EyeControlledInterface()
        app.run()

    except Exception as e:
        logging.error(f"Fatal error: {e}")
        logging.error(traceback.format_exc())

        # Show error dialog if possible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Fatal Error", f"Application crashed:\n{str(e)}")
        except:
            pass

        sys.exit(1)

if __name__ == "__main__":
    main()
