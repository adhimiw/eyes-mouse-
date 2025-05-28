"""
YouTube-specific optimizations and gesture controls
"""

import pyautogui
import psutil
import re
from typing import Dict, Any, List, Tuple, Optional
from .base_plugin import StreamingPlugin
import logging

class YouTubePlugin(StreamingPlugin):
    def __init__(self, config_manager):
        super().__init__(config_manager)
        self.platform_name = "YouTube"
        self.window_titles = ["YouTube", "youtube.com"]
        self.url_patterns = [r".*youtube\.com.*", r".*youtu\.be.*"]
        
        # YouTube-specific state
        self.playback_speed = 1.0
        self.quality_setting = "auto"
        self.theater_mode = False
        
        # YouTube gesture zones
        self.youtube_zones = self._initialize_youtube_zones()
    
    def _initialize_youtube_zones(self) -> Dict[str, Dict[str, float]]:
        """Initialize YouTube-specific control zones"""
        screen_w, screen_h = pyautogui.size()
        
        zones = self.video_zones.copy()
        zones.update({
            "speed_control": {
                "x1": screen_w * 0.05, "y1": screen_h * 0.05,
                "x2": screen_w * 0.2, "y2": screen_h * 0.2
            },
            "quality_control": {
                "x1": screen_w * 0.8, "y1": screen_h * 0.05,
                "x2": screen_w * 0.95, "y2": screen_h * 0.2
            },
            "theater_mode": {
                "x1": screen_w * 0.7, "y1": screen_h * 0.8,
                "x2": screen_w * 0.85, "y2": screen_h * 0.95
            },
            "skip_ad": {
                "x1": screen_w * 0.85, "y1": screen_h * 0.7,
                "x2": screen_w, "y2": screen_h * 0.85
            },
            "like_button": {
                "x1": screen_w * 0.1, "y1": screen_h * 0.7,
                "x2": screen_w * 0.25, "y2": screen_h * 0.85
            },
            "subscribe_button": {
                "x1": screen_w * 0.25, "y1": screen_h * 0.7,
                "x2": screen_w * 0.4, "y2": screen_h * 0.85
            }
        })
        
        return zones
    
    def detect_platform(self) -> bool:
        """Detect if YouTube is currently active"""
        try:
            # Check for YouTube in browser windows
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] in ['chrome.exe', 'firefox.exe', 'msedge.exe', 'safari']:
                        cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                        if any(pattern in cmdline.lower() for pattern in ['youtube', 'youtu.be']):
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return False
        except Exception as e:
            logging.error(f"Error detecting YouTube: {e}")
            return False
    
    def get_platform_specific_gestures(self) -> Dict[str, Any]:
        """Get YouTube-specific gesture mappings"""
        return {
            "speed_control": {
                "gesture": "sustained_gaze",
                "zone": "speed_control",
                "duration": 2.0,
                "action": self._cycle_playback_speed
            },
            "quality_control": {
                "gesture": "sustained_gaze",
                "zone": "quality_control",
                "duration": 2.0,
                "action": self._cycle_quality
            },
            "theater_mode": {
                "gesture": "sustained_gaze",
                "zone": "theater_mode",
                "duration": 1.5,
                "action": self._toggle_theater_mode
            },
            "skip_ad": {
                "gesture": "sustained_gaze",
                "zone": "skip_ad",
                "duration": 1.0,
                "action": self._skip_ad
            },
            "like_video": {
                "gesture": "sustained_gaze",
                "zone": "like_button",
                "duration": 2.0,
                "action": self._like_video
            },
            "subscribe": {
                "gesture": "sustained_gaze",
                "zone": "subscribe_button",
                "duration": 3.0,
                "action": self._subscribe_channel
            }
        }
    
    def _process_platform_gestures(self, eye_position: Tuple[float, float], 
                                 gesture_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process YouTube-specific gestures"""
        actions = []
        screen_pos = self._eye_to_screen_coords(eye_position)
        
        # Process YouTube zones
        for zone_name, zone_coords in self.youtube_zones.items():
            if (zone_coords["x1"] <= screen_pos[0] <= zone_coords["x2"] and
                zone_coords["y1"] <= screen_pos[1] <= zone_coords["y2"]):
                
                action = self._execute_youtube_control(zone_name, screen_pos)
                if action:
                    actions.append(action)
        
        # Process YouTube-specific keyboard shortcuts
        if gesture_data.get("blink_detected"):
            shortcut_action = self._process_youtube_shortcuts(gesture_data)
            if shortcut_action:
                actions.append(shortcut_action)
        
        return actions
    
    def _execute_youtube_control(self, zone_name: str, position: Tuple[int, int]) -> Optional[Dict[str, Any]]:
        """Execute YouTube-specific control actions"""
        try:
            if zone_name == "speed_control":
                return self._cycle_playback_speed()
            elif zone_name == "quality_control":
                return self._cycle_quality()
            elif zone_name == "theater_mode":
                return self._toggle_theater_mode()
            elif zone_name == "skip_ad":
                return self._skip_ad()
            elif zone_name == "like_button":
                return self._like_video()
            elif zone_name == "subscribe_button":
                return self._subscribe_channel()
        except Exception as e:
            logging.error(f"Error executing YouTube control {zone_name}: {e}")
        
        return None
    
    def _cycle_playback_speed(self) -> Dict[str, Any]:
        """Cycle through playback speeds"""
        try:
            # YouTube speed shortcuts: Shift + . (faster), Shift + , (slower)
            speeds = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
            current_index = speeds.index(self.playback_speed) if self.playback_speed in speeds else 3
            
            # Cycle to next speed
            next_index = (current_index + 1) % len(speeds)
            self.playback_speed = speeds[next_index]
            
            # Use keyboard shortcut to change speed
            if self.playback_speed > 1.0:
                pyautogui.hotkey('shift', '.')
            else:
                pyautogui.hotkey('shift', ',')
            
            return {
                "type": "youtube_control",
                "action": "playback_speed",
                "speed": self.playback_speed
            }
        except Exception as e:
            logging.error(f"Error cycling playback speed: {e}")
            return {"type": "error", "message": str(e)}
    
    def _cycle_quality(self) -> Dict[str, Any]:
        """Cycle through video quality settings"""
        try:
            # Open settings menu and navigate to quality
            pyautogui.hotkey('shift', 'ctrl', 's')  # Settings shortcut
            
            return {
                "type": "youtube_control",
                "action": "quality_menu_opened"
            }
        except Exception as e:
            logging.error(f"Error opening quality menu: {e}")
            return {"type": "error", "message": str(e)}
    
    def _toggle_theater_mode(self) -> Dict[str, Any]:
        """Toggle theater mode"""
        try:
            pyautogui.press('t')  # Theater mode toggle
            self.theater_mode = not self.theater_mode
            
            return {
                "type": "youtube_control",
                "action": "theater_mode",
                "state": "enabled" if self.theater_mode else "disabled"
            }
        except Exception as e:
            logging.error(f"Error toggling theater mode: {e}")
            return {"type": "error", "message": str(e)}
    
    def _skip_ad(self) -> Dict[str, Any]:
        """Skip advertisement"""
        try:
            # Try clicking skip ad button (this would need more sophisticated detection)
            # For now, use Tab + Enter to navigate to skip button
            pyautogui.press('tab')
            pyautogui.press('enter')
            
            return {
                "type": "youtube_control",
                "action": "skip_ad"
            }
        except Exception as e:
            logging.error(f"Error skipping ad: {e}")
            return {"type": "error", "message": str(e)}
    
    def _like_video(self) -> Dict[str, Any]:
        """Like the current video"""
        try:
            # YouTube like shortcut
            pyautogui.hotkey('shift', 'l')
            
            return {
                "type": "youtube_control",
                "action": "like_video"
            }
        except Exception as e:
            logging.error(f"Error liking video: {e}")
            return {"type": "error", "message": str(e)}
    
    def _subscribe_channel(self) -> Dict[str, Any]:
        """Subscribe to the channel"""
        try:
            # YouTube subscribe shortcut
            pyautogui.hotkey('shift', 's')
            
            return {
                "type": "youtube_control",
                "action": "subscribe_channel"
            }
        except Exception as e:
            logging.error(f"Error subscribing to channel: {e}")
            return {"type": "error", "message": str(e)}
    
    def _process_youtube_shortcuts(self, gesture_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process YouTube keyboard shortcuts based on blink patterns"""
        # Implement blink pattern recognition for shortcuts
        # This is a placeholder for more sophisticated pattern recognition
        
        try:
            # Example: Long blink for skip forward
            if gesture_data.get("long_blink"):
                pyautogui.press('l')  # Skip forward 10 seconds
                return {
                    "type": "youtube_control",
                    "action": "skip_forward",
                    "trigger": "long_blink"
                }
        except Exception as e:
            logging.error(f"Error processing YouTube shortcuts: {e}")
        
        return None
    
    def get_video_recommendations(self, viewing_history: List[Dict[str, Any]]) -> List[str]:
        """Get video recommendations based on eye tracking patterns"""
        # Analyze viewing patterns and suggest videos
        # This is a placeholder for advanced analytics
        recommendations = []
        
        # Example: If user watches tech videos frequently
        if any("tech" in video.get("title", "").lower() for video in viewing_history):
            recommendations.append("Latest tech reviews")
        
        return recommendations
