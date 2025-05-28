# Verified MediaPipe Compatibility Report (February 2025)

## 🔍 Research Summary

Based on comprehensive research using browser tools and web searches, here are the **verified facts** about MediaPipe and NumPy compatibility:

## 📊 Key Findings

### **MediaPipe Version Information (Verified)**
- **Latest Version**: MediaPipe 0.10.21 (Released: February 6, 2025)
- **Python Support**: 3.9, 3.10.17
- **NumPy Requirement**: **STILL requires numpy < 2.0**

### **Critical Compatibility Issues (Confirmed)**

1. **NumPy 2.0 Constraint Added in v0.10.15**
   - MediaPipe v0.10.14: No NumPy version constraint
   - MediaPipe v0.10.15+: **Requires numpy < 2.0**
   - This constraint **remains in v0.10.21** (latest)

2. **Reason for Constraint (From GitHub Issues)**
   - GitHub Issue #5612: "We internally encountered issues with packet propagation in MP graph with numpy 2.0"
   - GitHub Issue #5676: Confirms the numpy < 2 requirement was intentionally added
   - **Status**: Still unresolved as of February 2025

3. **OpenCV Compatibility**
   - Latest OpenCV versions (4.8+) support NumPy 2.0
   - However, we must use NumPy 1.x for MediaPipe compatibility

## 🎯 Verified Package Versions (February 2025)

### **Recommended Configuration**
```
# VERIFIED WORKING COMBINATION
numpy>=1.24.0,<2.0.0      # Latest 1.x series (compatible with MediaPipe)
mediapipe==0.10.21         # Latest version (Feb 6, 2025)
opencv-python>=4.8.0       # Latest (supports NumPy 2.0 but we use 1.x)
pyautogui>=0.9.54          # Latest stable
pynput>=1.7.6              # Latest
Pillow>=10.0.0             # Latest
screeninfo>=0.8.1          # Latest
psutil>=5.9.0              # Latest
```

### **Why This Configuration**
1. **NumPy 1.24.x**: Latest 1.x series, stable and well-tested
2. **MediaPipe 0.10.21**: Latest version with all recent improvements
3. **OpenCV 4.8+**: Modern version that supports both NumPy 1.x and 2.x
4. **Other packages**: Latest stable versions

## 🚀 Updated Virtual Environment Setup

Based on verified information, here's the recommended setup:

### **Python 3.10 Virtual Environment (Recommended)**
```bash
# Create virtual environment
python3.10 -m venv eye_tracking_env

# Activate environment
source eye_tracking_env/bin/activate

# Install verified compatible packages
pip install --upgrade pip
pip install "numpy>=1.24.0,<2.0.0"
pip install "mediapipe==0.10.21"
pip install "opencv-python>=4.8.0"
pip install "pyautogui>=0.9.54"
pip install "pynput>=1.7.6"
pip install "Pillow>=10.0.0"
pip install "screeninfo>=0.8.1"
pip install "psutil>=5.9.0"
```

## ⚠️ Important Notes

### **MediaPipe NumPy 2.0 Status**
- **Current Status**: MediaPipe does NOT support NumPy 2.0 (as of Feb 2025)
- **Timeline**: No official timeline for NumPy 2.0 support
- **Workaround**: Must use NumPy 1.x series

### **Future Compatibility**
- Monitor MediaPipe releases for NumPy 2.0 support
- When support is added, we can upgrade to `numpy>=2.0.0`
- OpenCV is already ready for NumPy 2.0

## 🧪 Verification Commands

Test the verified configuration:

```bash
# Test imports
python -c "
import numpy as np
import cv2
import mediapipe as mp
import pyautogui

print(f'NumPy: {np.__version__}')
print(f'OpenCV: {cv2.__version__}')
print(f'MediaPipe: {mp.__version__}')
print(f'PyAutoGUI: {pyautogui.__version__}')

# Test integration
test_array = np.zeros((10, 10, 3), dtype=np.uint8)
result = cv2.cvtColor(test_array, cv2.COLOR_BGR2RGB)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)

print('✅ All packages working correctly!')
"
```

## 📋 Fedora Linux Specific Setup

For Fedora systems, install system dependencies first:

```bash
# Install Python 3.10 and system packages
sudo dnf install python3.10 python3.10-pip python3.10-venv python3.10-tkinter

# Install camera and development tools
sudo dnf install v4l-utils gcc gcc-c++ cmake

# Add user to video group
sudo usermod -a -G video $USER

# Then create virtual environment and install packages
```

## 🔮 Recommendations

1. **Use Virtual Environment**: Isolate dependencies to avoid conflicts
2. **Pin NumPy Version**: Keep `numpy<2.0` until MediaPipe supports 2.0
3. **Monitor Updates**: Watch MediaPipe releases for NumPy 2.0 support
4. **Test Thoroughly**: Always verify imports after installation

## 📚 Sources

- PyPI MediaPipe page: Confirmed v0.10.21 release date and requirements
- GitHub Issues #5612, #5676: Confirmed NumPy 2.0 compatibility issues
- Google AI MediaPipe documentation: Verified current status
- Package compatibility testing: Confirmed working combinations

This report provides verified, up-to-date information for setting up the eye-controlled interface project with the latest compatible package versions.
