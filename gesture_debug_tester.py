#!/usr/bin/env python3
"""
Comprehensive Gesture Recognition Debug and Test System
Tests each component individually and provides detailed debugging information
"""

import cv2
import mediapipe as mp
import pyautogui
import math
import numpy as np
import time
import json
from enum import IntEnum
from collections import deque

# Import our working gesture controller
from gesture_controller_working import Gest, HLabel, HandRecog, Controller, GestureController

class GestureDebugger:
    """Comprehensive debugging system for gesture recognition"""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Debug tracking
        self.debug_mode = True
        self.show_landmarks = True
        self.show_finger_states = True
        self.show_distances = True
        self.frame_count = 0
        self.start_time = time.time()
        
        print("🔍 Gesture Debug System Initialized")
        print("   Press 'd' to toggle debug info")
        print("   Press 'l' to toggle landmarks")
        print("   Press 'f' to toggle finger states")
        print("   Press 'q' to quit")

    def draw_debug_info(self, image, hand_landmarks, hand_recog):
        """Draw comprehensive debug information"""
        if not self.debug_mode:
            return image
        
        h, w, _ = image.shape
        
        # Performance info
        current_time = time.time()
        elapsed = current_time - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        debug_lines = [
            f"FPS: {fps:.1f}",
            f"Frame: {self.frame_count}",
            f"Hand Detected: {'YES' if hand_landmarks else 'NO'}"
        ]
        
        if hand_landmarks and hand_recog.hand_result:
            # Finger state info
            finger_binary = format(hand_recog.finger, '05b')
            debug_lines.extend([
                f"Finger State: {hand_recog.finger} ({finger_binary})",
                f"Current Gesture: {Gest(hand_recog.ori_gesture).name}",
                f"Frame Count: {hand_recog.frame_count}"
            ])
            
            # Distance calculations for key gestures
            if self.show_distances:
                try:
                    thumb_index_dist = hand_recog.get_dist([4, 8])
                    index_middle_dist = hand_recog.get_dist([8, 12])
                    debug_lines.extend([
                        f"Thumb-Index: {thumb_index_dist:.3f}",
                        f"Index-Middle: {index_middle_dist:.3f}"
                    ])
                except:
                    pass
        
        # Draw debug info
        for i, line in enumerate(debug_lines):
            cv2.putText(image, line, (10, 30 + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Draw finger state visualization
        if self.show_finger_states and hand_landmarks and hand_recog.hand_result:
            self.draw_finger_states(image, hand_recog)
        
        return image

    def draw_finger_states(self, image, hand_recog):
        """Draw finger state visualization"""
        h, w, _ = image.shape
        
        # Finger names
        finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
        
        # Draw finger state boxes
        box_width = 80
        box_height = 30
        start_x = w - 450
        start_y = 50
        
        for i, name in enumerate(finger_names):
            x = start_x + i * (box_width + 10)
            y = start_y
            
            # Check if finger is extended
            finger_extended = (hand_recog.finger >> (4-i)) & 1
            color = (0, 255, 0) if finger_extended else (0, 0, 255)
            
            # Draw box
            cv2.rectangle(image, (x, y), (x + box_width, y + box_height), color, 2)
            
            # Draw text
            cv2.putText(image, name, (x + 5, y + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    def test_individual_gestures(self):
        """Test individual gesture recognition"""
        print("\n🧪 Testing Individual Gestures...")
        
        handmajor = HandRecog(HLabel.MAJOR)
        
        with self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        ) as hands:
            
            gesture_counts = {}
            
            while True:
                success, image = self.cap.read()
                if not success:
                    continue
                
                # Process image
                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = hands.process(image)
                
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    handmajor.update_hand_result(hand_landmarks)
                    handmajor.set_finger_state()
                    gesture = handmajor.get_gesture()
                    
                    # Count gestures
                    gesture_name = Gest(gesture).name
                    gesture_counts[gesture_name] = gesture_counts.get(gesture_name, 0) + 1
                    
                    # Draw landmarks if enabled
                    if self.show_landmarks:
                        self.mp_drawing.draw_landmarks(
                            image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Draw debug info
                    image = self.draw_debug_info(image, hand_landmarks, handmajor)
                    
                    # Draw gesture statistics
                    y_offset = 200
                    for i, (gest_name, count) in enumerate(gesture_counts.items()):
                        cv2.putText(image, f"{gest_name}: {count}", 
                                   (10, y_offset + i * 25), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                else:
                    # No hand detected
                    cv2.putText(image, "No hand detected", (10, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Display
                cv2.imshow('Gesture Debug Test', image)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('d'):
                    self.debug_mode = not self.debug_mode
                    print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
                elif key == ord('l'):
                    self.show_landmarks = not self.show_landmarks
                    print(f"Landmarks: {'ON' if self.show_landmarks else 'OFF'}")
                elif key == ord('f'):
                    self.show_finger_states = not self.show_finger_states
                    print(f"Finger states: {'ON' if self.show_finger_states else 'OFF'}")
                elif key == ord('c'):
                    gesture_counts.clear()
                    print("Gesture counts cleared")
                
                self.frame_count += 1

    def test_performance_benchmark(self):
        """Run performance benchmark"""
        print("\n⚡ Running Performance Benchmark...")
        
        frame_times = []
        gesture_times = []
        
        handmajor = HandRecog(HLabel.MAJOR)
        
        with self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        ) as hands:
            
            test_frames = 100
            processed_frames = 0
            
            while processed_frames < test_frames:
                frame_start = time.time()
                
                success, image = self.cap.read()
                if not success:
                    continue
                
                # Process image
                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                
                gesture_start = time.time()
                results = hands.process(image)
                
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    handmajor.update_hand_result(hand_landmarks)
                    handmajor.set_finger_state()
                    gesture = handmajor.get_gesture()
                
                gesture_end = time.time()
                gesture_times.append((gesture_end - gesture_start) * 1000)  # ms
                
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                # Draw progress
                progress = (processed_frames / test_frames) * 100
                cv2.putText(image, f"Benchmark Progress: {progress:.1f}%", 
                           (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow('Performance Benchmark', image)
                cv2.waitKey(1)
                
                frame_end = time.time()
                frame_times.append((frame_end - frame_start) * 1000)  # ms
                
                processed_frames += 1
        
        # Calculate statistics
        avg_frame_time = np.mean(frame_times)
        avg_gesture_time = np.mean(gesture_times)
        avg_fps = 1000 / avg_frame_time
        
        print(f"\n📊 Performance Results:")
        print(f"   Frames processed: {test_frames}")
        print(f"   Average frame time: {avg_frame_time:.2f}ms")
        print(f"   Average gesture time: {avg_gesture_time:.2f}ms")
        print(f"   Average FPS: {avg_fps:.1f}")
        print(f"   Min frame time: {min(frame_times):.2f}ms")
        print(f"   Max frame time: {max(frame_times):.2f}ms")

    def test_gesture_accuracy(self):
        """Test gesture recognition accuracy"""
        print("\n🎯 Testing Gesture Accuracy...")
        print("   Perform each gesture when prompted")
        
        test_gestures = [
            (Gest.PALM, "Open palm"),
            (Gest.FIST, "Closed fist"),
            (Gest.INDEX, "Index finger up"),
            (Gest.V_GEST, "V-gesture (peace sign with spread fingers)"),
            (Gest.PINCH_MAJOR, "Pinch gesture (thumb and index close)")
        ]
        
        handmajor = HandRecog(HLabel.MAJOR)
        
        with self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        ) as hands:
            
            for target_gesture, description in test_gestures:
                print(f"\n👉 Show: {description}")
                print("   Press SPACE when ready, ESC to skip")
                
                # Wait for user to get ready
                while True:
                    success, image = self.cap.read()
                    if not success:
                        continue
                    
                    image = cv2.flip(image, 1)
                    cv2.putText(image, f"Show: {description}", 
                               (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(image, "Press SPACE when ready", 
                               (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                    
                    cv2.imshow('Gesture Accuracy Test', image)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord(' '):
                        break
                    elif key == 27:  # ESC
                        return
                
                # Test gesture recognition for 3 seconds
                correct_detections = 0
                total_detections = 0
                test_start = time.time()
                
                while time.time() - test_start < 3.0:
                    success, image = self.cap.read()
                    if not success:
                        continue
                    
                    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                    image.flags.writeable = False
                    results = hands.process(image)
                    
                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    
                    if results.multi_hand_landmarks:
                        hand_landmarks = results.multi_hand_landmarks[0]
                        handmajor.update_hand_result(hand_landmarks)
                        handmajor.set_finger_state()
                        detected_gesture = handmajor.get_gesture()
                        
                        total_detections += 1
                        if detected_gesture == target_gesture:
                            correct_detections += 1
                        
                        # Draw feedback
                        gesture_name = Gest(detected_gesture).name
                        color = (0, 255, 0) if detected_gesture == target_gesture else (0, 0, 255)
                        cv2.putText(image, f"Detected: {gesture_name}", 
                                   (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                        
                        # Draw landmarks
                        self.mp_drawing.draw_landmarks(
                            image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Show countdown
                    remaining = 3.0 - (time.time() - test_start)
                    cv2.putText(image, f"Time: {remaining:.1f}s", 
                               (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                    
                    cv2.imshow('Gesture Accuracy Test', image)
                    cv2.waitKey(1)
                
                # Calculate accuracy
                accuracy = (correct_detections / total_detections * 100) if total_detections > 0 else 0
                print(f"   Accuracy: {accuracy:.1f}% ({correct_detections}/{total_detections})")

    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

def main():
    """Main debug menu"""
    debugger = GestureDebugger()
    
    try:
        while True:
            print("\n" + "="*60)
            print("    🔍 GESTURE RECOGNITION DEBUG SYSTEM")
            print("="*60)
            print("\n📋 Available Tests:")
            print("1. 🧪 Individual Gesture Test (Real-time debug)")
            print("2. ⚡ Performance Benchmark")
            print("3. 🎯 Gesture Accuracy Test")
            print("4. 🚀 Run Full Gesture Controller")
            print("5. ❌ Exit")
            
            choice = input("\n🎯 Select test (1-5): ").strip()
            
            if choice == '1':
                debugger.test_individual_gestures()
            elif choice == '2':
                debugger.test_performance_benchmark()
            elif choice == '3':
                debugger.test_gesture_accuracy()
            elif choice == '4':
                print("\n🚀 Starting Full Gesture Controller...")
                controller = GestureController()
                controller.start()
                controller.cleanup()
            elif choice == '5':
                break
            else:
                print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
    finally:
        debugger.cleanup()

if __name__ == "__main__":
    main()
