"""
Performance Monitoring and Optimization System
Monitors system performance and automatically adjusts settings for optimal operation
"""

import time
import psutil
import threading
import logging
from typing import Dict, Any, List, Optional, Callable
from collections import deque
import json
import os

class PerformanceMonitor:
    def __init__(self, config_manager):
        self.config = config_manager
        
        # Performance metrics
        self.cpu_usage_history = deque(maxlen=60)  # Last 60 seconds
        self.memory_usage_history = deque(maxlen=60)
        self.fps_history = deque(maxlen=30)
        self.latency_history = deque(maxlen=100)
        
        # Performance thresholds
        self.max_cpu_usage = self.config.get_setting("performance", "max_cpu_usage", 15.0)
        self.max_memory_mb = self.config.get_setting("performance", "max_memory_mb", 200)
        self.min_fps = 25
        self.max_latency_ms = 50
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        self.last_optimization_time = 0
        self.optimization_cooldown = 30  # seconds
        
        # Performance callbacks
        self.performance_callbacks = []
        
        # Adaptive quality settings
        self.quality_levels = {
            "high": {
                "frame_rate": 30,
                "resolution_scale": 1.0,
                "smoothing": 0.7,
                "tracking_quality_threshold": 0.8
            },
            "medium": {
                "frame_rate": 25,
                "resolution_scale": 0.8,
                "smoothing": 0.5,
                "tracking_quality_threshold": 0.6
            },
            "low": {
                "frame_rate": 20,
                "resolution_scale": 0.6,
                "smoothing": 0.3,
                "tracking_quality_threshold": 0.4
            }
        }
        
        self.current_quality_level = "high"
        
        # Performance log
        self.performance_log = []
        self.log_file = "performance_log.json"
        
    def start_monitoring(self):
        """Start performance monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logging.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        
        # Save performance log
        self._save_performance_log()
        
        logging.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        try:
            while self.is_monitoring:
                start_time = time.time()
                
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_info = psutil.virtual_memory()
                memory_mb = memory_info.used / (1024 * 1024)
                
                # Store metrics
                self.cpu_usage_history.append(cpu_percent)
                self.memory_usage_history.append(memory_mb)
                
                # Check for performance issues
                self._check_performance_thresholds()
                
                # Auto-optimize if needed
                if self.config.get_setting("performance", "adaptive_quality", True):
                    self._auto_optimize_performance()
                
                # Log performance data
                self._log_performance_data(cpu_percent, memory_mb)
                
                # Notify callbacks
                self._notify_performance_callbacks()
                
                # Sleep for monitoring interval
                elapsed = time.time() - start_time
                sleep_time = max(0, 1.0 - elapsed)  # Monitor every second
                time.sleep(sleep_time)
                
        except Exception as e:
            logging.error(f"Error in performance monitoring loop: {e}")
    
    def _check_performance_thresholds(self):
        """Check if performance thresholds are exceeded"""
        if not self.cpu_usage_history or not self.memory_usage_history:
            return
        
        # Check CPU usage
        avg_cpu = sum(list(self.cpu_usage_history)[-10:]) / min(10, len(self.cpu_usage_history))
        if avg_cpu > self.max_cpu_usage:
            logging.warning(f"High CPU usage detected: {avg_cpu:.1f}%")
            self._handle_high_cpu_usage()
        
        # Check memory usage
        current_memory = self.memory_usage_history[-1]
        if current_memory > self.max_memory_mb:
            logging.warning(f"High memory usage detected: {current_memory:.1f}MB")
            self._handle_high_memory_usage()
        
        # Check FPS
        if self.fps_history:
            avg_fps = sum(self.fps_history) / len(self.fps_history)
            if avg_fps < self.min_fps:
                logging.warning(f"Low FPS detected: {avg_fps:.1f}")
                self._handle_low_fps()
        
        # Check latency
        if self.latency_history:
            avg_latency = sum(self.latency_history) / len(self.latency_history)
            if avg_latency > self.max_latency_ms:
                logging.warning(f"High latency detected: {avg_latency:.1f}ms")
                self._handle_high_latency()
    
    def _handle_high_cpu_usage(self):
        """Handle high CPU usage"""
        if self.current_quality_level == "high":
            self._set_quality_level("medium")
        elif self.current_quality_level == "medium":
            self._set_quality_level("low")
    
    def _handle_high_memory_usage(self):
        """Handle high memory usage"""
        # Reduce frame buffer sizes
        if hasattr(self, 'eye_tracker'):
            # Reduce history buffer sizes
            pass
        
        # Force garbage collection
        import gc
        gc.collect()
    
    def _handle_low_fps(self):
        """Handle low FPS"""
        if self.current_quality_level == "high":
            self._set_quality_level("medium")
        elif self.current_quality_level == "medium":
            self._set_quality_level("low")
    
    def _handle_high_latency(self):
        """Handle high latency"""
        # Enable low latency mode
        self.config.set_setting("performance", "low_latency_mode", True)
        
        # Reduce processing complexity
        if self.current_quality_level != "low":
            self._set_quality_level("low")
    
    def _auto_optimize_performance(self):
        """Automatically optimize performance based on current metrics"""
        current_time = time.time()
        
        # Check optimization cooldown
        if current_time - self.last_optimization_time < self.optimization_cooldown:
            return
        
        # Calculate performance score
        performance_score = self._calculate_performance_score()
        
        # Adjust quality level based on performance
        if performance_score < 0.3 and self.current_quality_level != "low":
            self._set_quality_level("low")
            self.last_optimization_time = current_time
        elif performance_score > 0.7 and self.current_quality_level == "low":
            self._set_quality_level("medium")
            self.last_optimization_time = current_time
        elif performance_score > 0.9 and self.current_quality_level == "medium":
            self._set_quality_level("high")
            self.last_optimization_time = current_time
    
    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0.0 to 1.0)"""
        scores = []
        
        # CPU score
        if self.cpu_usage_history:
            avg_cpu = sum(list(self.cpu_usage_history)[-10:]) / min(10, len(self.cpu_usage_history))
            cpu_score = max(0, 1.0 - (avg_cpu / 100.0))
            scores.append(cpu_score)
        
        # Memory score
        if self.memory_usage_history:
            current_memory = self.memory_usage_history[-1]
            memory_score = max(0, 1.0 - (current_memory / (self.max_memory_mb * 2)))
            scores.append(memory_score)
        
        # FPS score
        if self.fps_history:
            avg_fps = sum(self.fps_history) / len(self.fps_history)
            fps_score = min(1.0, avg_fps / 30.0)
            scores.append(fps_score)
        
        # Latency score
        if self.latency_history:
            avg_latency = sum(self.latency_history) / len(self.latency_history)
            latency_score = max(0, 1.0 - (avg_latency / 100.0))
            scores.append(latency_score)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _set_quality_level(self, level: str):
        """Set performance quality level"""
        if level not in self.quality_levels:
            return
        
        self.current_quality_level = level
        quality_settings = self.quality_levels[level]
        
        # Update configuration
        self.config.set_setting("tracking", "frame_rate", quality_settings["frame_rate"])
        self.config.set_setting("tracking", "smoothing", quality_settings["smoothing"])
        self.config.set_setting("tracking", "tracking_quality_threshold", 
                               quality_settings["tracking_quality_threshold"])
        
        logging.info(f"Performance quality level set to: {level}")
    
    def update_fps(self, fps: float):
        """Update FPS measurement"""
        self.fps_history.append(fps)
    
    def update_latency(self, latency_ms: float):
        """Update latency measurement"""
        self.latency_history.append(latency_ms)
    
    def add_performance_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback for performance updates"""
        self.performance_callbacks.append(callback)
    
    def _notify_performance_callbacks(self):
        """Notify all performance callbacks"""
        performance_data = self.get_current_performance_data()
        
        for callback in self.performance_callbacks:
            try:
                callback(performance_data)
            except Exception as e:
                logging.error(f"Error in performance callback: {e}")
    
    def get_current_performance_data(self) -> Dict[str, Any]:
        """Get current performance data"""
        data = {
            "timestamp": time.time(),
            "cpu_usage": self.cpu_usage_history[-1] if self.cpu_usage_history else 0,
            "memory_usage_mb": self.memory_usage_history[-1] if self.memory_usage_history else 0,
            "fps": self.fps_history[-1] if self.fps_history else 0,
            "latency_ms": self.latency_history[-1] if self.latency_history else 0,
            "quality_level": self.current_quality_level,
            "performance_score": self._calculate_performance_score()
        }
        
        return data
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics"""
        summary = {
            "monitoring_duration": len(self.cpu_usage_history),
            "quality_level": self.current_quality_level,
            "performance_score": self._calculate_performance_score()
        }
        
        # CPU statistics
        if self.cpu_usage_history:
            cpu_list = list(self.cpu_usage_history)
            summary["cpu"] = {
                "current": cpu_list[-1],
                "average": sum(cpu_list) / len(cpu_list),
                "max": max(cpu_list),
                "min": min(cpu_list)
            }
        
        # Memory statistics
        if self.memory_usage_history:
            memory_list = list(self.memory_usage_history)
            summary["memory"] = {
                "current_mb": memory_list[-1],
                "average_mb": sum(memory_list) / len(memory_list),
                "max_mb": max(memory_list),
                "min_mb": min(memory_list)
            }
        
        # FPS statistics
        if self.fps_history:
            fps_list = list(self.fps_history)
            summary["fps"] = {
                "current": fps_list[-1],
                "average": sum(fps_list) / len(fps_list),
                "max": max(fps_list),
                "min": min(fps_list)
            }
        
        # Latency statistics
        if self.latency_history:
            latency_list = list(self.latency_history)
            summary["latency"] = {
                "current_ms": latency_list[-1],
                "average_ms": sum(latency_list) / len(latency_list),
                "max_ms": max(latency_list),
                "min_ms": min(latency_list)
            }
        
        return summary
    
    def _log_performance_data(self, cpu_percent: float, memory_mb: float):
        """Log performance data for analysis"""
        log_entry = {
            "timestamp": time.time(),
            "cpu_percent": cpu_percent,
            "memory_mb": memory_mb,
            "quality_level": self.current_quality_level
        }
        
        self.performance_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.performance_log) > 1000:
            self.performance_log = self.performance_log[-1000:]
    
    def _save_performance_log(self):
        """Save performance log to file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.performance_log, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving performance log: {e}")
    
    def load_performance_log(self) -> List[Dict[str, Any]]:
        """Load performance log from file"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Error loading performance log: {e}")
        
        return []
    
    def reset_performance_data(self):
        """Reset all performance data"""
        self.cpu_usage_history.clear()
        self.memory_usage_history.clear()
        self.fps_history.clear()
        self.latency_history.clear()
        self.performance_log.clear()
        
        logging.info("Performance data reset")
