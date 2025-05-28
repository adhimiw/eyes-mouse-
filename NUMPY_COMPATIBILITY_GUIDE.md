# NumPy Compatibility Fix Guide for Fedora Linux

## Problem Description

The eye-controlled interface system fails on Fedora Linux due to NumPy 2.x compatibility issues. Packages like OpenCV, MediaPipe, and PyAutoGUI were compiled against NumPy 1.x and cannot work with NumPy 2.x, causing "_ARRAY_API not found" errors.

## Quick Fix (Recommended)

Run the automated fix script:

```bash
chmod +x fix_numpy_compatibility.sh
./fix_numpy_compatibility.sh
```

## Manual Fix Steps

### 1. Check Current NumPy Version

```bash
python3 -c "import numpy; print('NumPy version:', numpy.__version__)"
```

If the version is 2.x (e.g., 2.2.6), you need to downgrade.

### 2. Remove Conflicting Packages

```bash
# Remove system packages that might conflict
sudo dnf remove -y python3-opencv python3-numpy python3-scipy

# Remove pip packages
python3 -m pip uninstall -y opencv-python opencv-contrib-python mediapipe pyautogui numpy scipy
```

### 3. Install Compatible NumPy Version

```bash
# Install NumPy 1.x (compatible version)
python3 -m pip install --user "numpy>=1.21.0,<2.0.0"
```

### 4. Install Packages with Compatible Versions

```bash
# Install packages in specific order
python3 -m pip install --user --force-reinstall "numpy>=1.21.0,<2.0.0"
python3 -m pip install --user --force-reinstall "opencv-python==4.8.1.78"
python3 -m pip install --user --force-reinstall "mediapipe==0.10.7"
python3 -m pip install --user --force-reinstall "pyautogui==0.9.54"
python3 -m pip install --user --force-reinstall "Pillow>=9.0.0,<11.0.0"
python3 -m pip install --user --force-reinstall "psutil>=5.8.0"
python3 -m pip install --user --force-reinstall "pynput>=1.7.0"
python3 -m pip install --user --force-reinstall "screeninfo>=0.8.0"
```

### 5. Verify Installation

```bash
python3 -c "
import numpy, cv2, mediapipe, pyautogui
print('✅ NumPy version:', numpy.__version__)
print('✅ OpenCV version:', cv2.__version__)
print('✅ MediaPipe version:', mediapipe.__version__)
print('✅ PyAutoGUI version:', pyautogui.__version__)
print('🎉 All packages working!')
"
```

## Alternative Solutions

### Option 1: Use Virtual Environment

Create an isolated environment with compatible versions:

```bash
# Install virtualenv
python3 -m pip install --user virtualenv

# Create virtual environment
python3 -m virtualenv eye_tracking_env

# Activate environment
source eye_tracking_env/bin/activate

# Install compatible packages
pip install "numpy>=1.21.0,<2.0.0"
pip install "opencv-python==4.8.1.78"
pip install "mediapipe==0.10.7"
pip install "pyautogui==0.9.54"
pip install "Pillow>=9.0.0,<11.0.0"
pip install "psutil>=5.8.0"
pip install "pynput>=1.7.0"
pip install "screeninfo>=0.8.0"

# Run the application
python main.py

# Deactivate when done
deactivate
```

### Option 2: Use Conda Environment

```bash
# Install conda/miniconda if not available
# Then create environment with specific NumPy version

conda create -n eye_tracking python=3.11 "numpy>=1.21.0,<2.0.0"
conda activate eye_tracking

# Install packages
pip install "opencv-python==4.8.1.78"
pip install "mediapipe==0.10.7"
pip install "pyautogui==0.9.54"
pip install "Pillow>=9.0.0,<11.0.0"
pip install "psutil>=5.8.0"
pip install "pynput>=1.7.0"
pip install "screeninfo>=0.8.0"

# Run application
python main.py
```

## Understanding the Issue

### Why This Happens

1. **NumPy 2.0 Breaking Changes**: NumPy 2.0 introduced significant API changes
2. **Binary Compatibility**: Packages compiled against NumPy 1.x cannot load with NumPy 2.x
3. **C Extension Modules**: OpenCV and MediaPipe use C extensions that depend on NumPy's C API
4. **Fedora's Latest Packages**: Fedora often ships with the latest versions, including NumPy 2.x

### Compatible Version Matrix

| Package | Compatible NumPy | Recommended Version |
|---------|------------------|-------------------|
| opencv-python | 1.21.0 - 1.26.x | 4.8.1.78 |
| mediapipe | 1.21.0 - 1.26.x | 0.10.7 |
| pyautogui | 1.19.0 - 1.26.x | 0.9.54 |

## Troubleshooting

### Error: "RuntimeError: module compiled against API version 0x10 but this version of numpy is 0x11"

**Solution**: Reinstall packages with compatible NumPy version:
```bash
python3 -m pip install --user --force-reinstall "numpy<2.0.0" opencv-python mediapipe
```

### Error: "ImportError: numpy.core.multiarray failed to import"

**Solution**: Complete package reinstallation:
```bash
python3 -m pip uninstall -y numpy opencv-python mediapipe
python3 -m pip install --user "numpy>=1.21.0,<2.0.0"
python3 -m pip install --user opencv-python mediapipe
```

### Error: "AttributeError: module 'numpy' has no attribute '_ARRAY_API'"

**Solution**: This is the classic NumPy 2.x compatibility issue:
```bash
# Run the fix script
./fix_numpy_compatibility.sh
```

### System Packages Interfering

If system packages conflict:
```bash
# Remove system packages
sudo dnf remove python3-opencv python3-numpy

# Use only pip packages
python3 -m pip install --user "numpy<2.0.0" opencv-python
```

## Prevention

### Pin NumPy Version in Requirements

Create a `requirements_compatible.txt`:
```
numpy>=1.21.0,<2.0.0
opencv-python==4.8.1.78
mediapipe==0.10.7
pyautogui==0.9.54
Pillow>=9.0.0,<11.0.0
psutil>=5.8.0
pynput>=1.7.0
screeninfo>=0.8.0
```

Install with:
```bash
python3 -m pip install --user -r requirements_compatible.txt
```

### Use Virtual Environments

Always use virtual environments for projects with specific version requirements:
```bash
python3 -m venv eye_tracking_env
source eye_tracking_env/bin/activate
pip install -r requirements_compatible.txt
```

## Testing the Fix

After applying the fix, test the installation:

```bash
# Run system tests
python3 test_system.py

# Test simple eye mouse
python3 simple_eye_mouse.py

# Test full application
python3 main.py
```

Expected output should show all modules importing successfully without NumPy compatibility errors.

## Long-term Considerations

1. **Future Updates**: Be careful when updating NumPy or related packages
2. **Virtual Environments**: Consider using virtual environments for isolation
3. **Package Monitoring**: Monitor for NumPy 2.x compatible versions of OpenCV and MediaPipe
4. **Alternative Packages**: Consider alternatives if compatibility issues persist

The fix script handles all these steps automatically and ensures your eye-controlled interface works properly on Fedora Linux.
