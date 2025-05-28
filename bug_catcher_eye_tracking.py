#!/usr/bin/env python3
"""
Comprehensive Bug Catcher for Eye Tracking Issues
This will help me see exactly what's happening in each implementation
"""

import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np
import json
import traceback
from collections import deque

# Disable PyAutoGUI failsafe
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.001

class EyeTrackingBugCatcher:
    def __init__(self):
        print("🐛 Eye Tracking Bug Catcher Initialized")
        print("   This will help debug eye tracking issues")
        
        # MediaPipe setup
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Screen info
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Debug data collection
        self.debug_data = {
            'face_detected': [],
            'iris_positions': [],
            'cursor_movements': [],
            'errors': [],
            'frame_times': []
        }
        
        # Settings
        self.sensitivity = 1.2
        self.frame_count = 0
        self.start_time = time.time()
        
        print(f"   Screen: {self.screen_w}x{self.screen_h}")
        print(f"   Camera: {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

    def log_debug_info(self, event_type, data):
        """Log debug information with timestamp"""
        timestamp = time.time() - self.start_time
        self.debug_data[event_type].append({
            'timestamp': timestamp,
            'frame': self.frame_count,
            'data': data
        })

    def analyze_landmarks(self, landmarks):
        """Analyze all available landmarks and their positions"""
        analysis = {
            'total_landmarks': len(landmarks),
            'iris_landmarks': {},
            'eye_landmarks': {},
            'face_bounds': {}
        }
        
        # Check iris landmarks
        iris_ids = [468, 469, 470, 471, 472, 473, 474, 475, 476, 477]
        for iris_id in iris_ids:
            if iris_id < len(landmarks):
                landmark = landmarks[iris_id]
                analysis['iris_landmarks'][iris_id] = {
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z
                }
        
        # Check eye outline landmarks
        eye_ids = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        for eye_id in eye_ids:
            if eye_id < len(landmarks):
                landmark = landmarks[eye_id]
                analysis['eye_landmarks'][eye_id] = {
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z
                }
        
        # Face bounds
        if landmarks:
            x_coords = [lm.x for lm in landmarks]
            y_coords = [lm.y for lm in landmarks]
            analysis['face_bounds'] = {
                'min_x': min(x_coords),
                'max_x': max(x_coords),
                'min_y': min(y_coords),
                'max_y': max(y_coords),
                'width': max(x_coords) - min(x_coords),
                'height': max(y_coords) - min(y_coords)
            }
        
        return analysis

    def test_simple_eye_mouse_method(self, landmarks):
        """Test the exact method from simple_eye_mouse.py"""
        try:
            if len(landmarks) > 475:
                iris_center = landmarks[475]  # Right iris center
                
                # Convert to screen coordinates (EXACT same as simple_eye_mouse.py)
                raw_x = iris_center.x * self.screen_w * self.sensitivity
                raw_y = iris_center.y * self.screen_h * self.sensitivity
                
                # Clamp to screen bounds
                screen_x = max(0, min(self.screen_w - 1, int(raw_x)))
                screen_y = max(0, min(self.screen_h - 1, int(raw_y)))
                
                return {
                    'success': True,
                    'iris_raw': {'x': iris_center.x, 'y': iris_center.y, 'z': iris_center.z},
                    'screen_raw': {'x': raw_x, 'y': raw_y},
                    'screen_final': {'x': screen_x, 'y': screen_y},
                    'method': 'simple_eye_mouse_exact'
                }
            else:
                return {
                    'success': False,
                    'error': f'Not enough landmarks: {len(landmarks)}',
                    'method': 'simple_eye_mouse_exact'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'method': 'simple_eye_mouse_exact'
            }

    def test_alternative_methods(self, landmarks):
        """Test alternative eye tracking methods"""
        methods = {}
        
        # Method 1: Average of both iris centers
        try:
            if len(landmarks) > 475:
                left_iris = landmarks[468]  # Left iris center
                right_iris = landmarks[475]  # Right iris center
                
                avg_x = (left_iris.x + right_iris.x) / 2
                avg_y = (left_iris.y + right_iris.y) / 2
                
                screen_x = int(avg_x * self.screen_w * self.sensitivity)
                screen_y = int(avg_y * self.screen_h * self.sensitivity)
                
                methods['average_iris'] = {
                    'success': True,
                    'screen_pos': {'x': screen_x, 'y': screen_y}
                }
        except Exception as e:
            methods['average_iris'] = {'success': False, 'error': str(e)}
        
        # Method 2: Eye center calculation
        try:
            # Use eye corner landmarks
            left_corner = landmarks[33]   # Left eye left corner
            right_corner = landmarks[133] # Left eye right corner
            
            eye_center_x = (left_corner.x + right_corner.x) / 2
            eye_center_y = (left_corner.y + right_corner.y) / 2
            
            screen_x = int(eye_center_x * self.screen_w * self.sensitivity)
            screen_y = int(eye_center_y * self.screen_h * self.sensitivity)
            
            methods['eye_center'] = {
                'success': True,
                'screen_pos': {'x': screen_x, 'y': screen_y}
            }
        except Exception as e:
            methods['eye_center'] = {'success': False, 'error': str(e)}
        
        return methods

    def draw_comprehensive_debug(self, frame, landmarks, analysis, test_results):
        """Draw comprehensive debug information"""
        h, w, _ = frame.shape
        
        # Performance info
        current_time = time.time()
        elapsed = current_time - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        # Current cursor position
        cursor_x, cursor_y = pyautogui.position()
        
        # Basic info
        info_lines = [
            f"FPS: {fps:.1f}",
            f"Frame: {self.frame_count}",
            f"Cursor: ({cursor_x}, {cursor_y})",
            f"Landmarks: {analysis['total_landmarks']}",
            f"Sensitivity: {self.sensitivity:.1f}"
        ]
        
        # Draw basic info
        for i, line in enumerate(info_lines):
            cv2.putText(frame, line, (10, 30 + i * 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Draw iris landmarks
        for iris_id, pos in analysis['iris_landmarks'].items():
            x = int(pos['x'] * w)
            y = int(pos['y'] * h)
            color = (0, 255, 255) if iris_id == 475 else (255, 255, 0)
            cv2.circle(frame, (x, y), 3, color, -1)
            cv2.putText(frame, str(iris_id), (x + 5, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
        
        # Draw test results
        y_offset = 150
        if test_results['success']:
            result_lines = [
                f"Method: {test_results['method']}",
                f"Iris Raw: ({test_results['iris_raw']['x']:.3f}, {test_results['iris_raw']['y']:.3f})",
                f"Screen Raw: ({test_results['screen_raw']['x']:.1f}, {test_results['screen_raw']['y']:.1f})",
                f"Screen Final: ({test_results['screen_final']['x']}, {test_results['screen_final']['y']})"
            ]
            color = (0, 255, 0)
        else:
            result_lines = [
                f"ERROR: {test_results['error']}"
            ]
            color = (0, 0, 255)
        
        for i, line in enumerate(result_lines):
            cv2.putText(frame, line, (10, y_offset + i * 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        # Draw face bounds
        if 'face_bounds' in analysis and analysis['face_bounds']:
            bounds = analysis['face_bounds']
            x1 = int(bounds['min_x'] * w)
            y1 = int(bounds['min_y'] * h)
            x2 = int(bounds['max_x'] * w)
            y2 = int(bounds['max_y'] * h)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        return frame

    def run_comprehensive_test(self):
        """Run comprehensive eye tracking test"""
        print("\n🔍 Starting Comprehensive Eye Tracking Debug...")
        print("   This will analyze every aspect of eye tracking")
        print("   Press 'q' to quit, 's' to save debug data")
        
        try:
            while True:
                frame_start = time.time()
                
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                # Flip frame
                frame = cv2.flip(frame, 1)
                
                # Convert to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process with MediaPipe
                results = self.face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    
                    # Log face detection
                    self.log_debug_info('face_detected', True)
                    
                    # Analyze landmarks
                    analysis = self.analyze_landmarks(landmarks)
                    
                    # Test simple_eye_mouse method
                    test_results = self.test_simple_eye_mouse_method(landmarks)
                    
                    # Test alternative methods
                    alt_methods = self.test_alternative_methods(landmarks)
                    
                    # Log iris position
                    if test_results['success']:
                        self.log_debug_info('iris_positions', test_results['iris_raw'])
                        
                        # Actually move cursor for testing
                        screen_x = test_results['screen_final']['x']
                        screen_y = test_results['screen_final']['y']
                        pyautogui.moveTo(screen_x, screen_y)
                        
                        self.log_debug_info('cursor_movements', {'x': screen_x, 'y': screen_y})
                    else:
                        self.log_debug_info('errors', test_results)
                    
                    # Draw debug info
                    frame = self.draw_comprehensive_debug(frame, landmarks, analysis, test_results)
                    
                    # Draw landmarks
                    self.mp_drawing.draw_landmarks(
                        frame, results.multi_face_landmarks[0], 
                        self.mp_face_mesh.FACEMESH_IRISES,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                    )
                
                else:
                    # No face detected
                    self.log_debug_info('face_detected', False)
                    cv2.putText(frame, "NO FACE DETECTED", (10, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Log frame time
                frame_time = time.time() - frame_start
                self.log_debug_info('frame_times', frame_time * 1000)  # ms
                
                # Display
                cv2.imshow('Eye Tracking Bug Catcher', frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self.save_debug_data()
                elif key == ord('+'):
                    self.sensitivity = min(3.0, self.sensitivity + 0.1)
                    print(f"Sensitivity: {self.sensitivity:.1f}")
                elif key == ord('-'):
                    self.sensitivity = max(0.1, self.sensitivity - 0.1)
                    print(f"Sensitivity: {self.sensitivity:.1f}")
                
                self.frame_count += 1
        
        except KeyboardInterrupt:
            print("\n⏹️ Test stopped by user")
        finally:
            self.cleanup()

    def save_debug_data(self):
        """Save debug data to file"""
        filename = f"eye_tracking_debug_{int(time.time())}.json"
        
        # Calculate statistics
        stats = {
            'total_frames': self.frame_count,
            'runtime': time.time() - self.start_time,
            'face_detection_rate': len([x for x in self.debug_data['face_detected'] if x['data']]) / len(self.debug_data['face_detected']) if self.debug_data['face_detected'] else 0,
            'avg_frame_time': np.mean([x['data'] for x in self.debug_data['frame_times']]) if self.debug_data['frame_times'] else 0,
            'error_count': len(self.debug_data['errors'])
        }
        
        debug_export = {
            'stats': stats,
            'debug_data': self.debug_data,
            'settings': {
                'sensitivity': self.sensitivity,
                'screen_size': {'w': self.screen_w, 'h': self.screen_h}
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(debug_export, f, indent=2)
        
        print(f"📊 Debug data saved to {filename}")
        print(f"   Face detection rate: {stats['face_detection_rate']:.1%}")
        print(f"   Average frame time: {stats['avg_frame_time']:.1f}ms")
        print(f"   Error count: {stats['error_count']}")

    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
        # Print final summary
        print("\n📊 Bug Catcher Summary:")
        print(f"   Total frames: {self.frame_count}")
        print(f"   Runtime: {time.time() - self.start_time:.1f}s")
        print(f"   Face detections: {len([x for x in self.debug_data['face_detected'] if x['data']])}")
        print(f"   Errors logged: {len(self.debug_data['errors'])}")

def main():
    """Main function"""
    print("=" * 60)
    print("    🐛 EYE TRACKING BUG CATCHER")
    print("    Comprehensive Debug & Analysis Tool")
    print("=" * 60)
    
    try:
        bug_catcher = EyeTrackingBugCatcher()
        bug_catcher.run_comprehensive_test()
    except Exception as e:
        print(f"❌ Bug catcher failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
