#!/usr/bin/env python3
"""
Gesture Action Processor
Handles the execution of actions based on detected gestures
"""

import subprocess
import time
import logging
from typing import Dict, List, Optional
from advanced_gesture_detector import GestureType

class GestureActionProcessor:
    def __init__(self, mouse_backend='xdotool'):
        """Initialize gesture action processor"""
        self.mouse_backend = mouse_backend
        self.drag_active = False
        self.drag_start_pos = None
        self.last_action_time = {}

        # Action mappings
        self.action_mappings = {
            GestureType.LEFT_WINK: self.left_click,
            GestureType.RIGHT_WINK: self.right_click,
            GestureType.BOTH_BLINK: self.middle_click_or_drag,
            GestureType.HEAD_TILT_DOWN: self.scroll_down,
            GestureType.HEAD_TILT_UP: self.scroll_up,
            GestureType.HEAD_TILT_LEFT: self.scroll_left,
            GestureType.HEAD_TILT_RIGHT: self.scroll_right
        }

        # Action statistics
        self.action_stats = {gesture_type: 0 for gesture_type in GestureType}

        # Enhanced action settings
        self.enhanced_feedback = True
        self.target_active_window = True
        self.action_intensity = 3  # Number of scroll steps

        print("✅ Gesture Action Processor initialized")

    def execute_gesture_action(self, gesture_data):
        """Execute action based on gesture type"""
        gesture_type = gesture_data['type']
        current_time = time.time()

        try:
            # Execute the mapped action
            if gesture_type in self.action_mappings:
                success = self.action_mappings[gesture_type](gesture_data)

                if success:
                    self.action_stats[gesture_type] += 1
                    self.last_action_time[gesture_type] = current_time

                    # Log successful action
                    confidence = gesture_data.get('confidence', 0.0)
                    angle = gesture_data.get('angle', 0.0)

                    if angle != 0.0:
                        print(f"🎯 {gesture_type.value}: {confidence:.2f} confidence, {angle:.1f}° angle")
                    else:
                        print(f"🎯 {gesture_type.value}: {confidence:.2f} confidence")

                    return True
                else:
                    logging.warning(f"Failed to execute action for {gesture_type.value}")
                    return False
            else:
                logging.warning(f"No action mapping for gesture type: {gesture_type.value}")
                return False

        except Exception as e:
            logging.error(f"Error executing gesture action {gesture_type.value}: {e}")
            return False

    def left_click(self, gesture_data):
        """Execute left mouse click with multiple fallback methods"""
        try:
            success = False

            if self.mouse_backend == 'xdotool':
                # Method 1: Direct xdotool click
                try:
                    result = subprocess.run(['xdotool', 'click', '1'],
                                          capture_output=True, text=True, timeout=0.5)
                    if result.returncode == 0:
                        success = True
                        print("👆 Left click (left wink) - xdotool")
                    else:
                        print(f"xdotool click failed: {result.stderr}")
                except subprocess.TimeoutExpired:
                    print("xdotool click timeout")

                # Method 2: Fallback with window focus
                if not success:
                    try:
                        # Get current window and click
                        subprocess.run(['xdotool', 'getactivewindow', 'mousemove', '--window', '%1', '50', '50', 'click', '1'],
                                     capture_output=True, timeout=0.5)
                        success = True
                        print("👆 Left click (left wink) - xdotool with focus")
                    except:
                        pass

            # Method 3: PyAutoGUI fallback
            if not success:
                try:
                    import pyautogui
                    pyautogui.click()
                    success = True
                    print("👆 Left click (left wink) - pyautogui")
                except:
                    pass

            # Method 4: Direct system call
            if not success:
                try:
                    import os
                    os.system('xdotool click 1')
                    success = True
                    print("👆 Left click (left wink) - system call")
                except:
                    pass

            if not success:
                print("❌ Left click failed - all methods exhausted")

            return success

        except Exception as e:
            logging.error(f"Left click error: {e}")
            return False

    def right_click(self, gesture_data):
        """Execute right mouse click with multiple fallback methods"""
        try:
            success = False

            if self.mouse_backend == 'xdotool':
                # Method 1: Direct xdotool right click
                try:
                    result = subprocess.run(['xdotool', 'click', '3'],
                                          capture_output=True, text=True, timeout=0.5)
                    if result.returncode == 0:
                        success = True
                        print("👆 Right click (right wink) - xdotool")
                    else:
                        print(f"xdotool right click failed: {result.stderr}")
                except subprocess.TimeoutExpired:
                    print("xdotool right click timeout")

                # Method 2: System call fallback
                if not success:
                    try:
                        import os
                        os.system('xdotool click 3')
                        success = True
                        print("👆 Right click (right wink) - system call")
                    except:
                        pass

            # Method 3: PyAutoGUI fallback
            if not success:
                try:
                    import pyautogui
                    pyautogui.rightClick()
                    success = True
                    print("👆 Right click (right wink) - pyautogui")
                except:
                    pass

            if not success:
                print("❌ Right click failed - all methods exhausted")

            return success

        except Exception as e:
            logging.error(f"Right click error: {e}")
            return False

    def middle_click_or_drag(self, gesture_data):
        """Execute middle click or toggle drag mode"""
        try:
            if not self.drag_active:
                # Start drag mode or middle click
                if self.mouse_backend == 'xdotool':
                    # Get current mouse position for drag start
                    result = subprocess.run(['xdotool', 'getmouselocation'],
                                          capture_output=True, text=True, check=True)
                    pos_str = result.stdout.strip()
                    # Parse position (format: x:123 y:456 screen:0 window:789)
                    x_pos = int(pos_str.split()[0].split(':')[1])
                    y_pos = int(pos_str.split()[1].split(':')[1])
                    self.drag_start_pos = (x_pos, y_pos)

                    # Start drag (mouse down)
                    subprocess.run(['xdotool', 'mousedown', '1'],
                                 capture_output=True, check=True, timeout=0.5)
                    self.drag_active = True
                    print("🖱️  Drag started (both eyes blink)")
                else:
                    import pyautogui
                    self.drag_start_pos = pyautogui.position()
                    pyautogui.mouseDown()
                    self.drag_active = True
                    print("🖱️  Drag started (both eyes blink)")
            else:
                # End drag mode
                if self.mouse_backend == 'xdotool':
                    subprocess.run(['xdotool', 'mouseup', '1'],
                                 capture_output=True, check=True, timeout=0.5)
                else:
                    import pyautogui
                    pyautogui.mouseUp()

                self.drag_active = False
                self.drag_start_pos = None
                print("🖱️  Drag ended (both eyes blink)")

            return True

        except Exception as e:
            logging.error(f"Middle click/drag error: {e}")
            return False

    def scroll_down(self, gesture_data):
        """Execute scroll down action with multiple methods"""
        try:
            success = False
            angle = gesture_data.get('angle', 0.0)

            if self.mouse_backend == 'xdotool':
                # Method 1: Multiple scroll wheel down for visibility
                try:
                    for _ in range(self.action_intensity):
                        result = subprocess.run(['xdotool', 'click', '5'],
                                              capture_output=True, text=True, timeout=0.1)
                        if result.returncode != 0:
                            break
                    else:
                        success = True
                        print(f"⬇️  Scroll down (head tilt down {angle:.1f}°) - {self.action_intensity}x wheel")
                except:
                    pass

                # Method 2: Page Down key
                if not success:
                    try:
                        subprocess.run(['xdotool', 'key', 'Page_Down'],
                                     capture_output=True, timeout=0.3)
                        success = True
                        print(f"⬇️  Scroll down (head tilt down {angle:.1f}°) - Page Down")
                    except:
                        pass

                # Method 3: Arrow Down key
                if not success:
                    try:
                        subprocess.run(['xdotool', 'key', 'Down', 'Down', 'Down'],
                                     capture_output=True, timeout=0.3)
                        success = True
                        print(f"⬇️  Scroll down (head tilt down {angle:.1f}°) - Arrow Down")
                    except:
                        pass

            # Method 4: PyAutoGUI fallback
            if not success:
                try:
                    import pyautogui
                    pyautogui.scroll(-3)  # Negative for down
                    success = True
                    print(f"⬇️  Scroll down (head tilt down {angle:.1f}°) - pyautogui")
                except:
                    pass

            if not success:
                print(f"❌ Scroll down failed (angle {angle:.1f}°)")

            return success

        except Exception as e:
            logging.error(f"Scroll down error: {e}")
            return False

    def scroll_up(self, gesture_data):
        """Execute scroll up action with multiple methods"""
        try:
            success = False
            angle = gesture_data.get('angle', 0.0)

            if self.mouse_backend == 'xdotool':
                # Method 1: Multiple scroll wheel up for visibility
                try:
                    for _ in range(self.action_intensity):
                        result = subprocess.run(['xdotool', 'click', '4'],
                                              capture_output=True, text=True, timeout=0.1)
                        if result.returncode != 0:
                            break
                    else:
                        success = True
                        print(f"⬆️  Scroll up (head tilt up {angle:.1f}°) - {self.action_intensity}x wheel")
                except:
                    pass

                # Method 2: Page Up key
                if not success:
                    try:
                        subprocess.run(['xdotool', 'key', 'Page_Up'],
                                     capture_output=True, timeout=0.3)
                        success = True
                        print(f"⬆️  Scroll up (head tilt up {angle:.1f}°) - Page Up")
                    except:
                        pass

                # Method 3: Arrow Up key
                if not success:
                    try:
                        subprocess.run(['xdotool', 'key', 'Up', 'Up', 'Up'],
                                     capture_output=True, timeout=0.3)
                        success = True
                        print(f"⬆️  Scroll up (head tilt up {angle:.1f}°) - Arrow Up")
                    except:
                        pass

            # Method 4: PyAutoGUI fallback
            if not success:
                try:
                    import pyautogui
                    pyautogui.scroll(3)  # Positive for up
                    success = True
                    print(f"⬆️  Scroll up (head tilt up {angle:.1f}°) - pyautogui")
                except:
                    pass

            if not success:
                print(f"❌ Scroll up failed (angle {angle:.1f}°)")

            return success

        except Exception as e:
            logging.error(f"Scroll up error: {e}")
            return False

    def scroll_left(self, gesture_data):
        """Execute scroll left action"""
        try:
            if self.mouse_backend == 'xdotool':
                # Use horizontal scroll or arrow key
                subprocess.run(['xdotool', 'click', '6'],
                             capture_output=True, check=True, timeout=0.3)
            else:
                import pyautogui
                pyautogui.hscroll(-3)  # Negative for left

            angle = gesture_data.get('angle', 0.0)
            print(f"⬅️  Scroll left (head tilt left {angle:.1f}°)")
            return True

        except Exception as e:
            logging.error(f"Scroll left error: {e}")
            return False

    def scroll_right(self, gesture_data):
        """Execute scroll right action"""
        try:
            if self.mouse_backend == 'xdotool':
                # Use horizontal scroll or arrow key
                subprocess.run(['xdotool', 'click', '7'],
                             capture_output=True, check=True, timeout=0.3)
            else:
                import pyautogui
                pyautogui.hscroll(3)  # Positive for right

            angle = gesture_data.get('angle', 0.0)
            print(f"➡️  Scroll right (head tilt right {angle:.1f}°)")
            return True

        except Exception as e:
            logging.error(f"Scroll right error: {e}")
            return False

    def get_action_statistics(self):
        """Get statistics about executed actions"""
        total_actions = sum(self.action_stats.values())

        stats = {
            'total_actions': total_actions,
            'action_counts': {gesture_type.value: count for gesture_type, count in self.action_stats.items()},
            'drag_active': self.drag_active,
            'last_action_times': {gesture_type.value: timestamp for gesture_type, timestamp in self.last_action_time.items()}
        }

        return stats

    def reset_statistics(self):
        """Reset action statistics"""
        self.action_stats = {gesture_type: 0 for gesture_type in GestureType}
        self.last_action_time = {}
        print("📊 Action statistics reset")

    def is_drag_active(self):
        """Check if drag mode is currently active"""
        return self.drag_active

    def cancel_drag(self):
        """Cancel current drag operation"""
        if self.drag_active:
            try:
                if self.mouse_backend == 'xdotool':
                    subprocess.run(['xdotool', 'mouseup', '1'],
                                 capture_output=True, check=True, timeout=0.5)
                else:
                    import pyautogui
                    pyautogui.mouseUp()

                self.drag_active = False
                self.drag_start_pos = None
                print("🖱️  Drag cancelled")
                return True
            except Exception as e:
                logging.error(f"Error cancelling drag: {e}")
                return False
        return True
