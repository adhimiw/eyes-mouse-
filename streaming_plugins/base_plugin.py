"""
Base Plugin for Streaming Platform Optimizations
Provides common functionality for all streaming platform plugins
"""

import time
import pyautogui
import psutil
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import logging

class StreamingPlugin(ABC):
    def __init__(self, config_manager):
        self.config = config_manager
        self.is_active = False
        self.last_activity_time = time.time()
        self.auto_pause_timeout = self.config.get_setting("streaming", "auto_pause_timeout", 10.0)
        
        # Platform-specific settings
        self.platform_name = ""
        self.window_titles = []
        self.url_patterns = []
        
        # Media control state
        self.is_playing = False
        self.is_fullscreen = False
        self.volume_level = 50
        
        # Gesture zones specific to video players
        self.video_zones = self._initialize_video_zones()
        
    def _initialize_video_zones(self) -> Dict[str, Dict[str, float]]:
        """Initialize video player control zones"""
        screen_w, screen_h = pyautogui.size()
        
        return {
            "play_pause_center": {
                "x1": screen_w * 0.4, "y1": screen_h * 0.4,
                "x2": screen_w * 0.6, "y2": screen_h * 0.6
            },
            "volume_left": {
                "x1": 0, "y1": screen_h * 0.3,
                "x2": 100, "y2": screen_h * 0.7
            },
            "volume_right": {
                "x1": screen_w - 100, "y1": screen_h * 0.3,
                "x2": screen_w, "y2": screen_h * 0.7
            },
            "seek_bar": {
                "x1": screen_w * 0.1, "y1": screen_h * 0.85,
                "x2": screen_w * 0.9, "y2": screen_h * 0.95
            },
            "fullscreen_toggle": {
                "x1": screen_w * 0.45, "y1": 0,
                "x2": screen_w * 0.55, "y2": 50
            }
        }
    
    @abstractmethod
    def detect_platform(self) -> bool:
        """Detect if the platform is currently active"""
        pass
    
    @abstractmethod
    def get_platform_specific_gestures(self) -> Dict[str, Any]:
        """Get platform-specific gesture mappings"""
        pass
    
    def is_platform_active(self) -> bool:
        """Check if this streaming platform is currently active"""
        return self.detect_platform()
    
    def process_streaming_gestures(self, eye_position: Tuple[float, float], 
                                 gesture_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process streaming-specific gestures"""
        if not self.is_platform_active():
            return []
        
        actions = []
        screen_pos = self._eye_to_screen_coords(eye_position)
        current_time = time.time()
        
        # Update activity time
        self.last_activity_time = current_time
        
        # Process video control zones
        zone_action = self._process_video_zones(screen_pos, current_time)
        if zone_action:
            actions.append(zone_action)
        
        # Process auto-pause functionality
        auto_pause_action = self._process_auto_pause(current_time)
        if auto_pause_action:
            actions.append(auto_pause_action)
        
        # Process platform-specific gestures
        platform_actions = self._process_platform_gestures(eye_position, gesture_data)
        actions.extend(platform_actions)
        
        return actions
    
    def _eye_to_screen_coords(self, eye_position: Tuple[float, float]) -> Tuple[int, int]:
        """Convert eye position to screen coordinates"""
        screen_w, screen_h = pyautogui.size()
        x = int(eye_position[0] * screen_w)
        y = int(eye_position[1] * screen_h)
        return (x, y)
    
    def _process_video_zones(self, position: Tuple[int, int], current_time: float) -> Optional[Dict[str, Any]]:
        """Process video player control zones"""
        for zone_name, zone_coords in self.video_zones.items():
            if (zone_coords["x1"] <= position[0] <= zone_coords["x2"] and
                zone_coords["y1"] <= position[1] <= zone_coords["y2"]):
                
                # Sustained gaze required for video controls
                sustained_time = 2.0
                
                if hasattr(self, 'zone_gaze_start'):
                    if (self.zone_gaze_start.get(zone_name) and 
                        current_time - self.zone_gaze_start[zone_name] >= sustained_time):
                        
                        action = self._execute_video_control(zone_name, position)
                        if action:
                            # Reset gaze timer
                            self.zone_gaze_start[zone_name] = None
                            return action
                else:
                    self.zone_gaze_start = {}
                
                # Start gaze timer
                if not self.zone_gaze_start.get(zone_name):
                    self.zone_gaze_start[zone_name] = current_time
        
        return None
    
    def _execute_video_control(self, zone_name: str, position: Tuple[int, int]) -> Optional[Dict[str, Any]]:
        """Execute video control action based on zone"""
        try:
            if zone_name == "play_pause_center":
                pyautogui.press('space')
                self.is_playing = not self.is_playing
                return {
                    "type": "video_control",
                    "action": "play_pause",
                    "state": "playing" if self.is_playing else "paused"
                }
            
            elif zone_name == "volume_left":
                pyautogui.press('volumedown')
                self.volume_level = max(0, self.volume_level - 10)
                return {
                    "type": "video_control",
                    "action": "volume_down",
                    "level": self.volume_level
                }
            
            elif zone_name == "volume_right":
                pyautogui.press('volumeup')
                self.volume_level = min(100, self.volume_level + 10)
                return {
                    "type": "video_control",
                    "action": "volume_up",
                    "level": self.volume_level
                }
            
            elif zone_name == "seek_bar":
                # Calculate seek position based on horizontal position
                seek_percentage = (position[0] - self.video_zones["seek_bar"]["x1"]) / \
                                (self.video_zones["seek_bar"]["x2"] - self.video_zones["seek_bar"]["x1"])
                
                # Use arrow keys for seeking (platform-specific implementation needed)
                if seek_percentage < 0.5:
                    pyautogui.press('left')
                    return {"type": "video_control", "action": "seek_backward"}
                else:
                    pyautogui.press('right')
                    return {"type": "video_control", "action": "seek_forward"}
            
            elif zone_name == "fullscreen_toggle":
                pyautogui.press('f')
                self.is_fullscreen = not self.is_fullscreen
                return {
                    "type": "video_control",
                    "action": "fullscreen_toggle",
                    "state": "fullscreen" if self.is_fullscreen else "windowed"
                }
        
        except Exception as e:
            logging.error(f"Error executing video control {zone_name}: {e}")
        
        return None
    
    def _process_auto_pause(self, current_time: float) -> Optional[Dict[str, Any]]:
        """Process auto-pause when user looks away"""
        if current_time - self.last_activity_time > self.auto_pause_timeout:
            if self.is_playing:
                pyautogui.press('space')
                self.is_playing = False
                return {
                    "type": "auto_control",
                    "action": "auto_pause",
                    "reason": "user_away"
                }
        return None
    
    def _process_platform_gestures(self, eye_position: Tuple[float, float], 
                                 gesture_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process platform-specific gestures - to be implemented by subclasses"""
        return []
    
    def get_window_titles(self) -> List[str]:
        """Get list of window titles for this platform"""
        return self.window_titles
    
    def activate(self):
        """Activate this plugin"""
        self.is_active = True
        logging.info(f"{self.platform_name} plugin activated")
    
    def deactivate(self):
        """Deactivate this plugin"""
        self.is_active = False
        logging.info(f"{self.platform_name} plugin deactivated")
