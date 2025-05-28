# Fedora Linux Installation Guide

## Quick Installation (Recommended)

Run the automated installation script:

```bash
# Make the script executable and run it
chmod +x install_fedora.sh
./install_fedora.sh
```

## Manual Installation

If you prefer to install manually or the script fails:

### 1. Install System Dependencies

```bash
# Update system
sudo dnf update -y

# Install Python and pip
sudo dnf install -y python3 python3-pip python3-devel python3-tkinter

# Install OpenCV and camera dependencies
sudo dnf install -y \
    opencv-devel \
    opencv-python3 \
    v4l-utils \
    cheese \
    guvcview

# Install development tools
sudo dnf install -y gcc gcc-c++ cmake make pkg-config

# Add user to video group for camera access
sudo usermod -a -G video $USER
```

### 2. Install Python Packages

```bash
# Upgrade pip
python3 -m pip install --user --upgrade pip

# Install required packages
python3 -m pip install --user numpy==1.24.3
python3 -m pip install --user opencv-python==4.8.1.78
python3 -m pip install --user mediapipe==0.10.7
python3 -m pip install --user pyautogui==0.9.54
python3 -m pip install --user Pillow==10.0.1
python3 -m pip install --user psutil==5.9.6
python3 -m pip install --user pynput==1.7.6
python3 -m pip install --user screeninfo==0.8.1
```

### 3. Alternative Package Installation

If pip installation fails, try using dnf:

```bash
# Install available packages via dnf
sudo dnf install -y \
    python3-opencv \
    python3-numpy \
    python3-pillow \
    python3-psutil

# Then install remaining packages via pip
python3 -m pip install --user mediapipe pyautogui pynput screeninfo
```

### 4. Set Up Camera Permissions

```bash
# Create udev rule for camera access
echo 'SUBSYSTEM=="video4linux", GROUP="video", MODE="0664"' | sudo tee /etc/udev/rules.d/99-camera-permissions.rules

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 5. Test Installation

```bash
# Test camera access
ls -la /dev/video*

# Test camera functionality
cheese  # or guvcview

# Test Python imports
python3 -c "
import cv2, mediapipe, pyautogui, numpy, PIL, psutil, pynput, screeninfo, tkinter
print('✅ All modules imported successfully!')
"

# Run system tests
python3 test_system.py
```

## Troubleshooting

### Common Issues on Fedora:

#### 1. "No module named 'pip'"
```bash
sudo dnf install python3-pip
```

#### 2. "No module named 'tkinter'"
```bash
sudo dnf install python3-tkinter
```

#### 3. Camera permission denied
```bash
# Add user to video group
sudo usermod -a -G video $USER

# Log out and log back in, or restart
```

#### 4. OpenCV installation fails
```bash
# Install system OpenCV first
sudo dnf install python3-opencv opencv-devel

# Then try pip installation
python3 -m pip install --user opencv-python
```

#### 5. MediaPipe installation fails
```bash
# Install dependencies first
sudo dnf install gcc gcc-c++ cmake

# Try installing without version constraint
python3 -m pip install --user mediapipe
```

#### 6. PyAutoGUI doesn't work
```bash
# Install X11 dependencies
sudo dnf install python3-xlib

# For Wayland users, you might need additional setup
export XDG_SESSION_TYPE=x11
```

### Performance Issues:

#### 1. Low FPS or high CPU usage
- Close unnecessary applications
- Use the "Low" quality preset in settings
- Ensure good lighting for better tracking

#### 2. Camera not detected
```bash
# Check camera devices
ls /dev/video*

# Test camera
v4l2-ctl --list-devices

# Install camera tools
sudo dnf install v4l-utils cheese
```

## Running the Application

After successful installation:

```bash
# Test the system
python3 test_system.py

# Run the simple version
python3 simple_eye_mouse.py

# Run the full application
python3 main.py

# Or use the launcher
python3 launch.py
```

## Post-Installation Notes

1. **Restart Required**: After installation, log out and log back in (or restart) to ensure video group permissions take effect.

2. **Camera Testing**: Test your camera with `cheese` or `guvcview` before running the eye tracking application.

3. **Lighting**: Ensure good lighting on your face for optimal eye tracking performance.

4. **Performance**: The application will automatically adjust quality based on your system performance.

## System Requirements

- **OS**: Fedora Linux (tested on Fedora 42)
- **Python**: 3.6+ (3.11+ recommended)
- **RAM**: 4GB+ recommended
- **CPU**: 2+ cores recommended
- **Camera**: Any USB webcam or built-in camera
- **Display**: Any resolution (multi-monitor supported)

## Security Notes

- The application processes all data locally
- No data is sent to external servers
- Camera access is only used for real-time processing
- All settings and calibration data are stored locally

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Run `python3 test_system.py` for detailed diagnostics
3. Check the log files in the project directory
4. Ensure your camera works with other applications first

## Fedora-Specific Notes

- Fedora uses `dnf` package manager instead of `apt`
- Some Python packages are available as system packages (`python3-*`)
- SELinux might affect camera permissions (usually not an issue)
- Wayland vs X11 considerations for PyAutoGUI
