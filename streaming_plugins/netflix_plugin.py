"""
Netflix-specific optimizations and gesture controls
"""

import pyautogui
import psutil
import re
from typing import Dict, Any, List, Tuple, Optional
from .base_plugin import StreamingPlugin
import logging

class NetflixPlugin(StreamingPlugin):
    def __init__(self, config_manager):
        super().__init__(config_manager)
        self.platform_name = "Netflix"
        self.window_titles = ["Netflix", "netflix.com"]
        self.url_patterns = [r".*netflix\.com.*", r".*netflix\..*"]
        
        # Netflix-specific controls
        self.subtitle_enabled = False
        self.playback_speed = 1.0
        
        # Netflix gesture zones
        self.netflix_zones = self._initialize_netflix_zones()
    
    def _initialize_netflix_zones(self) -> Dict[str, Dict[str, float]]:
        """Initialize Netflix-specific control zones"""
        screen_w, screen_h = pyautogui.size()
        
        zones = self.video_zones.copy()
        zones.update({
            "subtitle_toggle": {
                "x1": screen_w * 0.8, "y1": screen_h * 0.8,
                "x2": screen_w * 0.95, "y2": screen_h * 0.95
            },
            "episode_next": {
                "x1": screen_w * 0.85, "y1": screen_h * 0.4,
                "x2": screen_w, "y2": screen_h * 0.6
            },
            "episode_previous": {
                "x1": 0, "y1": screen_h * 0.4,
                "x2": screen_w * 0.15, "y2": screen_h * 0.6
            },
            "browse_mode": {
                "x1": 0, "y1": 0,
                "x2": screen_w * 0.2, "y2": screen_h * 0.2
            },
            "search_zone": {
                "x1": screen_w * 0.4, "y1": 0,
                "x2": screen_w * 0.6, "y2": 100
            }
        })
        
        return zones
    
    def detect_platform(self) -> bool:
        """Detect if Netflix is currently active"""
        try:
            # Check for Netflix in browser windows
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] in ['chrome.exe', 'firefox.exe', 'msedge.exe', 'safari']:
                        cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                        if any(pattern in cmdline.lower() for pattern in ['netflix']):
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Check for Netflix app
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'netflix' in proc.info['name'].lower():
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return False
        except Exception as e:
            logging.error(f"Error detecting Netflix: {e}")
            return False
    
    def get_platform_specific_gestures(self) -> Dict[str, Any]:
        """Get Netflix-specific gesture mappings"""
        return {
            "subtitle_toggle": {
                "gesture": "sustained_gaze",
                "zone": "subtitle_toggle",
                "duration": 2.0,
                "action": self._toggle_subtitles
            },
            "next_episode": {
                "gesture": "sustained_gaze",
                "zone": "episode_next",
                "duration": 1.5,
                "action": self._next_episode
            },
            "previous_episode": {
                "gesture": "sustained_gaze",
                "zone": "episode_previous",
                "duration": 1.5,
                "action": self._previous_episode
            },
            "browse_mode": {
                "gesture": "sustained_gaze",
                "zone": "browse_mode",
                "duration": 2.0,
                "action": self._enter_browse_mode
            },
            "search": {
                "gesture": "sustained_gaze",
                "zone": "search_zone",
                "duration": 2.0,
                "action": self._open_search
            }
        }
    
    def _process_platform_gestures(self, eye_position: Tuple[float, float], 
                                 gesture_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Netflix-specific gestures"""
        actions = []
        screen_pos = self._eye_to_screen_coords(eye_position)
        
        # Process Netflix zones
        for zone_name, zone_coords in self.netflix_zones.items():
            if (zone_coords["x1"] <= screen_pos[0] <= zone_coords["x2"] and
                zone_coords["y1"] <= screen_pos[1] <= zone_coords["y2"]):
                
                action = self._execute_netflix_control(zone_name, screen_pos)
                if action:
                    actions.append(action)
        
        # Process Netflix-specific blink patterns
        if gesture_data.get("blink_detected"):
            blink_action = self._process_netflix_blinks(gesture_data)
            if blink_action:
                actions.append(blink_action)
        
        return actions
    
    def _execute_netflix_control(self, zone_name: str, position: Tuple[int, int]) -> Optional[Dict[str, Any]]:
        """Execute Netflix-specific control actions"""
        try:
            if zone_name == "subtitle_toggle":
                return self._toggle_subtitles()
            elif zone_name == "episode_next":
                return self._next_episode()
            elif zone_name == "episode_previous":
                return self._previous_episode()
            elif zone_name == "browse_mode":
                return self._enter_browse_mode()
            elif zone_name == "search_zone":
                return self._open_search()
        except Exception as e:
            logging.error(f"Error executing Netflix control {zone_name}: {e}")
        
        return None
    
    def _toggle_subtitles(self) -> Dict[str, Any]:
        """Toggle subtitle display"""
        try:
            # Netflix subtitle toggle shortcut
            pyautogui.hotkey('ctrl', 'shift', 'alt', 't')
            self.subtitle_enabled = not self.subtitle_enabled
            
            return {
                "type": "netflix_control",
                "action": "subtitle_toggle",
                "state": "enabled" if self.subtitle_enabled else "disabled"
            }
        except Exception as e:
            logging.error(f"Error toggling subtitles: {e}")
            return {"type": "error", "message": str(e)}
    
    def _next_episode(self) -> Dict[str, Any]:
        """Skip to next episode"""
        try:
            # Netflix next episode shortcut
            pyautogui.hotkey('shift', 'n')
            
            return {
                "type": "netflix_control",
                "action": "next_episode"
            }
        except Exception as e:
            logging.error(f"Error going to next episode: {e}")
            return {"type": "error", "message": str(e)}
    
    def _previous_episode(self) -> Dict[str, Any]:
        """Go to previous episode"""
        try:
            # Netflix previous episode (custom implementation)
            pyautogui.hotkey('shift', 'p')
            
            return {
                "type": "netflix_control",
                "action": "previous_episode"
            }
        except Exception as e:
            logging.error(f"Error going to previous episode: {e}")
            return {"type": "error", "message": str(e)}
    
    def _enter_browse_mode(self) -> Dict[str, Any]:
        """Enter Netflix browse mode"""
        try:
            # Press Escape to exit fullscreen and return to browse
            pyautogui.press('escape')
            
            return {
                "type": "netflix_control",
                "action": "browse_mode"
            }
        except Exception as e:
            logging.error(f"Error entering browse mode: {e}")
            return {"type": "error", "message": str(e)}
    
    def _open_search(self) -> Dict[str, Any]:
        """Open Netflix search"""
        try:
            # Netflix search shortcut
            pyautogui.hotkey('ctrl', 'k')
            
            return {
                "type": "netflix_control",
                "action": "open_search"
            }
        except Exception as e:
            logging.error(f"Error opening search: {e}")
            return {"type": "error", "message": str(e)}
    
    def _process_netflix_blinks(self, gesture_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process Netflix-specific blink patterns"""
        # Triple blink for skip intro
        if hasattr(self, 'blink_pattern'):
            self.blink_pattern.append(gesture_data.get("timestamp", 0))
            
            # Keep only recent blinks (within 2 seconds)
            current_time = gesture_data.get("timestamp", 0)
            self.blink_pattern = [t for t in self.blink_pattern if current_time - t <= 2.0]
            
            if len(self.blink_pattern) >= 3:
                # Triple blink detected - skip intro
                try:
                    pyautogui.hotkey('ctrl', 's')  # Netflix skip intro
                    self.blink_pattern = []
                    return {
                        "type": "netflix_control",
                        "action": "skip_intro",
                        "trigger": "triple_blink"
                    }
                except Exception as e:
                    logging.error(f"Error skipping intro: {e}")
        else:
            self.blink_pattern = [gesture_data.get("timestamp", 0)]
        
        return None
    
    def get_netflix_recommendations(self, eye_tracking_data: Dict[str, Any]) -> List[str]:
        """Get viewing recommendations based on eye tracking patterns"""
        # Analyze viewing patterns and suggest content
        # This is a placeholder for advanced analytics
        recommendations = []
        
        # Example: If user frequently looks at action movie thumbnails
        if eye_tracking_data.get("genre_preference") == "action":
            recommendations.append("Action movies in your area")
        
        return recommendations
