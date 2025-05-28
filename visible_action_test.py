#!/usr/bin/env python3
"""
Visible Action Test
Creates a test window with visible feedback for gesture actions
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import subprocess
from gesture_action_processor import GestureActionProcessor
from advanced_gesture_detector import GestureType

class VisibleActionTest:
    def __init__(self):
        """Initialize the visible action test window"""
        self.root = tk.Tk()
        self.root.title("Gesture Action Test - Watch for Actions Here!")
        self.root.geometry("800x600")
        self.root.configure(bg='lightblue')
        
        # Make window stay on top
        self.root.attributes('-topmost', True)
        
        # Create UI
        self.setup_ui()
        
        # Initialize gesture processor
        self.processor = GestureActionProcessor('xdotool')
        
        # Action counter
        self.action_count = 0
        
        print("🎯 Visible Action Test Window Created")
        print("This window will show visible feedback for all gesture actions")
        print("Keep this window in focus and try your gestures!")
    
    def setup_ui(self):
        """Setup the test UI"""
        # Title
        title_label = tk.Label(self.root, text="🎯 GESTURE ACTION TEST WINDOW", 
                              font=('Arial', 20, 'bold'), bg='lightblue', fg='darkblue')
        title_label.pack(pady=20)
        
        # Instructions
        instructions = tk.Label(self.root, 
                               text="Keep this window in focus and perform gestures.\nYou should see immediate visual feedback below:",
                               font=('Arial', 12), bg='lightblue', fg='black')
        instructions.pack(pady=10)
        
        # Action feedback area
        self.feedback_frame = tk.Frame(self.root, bg='white', relief='sunken', bd=2)
        self.feedback_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Scrollable text area for action log
        self.action_log = scrolledtext.ScrolledText(self.feedback_frame, 
                                                   font=('Courier', 12),
                                                   bg='black', fg='green',
                                                   height=15)
        self.action_log.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Status bar
        self.status_frame = tk.Frame(self.root, bg='lightgray')
        self.status_frame.pack(fill='x', side='bottom')
        
        self.status_label = tk.Label(self.status_frame, text="Ready for gesture actions...", 
                                    font=('Arial', 10), bg='lightgray')
        self.status_label.pack(side='left', padx=10, pady=5)
        
        self.action_counter_label = tk.Label(self.status_frame, text="Actions: 0", 
                                           font=('Arial', 10, 'bold'), bg='lightgray')
        self.action_counter_label.pack(side='right', padx=10, pady=5)
        
        # Test buttons
        button_frame = tk.Frame(self.root, bg='lightblue')
        button_frame.pack(fill='x', pady=10)
        
        tk.Button(button_frame, text="Test Left Click", 
                 command=self.test_left_click, bg='lightgreen').pack(side='left', padx=5)
        tk.Button(button_frame, text="Test Right Click", 
                 command=self.test_right_click, bg='lightcoral').pack(side='left', padx=5)
        tk.Button(button_frame, text="Test Scroll Down", 
                 command=self.test_scroll_down, bg='lightyellow').pack(side='left', padx=5)
        tk.Button(button_frame, text="Test Scroll Up", 
                 command=self.test_scroll_up, bg='lightcyan').pack(side='left', padx=5)
        tk.Button(button_frame, text="Clear Log", 
                 command=self.clear_log, bg='lightpink').pack(side='right', padx=5)
        
        # Initial message
        self.log_action("🚀 Gesture Action Test Started")
        self.log_action("Perform eye winks and head tilts to see actions here!")
        self.log_action("=" * 50)
    
    def log_action(self, message):
        """Log an action to the display"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.action_log.insert(tk.END, log_message)
        self.action_log.see(tk.END)
        
        # Update status
        self.status_label.config(text=f"Last action: {message}")
        
        # Flash the window
        self.flash_window()
    
    def flash_window(self):
        """Flash the window to indicate action"""
        original_bg = self.root.cget('bg')
        self.root.configure(bg='yellow')
        self.root.after(100, lambda: self.root.configure(bg=original_bg))
    
    def increment_counter(self):
        """Increment and update action counter"""
        self.action_count += 1
        self.action_counter_label.config(text=f"Actions: {self.action_count}")
    
    def test_left_click(self):
        """Test left click action"""
        gesture_data = {
            'type': GestureType.LEFT_WINK,
            'confidence': 0.8,
            'timestamp': time.time()
        }
        success = self.processor.left_click(gesture_data)
        self.log_action(f"👆 LEFT CLICK - {'SUCCESS' if success else 'FAILED'}")
        if success:
            self.increment_counter()
    
    def test_right_click(self):
        """Test right click action"""
        gesture_data = {
            'type': GestureType.RIGHT_WINK,
            'confidence': 0.8,
            'timestamp': time.time()
        }
        success = self.processor.right_click(gesture_data)
        self.log_action(f"👆 RIGHT CLICK - {'SUCCESS' if success else 'FAILED'}")
        if success:
            self.increment_counter()
    
    def test_scroll_down(self):
        """Test scroll down action"""
        gesture_data = {
            'type': GestureType.HEAD_TILT_DOWN,
            'confidence': 1.0,
            'angle': 25.0,
            'timestamp': time.time()
        }
        success = self.processor.scroll_down(gesture_data)
        self.log_action(f"⬇️  SCROLL DOWN (25.0°) - {'SUCCESS' if success else 'FAILED'}")
        if success:
            self.increment_counter()
    
    def test_scroll_up(self):
        """Test scroll up action"""
        gesture_data = {
            'type': GestureType.HEAD_TILT_UP,
            'confidence': 1.0,
            'angle': -25.0,
            'timestamp': time.time()
        }
        success = self.processor.scroll_up(gesture_data)
        self.log_action(f"⬆️  SCROLL UP (-25.0°) - {'SUCCESS' if success else 'FAILED'}")
        if success:
            self.increment_counter()
    
    def clear_log(self):
        """Clear the action log"""
        self.action_log.delete(1.0, tk.END)
        self.log_action("🧹 Log cleared")
    
    def simulate_gesture_action(self, gesture_type, **kwargs):
        """Simulate a gesture action for testing"""
        gesture_data = {
            'type': gesture_type,
            'confidence': kwargs.get('confidence', 0.8),
            'timestamp': time.time()
        }
        
        if 'angle' in kwargs:
            gesture_data['angle'] = kwargs['angle']
        
        success = self.processor.execute_gesture_action(gesture_data)
        
        # Log the action
        action_name = gesture_type.value.replace('_', ' ').title()
        angle_info = f" ({kwargs['angle']:.1f}°)" if 'angle' in kwargs else ""
        self.log_action(f"🎯 {action_name}{angle_info} - {'SUCCESS' if success else 'FAILED'}")
        
        if success:
            self.increment_counter()
        
        return success
    
    def run(self):
        """Run the test window"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Test interrupted by user")

def main():
    """Main function"""
    print("🎯 Starting Visible Action Test")
    print("This will create a test window where you can see gesture actions")
    print("Keep the test window in focus and try your gestures!")
    
    test = VisibleActionTest()
    test.run()

if __name__ == "__main__":
    main()
