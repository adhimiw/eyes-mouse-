#!/usr/bin/env python3
"""
Code Comparison Analyzer
Compare working vs non-working eye tracking implementations
"""

import os
import re
import difflib
from typing import Dict, List, Tuple

class CodeAnalyzer:
    def __init__(self):
        self.working_files = ['simple_eye_mouse.py']
        self.broken_files = ['hybrid_eye_gesture_controller.py', 'main_optimized.py']
        
    def extract_eye_tracking_code(self, filepath: str) -> Dict[str, str]:
        """Extract eye tracking related code sections"""
        if not os.path.exists(filepath):
            return {'error': f'File not found: {filepath}'}
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        sections = {}
        
        # Extract eye position/iris detection methods
        iris_pattern = r'(def.*(?:iris|eye).*?(?=def|\Z))'
        iris_matches = re.findall(iris_pattern, content, re.DOTALL | re.IGNORECASE)
        sections['iris_detection'] = iris_matches
        
        # Extract cursor movement code
        cursor_pattern = r'(.*pyautogui\.moveTo.*)'
        cursor_matches = re.findall(cursor_pattern, content)
        sections['cursor_movement'] = cursor_matches
        
        # Extract landmark processing
        landmark_pattern = r'(.*landmarks\[.*?\].*)'
        landmark_matches = re.findall(landmark_pattern, content)
        sections['landmark_processing'] = landmark_matches
        
        # Extract coordinate conversion
        coord_pattern = r'(.*screen.*[xy].*=.*)'
        coord_matches = re.findall(coord_pattern, content)
        sections['coordinate_conversion'] = coord_matches
        
        return sections

    def compare_implementations(self):
        """Compare working vs broken implementations"""
        print("🔍 Analyzing Eye Tracking Implementations...")
        print("=" * 60)
        
        # Analyze working implementation
        print("\n✅ WORKING IMPLEMENTATION (simple_eye_mouse.py):")
        working_code = self.extract_eye_tracking_code('simple_eye_mouse.py')
        
        if 'error' in working_code:
            print(f"❌ {working_code['error']}")
            return
        
        print("\n📍 Iris Detection Method:")
        for method in working_code['iris_detection']:
            print("```python")
            print(method[:500] + "..." if len(method) > 500 else method)
            print("```")
        
        print("\n📍 Cursor Movement:")
        for movement in working_code['cursor_movement']:
            print(f"  {movement.strip()}")
        
        print("\n📍 Landmark Processing:")
        for landmark in working_code['landmark_processing'][:5]:  # Show first 5
            print(f"  {landmark.strip()}")
        
        print("\n📍 Coordinate Conversion:")
        for coord in working_code['coordinate_conversion']:
            print(f"  {coord.strip()}")
        
        # Analyze broken implementations
        for broken_file in self.broken_files:
            print(f"\n❌ POTENTIALLY BROKEN IMPLEMENTATION ({broken_file}):")
            broken_code = self.extract_eye_tracking_code(broken_file)
            
            if 'error' in broken_code:
                print(f"❌ {broken_code['error']}")
                continue
            
            print("\n📍 Cursor Movement:")
            for movement in broken_code['cursor_movement']:
                print(f"  {movement.strip()}")
            
            print("\n📍 Coordinate Conversion:")
            for coord in broken_code['coordinate_conversion']:
                print(f"  {coord.strip()}")
            
            # Compare differences
            print(f"\n🔄 DIFFERENCES from working version:")
            self.show_differences(working_code, broken_code)

    def show_differences(self, working: Dict, broken: Dict):
        """Show key differences between implementations"""
        
        # Compare cursor movement
        working_cursor = set(working.get('cursor_movement', []))
        broken_cursor = set(broken.get('cursor_movement', []))
        
        if working_cursor != broken_cursor:
            print("  📍 Cursor Movement Differences:")
            for line in working_cursor - broken_cursor:
                print(f"    WORKING HAS: {line.strip()}")
            for line in broken_cursor - working_cursor:
                print(f"    BROKEN HAS:  {line.strip()}")
        
        # Compare coordinate conversion
        working_coords = set(working.get('coordinate_conversion', []))
        broken_coords = set(broken.get('coordinate_conversion', []))
        
        if working_coords != broken_coords:
            print("  📍 Coordinate Conversion Differences:")
            for line in working_coords - broken_coords:
                print(f"    WORKING HAS: {line.strip()}")
            for line in broken_coords - working_coords:
                print(f"    BROKEN HAS:  {line.strip()}")

    def extract_key_functions(self, filepath: str) -> Dict[str, str]:
        """Extract key eye tracking functions"""
        if not os.path.exists(filepath):
            return {}
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        functions = {}
        
        # Find function definitions
        func_pattern = r'def\s+(\w*(?:eye|iris|cursor|move|track)\w*)\s*\([^)]*\):(.*?)(?=\n\s*def|\n\s*class|\Z)'
        matches = re.findall(func_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for func_name, func_body in matches:
            functions[func_name] = func_body.strip()
        
        return functions

    def detailed_function_comparison(self):
        """Compare key functions in detail"""
        print("\n" + "=" * 60)
        print("🔬 DETAILED FUNCTION COMPARISON")
        print("=" * 60)
        
        working_funcs = self.extract_key_functions('simple_eye_mouse.py')
        
        print(f"\n✅ WORKING FUNCTIONS in simple_eye_mouse.py:")
        for func_name, func_body in working_funcs.items():
            print(f"\n📍 {func_name}():")
            print("```python")
            print(func_body[:300] + "..." if len(func_body) > 300 else func_body)
            print("```")
        
        for broken_file in self.broken_files:
            broken_funcs = self.extract_key_functions(broken_file)
            
            print(f"\n❌ FUNCTIONS in {broken_file}:")
            for func_name, func_body in broken_funcs.items():
                print(f"\n📍 {func_name}():")
                print("```python")
                print(func_body[:300] + "..." if len(func_body) > 300 else func_body)
                print("```")
                
                # Compare with working version
                if func_name in working_funcs:
                    print(f"\n🔄 COMPARISON with working version:")
                    working_lines = working_funcs[func_name].split('\n')
                    broken_lines = func_body.split('\n')
                    
                    diff = list(difflib.unified_diff(
                        working_lines, broken_lines,
                        fromfile=f'working/{func_name}',
                        tofile=f'broken/{func_name}',
                        lineterm=''
                    ))
                    
                    if diff:
                        for line in diff[:10]:  # Show first 10 diff lines
                            print(f"    {line}")
                    else:
                        print("    ✅ Functions are identical")

def main():
    """Main analysis function"""
    print("🔬 CODE COMPARISON ANALYZER")
    print("Analyzing eye tracking implementations to find bugs")
    
    analyzer = CodeAnalyzer()
    
    # Basic comparison
    analyzer.compare_implementations()
    
    # Detailed function comparison
    analyzer.detailed_function_comparison()
    
    print("\n" + "=" * 60)
    print("📋 ANALYSIS COMPLETE")
    print("=" * 60)
    print("\n💡 Next Steps:")
    print("1. Run the bug catcher: python bug_catcher_eye_tracking.py")
    print("2. Compare the working simple_eye_mouse.py with broken implementations")
    print("3. Look for differences in landmark processing and coordinate conversion")
    print("4. Test each implementation individually")

if __name__ == "__main__":
    main()
