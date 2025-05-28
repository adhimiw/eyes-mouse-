"""
Configuration Manager for Eye-Controlled Interface
Handles user settings, profiles, and application configuration
"""

import json
import os
import configparser
from typing import Dict, Any, Optional
import logging

class ConfigManager:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "settings.json")
        self.profiles_file = os.path.join(config_dir, "profiles.json")

        # Create config directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)

        # Default configuration
        self.default_config = {
            "tracking": {
                "sensitivity": 1.0,
                "smoothing": 0.7,
                "dead_zone_radius": 10,
                "acceleration_curve": "linear",
                "frame_rate": 30,
                "tracking_quality_threshold": 0.8
            },
            "gestures": {
                "blink_threshold": 0.004,
                "double_blink_timeout": 0.5,
                "long_blink_duration": 1.0,
                "dwell_time": 1.5,
                "gesture_cooldown": 0.3
            },
            "display": {
                "show_overlay": True,
                "show_eye_tracking": True,
                "overlay_opacity": 0.8,
                "cursor_trail": True,
                "visual_feedback": True
            },
            "streaming": {
                "auto_detect_platforms": True,
                "netflix_optimizations": True,
                "youtube_optimizations": True,
                "hotstar_optimizations": True,
                "auto_pause_timeout": 10.0
            },
            "accessibility": {
                "break_reminders": True,
                "break_interval": 1800,  # 30 minutes
                "fatigue_detection": True,
                "emergency_disable_key": "ctrl+shift+e"
            },
            "performance": {
                "max_cpu_usage": 15.0,
                "max_memory_mb": 200,
                "adaptive_quality": True,
                "low_latency_mode": True
            }
        }

        self.current_config = self.load_config()
        self.profiles = self.load_profiles()
        self.current_profile = "default"

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_configs(self.default_config, config)
            else:
                self.save_config(self.default_config)
                return self.default_config.copy()
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return self.default_config.copy()

    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Save configuration to file"""
        try:
            config_to_save = config or self.current_config
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"Error saving config: {e}")
            return False

    def load_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load user profiles"""
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, 'r') as f:
                    return json.load(f)
            else:
                default_profiles = {
                    "default": self.default_config.copy(),
                    "high_precision": self._create_precision_profile(),
                    "accessibility": self._create_accessibility_profile(),
                    "gaming": self._create_gaming_profile()
                }
                self.save_profiles(default_profiles)
                return default_profiles
        except Exception as e:
            logging.error(f"Error loading profiles: {e}")
            return {"default": self.default_config.copy()}

    def save_profiles(self, profiles: Optional[Dict[str, Dict[str, Any]]] = None) -> bool:
        """Save user profiles to file"""
        try:
            profiles_to_save = profiles or self.profiles
            with open(self.profiles_file, 'w') as f:
                json.dump(profiles_to_save, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"Error saving profiles: {e}")
            return False

    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        try:
            return self.current_config.get(category, {}).get(key, default)
        except Exception:
            return default

    def set_setting(self, category: str, key: str, value: Any) -> bool:
        """Set a specific setting value"""
        try:
            if category not in self.current_config:
                self.current_config[category] = {}
            self.current_config[category][key] = value
            return self.save_config()
        except Exception as e:
            logging.error(f"Error setting config value: {e}")
            return False

    def get_section(self, category: str) -> Dict[str, Any]:
        """Get all settings in a category/section"""
        try:
            return self.current_config.get(category, {}).copy()
        except Exception:
            return {}

    def switch_profile(self, profile_name: str) -> bool:
        """Switch to a different user profile"""
        if profile_name in self.profiles:
            self.current_profile = profile_name
            self.current_config = self.profiles[profile_name].copy()
            return True
        return False

    def create_profile(self, name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new user profile"""
        try:
            profile_config = config or self.current_config.copy()
            self.profiles[name] = profile_config
            return self.save_profiles()
        except Exception as e:
            logging.error(f"Error creating profile: {e}")
            return False

    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config with defaults"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def _create_precision_profile(self) -> Dict[str, Any]:
        """Create high precision profile"""
        config = self.default_config.copy()
        config["tracking"]["sensitivity"] = 0.5
        config["tracking"]["smoothing"] = 0.9
        config["tracking"]["dead_zone_radius"] = 5
        config["gestures"]["dwell_time"] = 2.0
        return config

    def _create_accessibility_profile(self) -> Dict[str, Any]:
        """Create accessibility-focused profile"""
        config = self.default_config.copy()
        config["tracking"]["sensitivity"] = 1.5
        config["gestures"]["dwell_time"] = 1.0
        config["accessibility"]["break_interval"] = 900  # 15 minutes
        config["display"]["visual_feedback"] = True
        return config

    def _create_gaming_profile(self) -> Dict[str, Any]:
        """Create gaming-optimized profile"""
        config = self.default_config.copy()
        config["tracking"]["sensitivity"] = 1.2
        config["tracking"]["smoothing"] = 0.3
        config["performance"]["low_latency_mode"] = True
        config["gestures"]["gesture_cooldown"] = 0.1
        return config
